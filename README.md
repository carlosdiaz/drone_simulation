# Drone Simulation — Phase 4

A deliberately small, fictional 3D drone-training game built with Python and
Ursina. Phase 4 connects the flight and fictional target systems into a complete
training mission: take off, pass three gates, disable five targets, return to
base, and land safely. Press `M` at any time to select unrestricted manual
operation instead. The drone uses smooth aerodynamic shells, a raised canopy,
nose-mounted camera gimbal, diagonal carbon arms, motor pods, translucent rotor
discs, navigation lights, and landing skids built entirely from Ursina
primitives. This remains fictional arcade behavior, not a model of a real
aircraft or weapon system.

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
| Left / Right arrow | Turn left / right with chase camera |
| A / D | Strafe left / right without turning |
| Q / E | Alternate rotate left / right |
| Space / Left Shift | Ascend / descend |
| C | Switch first/third-person camera |
| H | Toggle automatic hover |
| F | Fire a virtual training projectile |
| M | Toggle guided mission/manual operation |
| P | Pause/resume the simulation |
| R | Reset the drone |
| Escape | Exit |

## Platform notes

Ursina opens a native Panda3D window, so this application needs a graphical
desktop session and working OpenGL drivers. Keyboard naming can differ on some
non-US layouts. The first launch can take a moment while Ursina initializes.

## Crash and landing test

Fly into a wall or building at full speed to trigger a crash. For a landing
test, climb several meters, press `H` to disable hover, and descend onto the
yellow pad. Gentle pad contact is a safe landing; a fast impact causes damage.
After a crash, press `R` to restart.

## Target training

Orange floating robot targets are distributed around the arena. Aim the drone
at a target and press `F`. Each virtual hit removes 50 health, so two hits
disable a target and award 100 points. Disabled targets respawn after four
seconds. The HUD displays score, active target count, and distance when a target
is under the crosshair.

## Phase 4 mission

1. Ascend above 2.5 meters to complete takeoff.
2. Fly through the three cyan gates in sequence.
3. Disable each of the five fictional robot targets.
4. Return over the yellow landing pad.
5. Land gently without crashing.

The HUD shows the current objective and progress. Press `R` to restart the
mission and reset the score, targets, checkpoints, and drone. In manual mode,
all flight, camera, collision, crash, and target systems remain available, but
mission objectives do not advance.

Phase 4 completes the original prototype scope.

## Outdoor training range

The Phase 4 environment is a purpose-built outdoor airfield assembled entirely
from Ursina primitives. It includes paved service roads, runway markings,
multiple hangars, a control tower, cargo containers, trees, perimeter fencing,
distant hills, layered clouds, safety barriers, and an illuminated landing pad.
These visual additions require no external models or texture downloads.
