#!/usr/bin/env python3
"""Lightweight live RAM/CPU widget for Linux.

Reads system counters from /proc and /sys with zero third-party dependencies.
"""

import argparse
import glob
import time
import tkinter as tk


def read_meminfo():
    meminfo = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as handle:
        for line in handle:
            key, value = line.split(":", 1)
            meminfo[key] = int(value.strip().split()[0])  # kB
    return meminfo


def get_ram_usage_percent():
    meminfo = read_meminfo()
    total = meminfo.get("MemTotal", 1)
    available = meminfo.get("MemAvailable", 0)
    used = max(total - available, 0)
    return (used / total) * 100.0


def read_cpu_counters():
    try:
        with open("/proc/stat", "r", encoding="utf-8") as handle:
            first = handle.readline().strip().split()
    except OSError:
        return None

    if len(first) < 8 or first[0] != "cpu":
        return None

    nums = [int(x) for x in first[1:]]
    total = sum(nums)
    idle = nums[3] + (nums[4] if len(nums) > 4 else 0)  # idle + iowait
    return total, idle


def get_cpu_temp_c():
    best = None
    try:
        for zone in glob.glob("/sys/class/thermal/thermal_zone*"):
            try:
                with open(f"{zone}/type", "r", encoding="utf-8") as t_handle:
                    zone_type = t_handle.read().strip().lower()
                with open(f"{zone}/temp", "r", encoding="utf-8") as temp_handle:
                    raw = int(temp_handle.read().strip())
            except (OSError, ValueError):
                continue

            if raw <= 0:
                continue
            temp_c = raw / 1000.0
            if "x86_pkg_temp" in zone_type:
                return temp_c
            if "cpu" in zone_type or "pkg" in zone_type:
                best = temp_c if best is None else max(best, temp_c)
    except OSError:
        return None
    return best


def read_swap_devices():
    devices = []
    try:
        with open("/proc/swaps", "r", encoding="utf-8") as handle:
            next(handle, None)
            for line in handle:
                parts = line.split()
                if len(parts) < 5:
                    continue
                name, swap_type, size_kb, used_kb, priority = parts[:5]
                devices.append(
                    {
                        "name": name,
                        "type": swap_type,
                        "size_kb": int(size_kb),
                        "used_kb": int(used_kb),
                        "priority": int(priority),
                    }
                )
    except OSError:
        pass
    return devices


def get_zram_stats():
    devices = read_swap_devices()
    zram = [dev for dev in devices if "/zram" in dev["name"]]
    if not zram:
        return None
    total_size = sum(dev["size_kb"] for dev in zram)
    total_used = sum(dev["used_kb"] for dev in zram)
    pct = (total_used / total_size) * 100.0 if total_size else 0.0
    return total_used, total_size, pct


def kb_to_gib(kb):
    return kb / (1024 * 1024)


