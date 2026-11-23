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

Measured on Ubuntu GNOME with default widget settings (`240x88`, `1000ms` refresh):

- memory: ~`25.4 MiB` RSS (about `26,000 KB`)
- CPU: typically around `1%` in this test environment

Actual usage can vary with desktop session, compositor, fonts, and refresh interval.

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

Run:

```bash
bash scripts/run-conky-mock.sh
```

Notes:

- Conky is not bundled and may need installation (`sudo apt install conky-all`).
- The Conky version is designed as a lightweight alternative and may not be pixel-identical to the Tk widget.

## Project structure

```text
ram-cpu-widget/
├── ram_widget.py
├── conky/
│   └── ram-cpu-widget.conkyrc
├── packaging/
│   └── ram-widget.desktop
├── scripts/
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
