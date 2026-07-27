"""On-screen controls and telemetry for the Phase 2 prototype."""

from ursina import Text, color


class FlightHUD:
    """Explain the free-flight objective and show basic movement feedback."""

    def __init__(self) -> None:
        self.instructions = Text(
            text=("PHASE 2: FLIGHT & CAMERA TRAINING\n"
                  "1  Take off from the yellow pad\n"
                  "2  Fly around the buildings\n"
                  "3  Try both camera views\n"
                  "4  Return to the pad and land\n\n"
                  "Up/Down arrows: forward/back\n"
                  "Left/Right arrows: turn\n"
                  "Space/Shift: up/down\n"
                  "C camera   H hover   R reset"),
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
        self.telemetry = Text(
            text="",
            origin=(.5, .5),
            position=(.87, .47),
            scale=1.05,
            color=color.azure,
            background=True,
        )

    def update(self, drone) -> None:
        """Refresh the small telemetry readout."""
        horizontal_speed = (drone.velocity.x ** 2 + drone.velocity.z ** 2) ** .5
        self.telemetry.text = (
            f"ALTITUDE  {drone.y:4.1f} m\n"
            f"SPEED     {horizontal_speed:4.1f} m/s\n"
            f"BATTERY   {drone.battery:4.1f}%\n"
            f"HOVER     {'ON' if drone.hover_enabled else 'OFF'}\n"
            f"CAMERA    {drone.camera_mode}"
        )
        self.telemetry.color = color.red if drone.battery < 20 else color.azure
        self.crosshair.enabled = drone.camera_mode == "FIRST PERSON"