class RamWidget:
    def __init__(self, width=240, height=88, interval_ms=1000, history=90):
        self.width = width
        self.height = height
        self.interval_ms = interval_ms
        self.history = history
        self.ram_points = []
        self.cpu_points = []
        self.prev_cpu = read_cpu_counters()

        self.root = tk.Tk()
        self.root.title("System Widget")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.configure(bg="#111111")
        self.root.overrideredirect(False)

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)

        self._place_initial_position()
        self.update_loop()

    def _place_initial_position(self):
        self.root.update_idletasks()
        self.root.geometry(f"{self.width}x{self.height}+24+52")

    def _on_drag_start(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def _on_drag_motion(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def _draw_panel(self, y0, y1, title, value_text, color):
        self.canvas.create_rectangle(
            10,
            y0,
            self.width - 10,
            y1,
            outline="#343434",
            width=1,
            fill="#171717",
        )
        self.canvas.create_text(
            18,
            y0 + 12,
            anchor="w",
            fill="#f6f6f6",
            font=("Sans", 9, "bold"),
            text=title,
        )
        self.canvas.create_text(
            self.width - 18,
            y0 + 12,
            anchor="e",
            fill=color,
            font=("Sans", 9, "bold"),
            text=value_text,
        )

        graph_top = y0 + 22
        graph_bottom = y1 - 6
        for pct in (33, 66):
            y = graph_bottom - int((pct / 100.0) * (graph_bottom - graph_top))
            self.canvas.create_line(14, y, self.width - 14, y, fill="#2a2a2a")
        return 14, graph_top, self.width - 14, graph_bottom

    def _series_to_xy(self, points, rect, x_step=2):
        graph_left, graph_top, graph_right, graph_bottom = rect
        graph_h = max(graph_bottom - graph_top, 1)
        max_points = max((graph_right - graph_left) // x_step + 1, 2)
        visible = points[-max_points:]
        if len(visible) < 2:
            return None

        # Newest sample stays on the right, older history extends left.
        start_x = graph_right - ((len(visible) - 1) * x_step)
        xy = []
        for idx, pct in enumerate(visible):
            x = start_x + (idx * x_step)
            y = graph_bottom - int((max(0.0, min(100.0, pct)) / 100.0) * graph_h)
            xy.extend((x, y))
        return xy

    def _draw_spark_series(self, points, rect, color):
        xy = self._series_to_xy(points, rect)
        if xy is None:
            return

        shadow = []
        for idx, value in enumerate(xy):
            shadow.append(value + 1 if idx % 2 == 1 else value)
        self.canvas.create_line(*shadow, fill="#101010", width=3, smooth=True, splinesteps=8)
        self.canvas.create_line(*xy, fill=color, width=2, smooth=True, splinesteps=8)

        x_last = xy[-2]
        y_last = xy[-1]
        self.canvas.create_oval(
            x_last - 2,
            y_last - 2,
            x_last + 2,
            y_last + 2,
            fill=color,
            outline=color,
        )

    def _next_cpu_usage(self):
        now = read_cpu_counters()
        if now is None or self.prev_cpu is None:
            self.prev_cpu = now
            return 0.0

        total_now, idle_now = now
        total_prev, idle_prev = self.prev_cpu
        total_delta = max(total_now - total_prev, 1)
        idle_delta = max(idle_now - idle_prev, 0)
        self.prev_cpu = now
        busy = max(total_delta - idle_delta, 0)
        return (busy / total_delta) * 100.0

    def update_loop(self):
        ram_pct = get_ram_usage_percent()
        cpu_pct = self._next_cpu_usage()
        cpu_temp = get_cpu_temp_c()

        self.ram_points.append(ram_pct)
        self.cpu_points.append(cpu_pct)
        if len(self.ram_points) > self.history:
            self.ram_points.pop(0)
        if len(self.cpu_points) > self.history:
            self.cpu_points.pop(0)

        zram_stats = get_zram_stats()
        self.canvas.delete("all")
        if zram_stats is None:
            ztxt = "zram: n/a"
        else:
            _, _, z_pct = zram_stats
            ztxt = f"zram {z_pct:4.1f}%"

        if cpu_temp is None:
            ttxt = "temp n/a"
        else:
            ttxt = f"temp {cpu_temp:.0f}C"

        self.canvas.create_text(
            12,
            10,
            anchor="w",
            fill="#bdbdbd",
            font=("Sans", 8),
            text=f"{ztxt}  |  {ttxt}  |  {self.interval_ms}ms",
        )

        ram_rect = self._draw_panel(14, 48, "RAM", f"{ram_pct:5.1f}%", "#77e67d")
        self._draw_spark_series(self.ram_points, ram_rect, "#77e67d")

        cpu_rect = self._draw_panel(50, self.height - 8, "CPU", f"{cpu_pct:5.1f}%", "#83cfff")
        self._draw_spark_series(self.cpu_points, cpu_rect, "#83cfff")

        self.canvas.create_text(
            self.width - 10,
            self.height - 2,
            anchor="e",
            fill="#7f7f7f",
            font=("Sans", 7),
            text="drag",
        )
        self.root.after(self.interval_ms, self.update_loop)

    def run(self):
        self.root.mainloop()


def run_once_snapshot():
    ram_pct = get_ram_usage_percent()
    cpu_now = read_cpu_counters()
    cpu_temp = get_cpu_temp_c()
    cpu_pct = 0.0
    if cpu_now is not None:
        time.sleep(0.2)
        cpu_after = read_cpu_counters()
        if cpu_after is not None:
            total_delta = max(cpu_after[0] - cpu_now[0], 1)
            idle_delta = max(cpu_after[1] - cpu_now[1], 0)
            cpu_pct = max((total_delta - idle_delta) / total_delta * 100.0, 0.0)

    zram = get_zram_stats()
    if cpu_temp is None:
        ttxt = "n/a"
    else:
        ttxt = f"{cpu_temp:.1f}C"

    if zram is None:
        print(f"RAM: {ram_pct:.1f}% | CPU: {cpu_pct:.1f}% | TEMP: {ttxt} | ZRAM: not active")
        return

    used_kb, total_kb, pct = zram
    print(
        f"RAM: {ram_pct:.1f}% | CPU: {cpu_pct:.1f}% | TEMP: {ttxt} | "
        f"ZRAM: {kb_to_gib(used_kb):.2f}/{kb_to_gib(total_kb):.2f} GiB ({pct:.1f}%)"
    )


def main():
    parser = argparse.ArgumentParser(description="Lightweight live RAM + CPU + ZRAM widget")
    parser.add_argument("--interval-ms", type=int, default=1000, help="Update interval in milliseconds")
    parser.add_argument("--width", type=int, default=240, help="Widget width")
    parser.add_argument("--height", type=int, default=88, help="Widget height")
    parser.add_argument("--history", type=int, default=90, help="Data points in graph history")
    parser.add_argument("--once", action="store_true", help="Print one snapshot and exit")
    args = parser.parse_args()

    if args.once:
        run_once_snapshot()
        return

    widget = RamWidget(
        width=args.width,
        height=args.height,
        interval_ms=max(args.interval_ms, 250),
        history=max(args.history, 30),
    )
    widget.run()


if __name__ == "__main__":
    main()
