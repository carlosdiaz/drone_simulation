# Drone Simulation — Phase 2

A deliberately small, fictional 3D drone-training game built with Python and
Ursina. Phase 2 is a flight and camera lesson: take off from the yellow landing
pad, practice flying around the buildings in both camera views, then return and
land. It includes collision detection, stabilized arcade flight, battery use,
hover control, first- and third-person cameras, a crosshair, and live telemetry.

## Requirements

- Python 3.11 or newer
- A desktop with OpenGL support

## Install and run

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windows PowerShell activation:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| Up / Down arrow | Move forward / backward |
| Left / Right arrow | Turn left / right |
| Space / Left Shift | Ascend / descend |
| C | Switch first/third-person camera |
| H | Toggle automatic hover |
| R | Reset the drone |
| Escape | Exit |

## Platform notes

Ursina opens a native Panda3D window, so this application needs a graphical
desktop session and working OpenGL drivers. Keyboard naming can differ on some
non-US layouts. The first launch can take a moment while Ursina initializes.

This repository intentionally stops at Phase 2. Targets, projectiles, and
mission progression belong to later requested phases.
