# RAM CPU Widget

A lightweight Linux desktop widget that shows live RAM and CPU usage with compact right-to-left sparklines.

This project is intentionally minimal:

- Python standard library only (`tkinter`, `argparse`, file reads from `/proc` and `/sys`)
- low memory footprint
- no heavy UI frameworks
- no background services

## Features

- live RAM usage percentage
- live CPU usage percentage
- optional CPU temperature readout (when thermal zones expose CPU data)
- optional zram usage summary
- draggable always-on-top window
- right-to-left timeline graph (newest values at the right edge)

## Resource usage

Measured on Ubuntu GNOME (`240x88`, `1000ms` refresh), real values from `/proc/*/smaps_rollup`.

### Python (`ram_widget.py`)

- RSS: ~`19-26 MiB` (includes shared libraries)
- PSS: ~`13 MiB`
- Private memory: ~`12-13 MiB`

### Conky (`conky/ram-cpu-widget.conkyrc`)

- RSS: ~`25-26 MiB` (includes shared libraries)
- PSS: ~`9-10 MiB`
- Private memory: ~`8-9 MiB`

Conky is usually lighter in practical per-process impact (`PSS`/`Private`) even when `RSS` appears similar or higher.
Actual usage varies by compositor, fonts, session type, and update interval.

## Requirements

- Linux
- Python 3.8+
- `tkinter` package available in your Python install

## Run

```bash
python3 ram_widget.py
```

## CLI options

```bash
python3 ram_widget.py --interval-ms 1000 --width 240 --height 88 --history 90
```

Available flags:

- `--interval-ms`: refresh interval in milliseconds (minimum enforced at 250)
- `--width`: widget width in pixels
- `--height`: widget height in pixels
- `--history`: number of historical samples retained
- `--once`: print one snapshot to terminal and exit

Example:

```bash
python3 ram_widget.py --once
```

## Autostart (GNOME and other desktop environments)

You can copy the desktop entry template:

```bash
mkdir -p ~/.config/autostart
cp packaging/ram-widget.desktop ~/.config/autostart/ram-widget.desktop
```

Then update the `Exec=` line in the copied file to your local project path.

## Conky low-RAM mock theme

If you want a much lower RAM baseline, this repo includes a Conky mock theme with a similar visual style:

- config: `conky/ram-cpu-widget.conkyrc`
- launcher: `scripts/run-conky-mock.sh`
- stopper: `scripts/stop-conky-mock.sh`

Run:

```bash
bash scripts/run-conky-mock.sh
```

Stop:

```bash
bash scripts/stop-conky-mock.sh
```

Notes:

- Conky is not bundled and may need installation (`sudo apt install conky-all`).
- The Conky version is designed as a lightweight alternative and may not be pixel-identical to the Tk widget.
- On GNOME, move the Conky window with your window-manager shortcut (commonly `Super` + drag or `Alt` + drag).

## Project structure

```text
ram-cpu-widget/
├── ram_widget.py
├── conky/
│   └── ram-cpu-widget.conkyrc
├── packaging/
│   └── ram-widget.desktop
├── scripts/
│   ├── conky-ram-pct.sh
│   ├── conky-temp.sh
│   ├── conky-zram.sh
│   ├── stop-conky-mock.sh
│   ├── run-conky-mock.sh
│   └── install-autostart.sh
├── LICENSE
├── README.md
└── .gitignore
```

## Notes

- This widget is Linux-specific due to `/proc` and `/sys` usage.
- On some systems, CPU temperature may report `n/a` if no matching thermal zone exists.

## License

MIT License. See `LICENSE`.
