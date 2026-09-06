"""On-screen controls, mission progress, and telemetry for Phase 4."""

from ursina import Text, color


class FlightHUD:
    """Explain the free-flight objective and show basic movement feedback."""

    def __init__(self) -> None:
        self.instructions = Text(
            text=("PHASE 4: TRAINING MISSION\n"
                  "Take off > pass 3 cyan gates\n"
                  "Disable 5 targets > return > land\n\n"
                  "Up/Down arrows: forward/back\n"
                  "Left/Right arrows: turn camera\n"
                  "A/D: strafe   Q/E: also turn\n"
                  "Space/Shift: up/down   F: fire\n"
                  "C camera   H hover   P pause\n"
                  "M mission/manual   R restart"),
            origin=(-.5, .5),
            position=(-.87, .47),
            scale=.78,
            color=color.white,
            background=True,
        )
        self.crosshair = Text(
            text="+",
            origin=(0, 0),
            position=(0, 0),
            scale=2,
            color=color.lime,
            enabled=False,
        )
        self.status = Text(
            text="",
            origin=(0, 0),
            position=(0, -.42),
            scale=1.15,
            color=color.yellow,
            background=True,
        )
        self.objective = Text(
            text="",
            origin=(0, 0),
            position=(0, .43),
            scale=1.02,
            color=color.yellow,
            background=True,
        )
        self.telemetry = Text(
            text="",
            origin=(.5, .5),
            position=(.87, .47),
            scale=1.05,
            color=color.azure,
            background=True,
        )

    def update(self, drone, score: int, active_targets: int, mission, paused: bool) -> None:
        """Refresh the small telemetry readout."""
        horizontal_speed = (drone.velocity.x ** 2 + drone.velocity.z ** 2) ** .5
        target_distance = drone.aimed_target_distance()
        target_text = f"{target_distance:4.1f} m" if target_distance is not None else "---"
        self.telemetry.text = (
            f"ALTITUDE  {drone.y:4.1f} m\n"
            f"SPEED     {horizontal_speed:4.1f} m/s\n"
            f"BATTERY   {drone.battery:4.1f}%\n"
            f"HEALTH    {drone.health:4.0f}%\n"
            f"SCORE     {score:4d}\n"
            f"TARGETS   {active_targets}\n"
            f"AIM RANGE {target_text}\n"
            f"HOVER     {'ON' if drone.hover_enabled else 'OFF'}\n"
            f"CAMERA    {drone.camera_mode}"
        )
        self.telemetry.color = color.red if drone.battery < 20 else color.azure
        self.crosshair.enabled = drone.camera_mode == "FIRST PERSON"
        self.status.text = drone.status
        self.status.color = color.red if drone.crashed else color.yellow
        mode = "MANUAL" if mission.manual_mode else "MISSION"
        pause_text = "  [PAUSED]" if paused else ""
        self.objective.text = f"{mode}{pause_text} | {mission.progress}\n{mission.objective}"
        self.objective.color = color.lime if mission.complete else color.yellow
