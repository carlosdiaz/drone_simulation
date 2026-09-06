"""Entry point, arena, and mission flow for Drone Simulation Phase 4."""

from ursina import Entity, Sky, Ursina, Vec3, application, color, window

import config
from drone import Drone
from hud import FlightHUD
from target import TrainingTarget


app = Ursina(title=config.WINDOW_TITLE, borderless=False)
window.size = config.WINDOW_SIZE
window.color = color.rgb32(120, 180, 220)


def create_arena() -> None:
    """Build a compact arena entirely from Ursina primitives."""
    arena = config.ARENA_SIZE
    Entity(name="ground", model="plane", texture="white_cube", texture_scale=(arena, arena),
           scale=arena, color=color.rgb32(80, 135, 70), collider="box")
    # High-contrast strips make horizontal motion visible from the chase camera.
    for offset in range(-30, 31, 10):
        Entity(model="cube", color=color.rgba32(220, 220, 190, 120),
               position=(offset, .025, 0), scale=(.08, .025, 68))
        Entity(model="cube", color=color.rgba32(220, 220, 190, 120),
               position=(0, .026, offset), scale=(68, .025, .08))
    wall_color = color.rgb32(105, 110, 120)
    for position, scale in (
        ((0, 2, arena / 2), (arena, 4, 1)),
        ((0, 2, -arena / 2), (arena, 4, 1)),
        ((arena / 2, 2, 0), (1, 4, arena)),
        ((-arena / 2, 2, 0), (1, 4, arena)),
    ):
        Entity(model="cube", color=wall_color, position=position, scale=scale, collider="box")

    for position, scale, building_color in (
        ((-15, 2, 2), (7, 4, 7), color.rgb32(150, 130, 105)),
        ((12, 3, 8), (9, 6, 6), color.rgb32(125, 140, 155)),
        ((0, 1.5, 20), (6, 3, 8), color.rgb32(165, 145, 115)),
        ((20, 2, -10), (5, 4, 10), color.rgb32(115, 130, 145)),
    ):
        Entity(model="cube", color=building_color, position=position,
               scale=scale, collider="box")

    Entity(name="landing_pad", model="cube", color=color.rgb32(45, 45, 50),
           position=(0, .08, -20), scale=(7, .12, 7), collider="box")
    Entity(model="cube", color=color.yellow, position=(0, .16, -20),
           scale=(3.2, .03, .45))
    Entity(model="cube", color=color.yellow, position=(0, .16, -20),
           scale=(.45, .03, 3.2))

    Sky(color=color.rgb32(120, 185, 235))


create_arena()
drone = Drone()
hud = FlightHUD()
score = 0
paused = False


class Checkpoint(Entity):
    """A simple visible training gate made from built-in geometry."""

    def __init__(self, position: Vec3, number: int) -> None:
        super().__init__(position=position)
        self.number = number
        gate_color = color.rgba32(60, 220, 255, 210)
        self.parts = [
            Entity(parent=self, model="cube", color=gate_color,
                   position=(-2.5, 0, 0), scale=(.25, 5, .25)),
            Entity(parent=self, model="cube", color=gate_color,
                   position=(2.5, 0, 0), scale=(.25, 5, .25)),
            Entity(parent=self, model="cube", color=gate_color,
                   position=(0, 2.5, 0), scale=(5.25, .25, .25)),
            Entity(parent=self, model="cube", color=gate_color,
                   position=(0, -2.5, 0), scale=(5.25, .25, .25)),
        ]

    def complete(self) -> None:
        """Mark the gate as passed without removing its visual reference."""
        for part in self.parts:
            part.color = color.rgba32(70, 255, 110, 120)
        self.scale = .72


checkpoints = [
    Checkpoint(Vec3(*position), number)
    for number, position in enumerate(config.CHECKPOINT_POSITIONS, start=1)
]


class TrainingMission:
    """Track the small five-step mission or unrestricted manual operation."""

    objectives = (
        "Take off above the landing pad",
        "Fly through the three cyan gates",
        "Disable all five robot targets",
        "Return to the yellow landing pad",
        "Land gently on the pad",
    )

    def __init__(self) -> None:
        self.manual_mode = False
        self.step = 0
        self.checkpoint_index = 0
        self.destroyed_target_ids: set[int] = set()
        self.complete = False

    @property
    def objective(self) -> str:
        if self.manual_mode:
            return "Manual operation — unrestricted free flight"
        if self.complete:
            return "Mission complete — press R to restart"
        return self.objectives[self.step]

    @property
    def progress(self) -> str:
        if self.manual_mode:
            return "MANUAL"
        if self.step == 1:
            return f"GATES {self.checkpoint_index}/3"
        if self.step == 2:
            return f"TARGETS {len(self.destroyed_target_ids)}/{config.MISSION_TARGET_GOAL}"
        return f"OBJECTIVE {min(self.step + 1, 5)}/5"

    def update(self) -> None:
        if self.manual_mode or self.complete or drone.crashed:
            return
        if self.step == 0 and drone.y >= config.TAKEOFF_ALTITUDE:
            self.step = 1
            drone.status = "TAKEOFF COMPLETE — FIND GATE 1"
        elif self.step == 1:
            gate = checkpoints[self.checkpoint_index]
            if (drone.world_position - gate.world_position).length() <= config.CHECKPOINT_RADIUS:
                gate.complete()
                self.checkpoint_index += 1
                if self.checkpoint_index == len(checkpoints):
                    self.step = 2
                    drone.status = "ALL GATES COMPLETE — DISABLE FIVE TARGETS"
                else:
                    drone.status = f"GATE {self.checkpoint_index} COMPLETE"
        elif self.step == 2 and len(self.destroyed_target_ids) >= config.MISSION_TARGET_GOAL:
            self.step = 3
            drone.status = "TARGET OBJECTIVE COMPLETE — RETURN TO BASE"
        elif self.step == 3 and self._over_pad() and drone.y <= 2.2:
            self.step = 4
            drone.status = "BASE REACHED — LAND GENTLY"
        elif self.step == 4 and self._safe_landing():
            self.complete = True
            drone.status = "MISSION COMPLETE — EXCELLENT FLIGHT"

    def record_target(self, target_id: int) -> None:
        if not self.manual_mode and self.step == 2:
            self.destroyed_target_ids.add(target_id)

    def toggle_mode(self) -> None:
        self.manual_mode = not self.manual_mode
        mode = "MANUAL OPERATION" if self.manual_mode else "MISSION MODE"
        drone.status = f"{mode} ENABLED"

    def reset(self) -> None:
        self.step = 0
        self.checkpoint_index = 0
        self.destroyed_target_ids.clear()
        self.complete = False
        for gate in checkpoints:
            gate.scale = 1
            for part in gate.parts:
                part.color = color.rgba32(60, 220, 255, 210)

    @staticmethod
    def _over_pad() -> bool:
        pad_x, pad_z = config.LANDING_PAD_CENTER
        return (abs(drone.x - pad_x) <= config.LANDING_PAD_HALF_SIZE
                and abs(drone.z - pad_z) <= config.LANDING_PAD_HALF_SIZE)

    def _safe_landing(self) -> bool:
        return self._over_pad() and drone.is_grounded and not drone.crashed


mission = TrainingMission()


def target_destroyed(target: TrainingTarget) -> None:
    """Award points when a fictional training target is disabled."""
    global score
    score += 100
    mission.record_target(target.target_id)
    drone.status = f"TARGET {target.target_id} DISABLED — +100"


target_positions = (
    Vec3(-18, 4, -4),
    Vec3(16, 6, 2),
    Vec3(-8, 3, 18),
    Vec3(22, 5, 18),
    Vec3(0, 8, 28),
)
targets = [
    TrainingTarget(position, index, target_destroyed)
    for index, position in enumerate(target_positions, start=1)
]


def update() -> None:
    """Advance player flight and the chase camera once per frame."""
    if paused:
        drone.update_camera()
        hud.update(drone, score, sum(target.is_active for target in targets), mission, paused)
        return
    drone.update_flight()
    drone.update_camera()
    mission.update()
    active_targets = sum(target.is_active for target in targets)
    hud.update(drone, score, active_targets, mission, paused)


def input(key: str) -> None:
    """Handle one-shot global controls."""
    drone.handle_key(key)
    global score, paused
    if key == "r":
        drone.reset()
        mission.reset()
        score = 0
        paused = False
        application.time_scale = 1
        for target in targets:
            target.respawn()
    elif key == "c":
        drone.switch_camera()
    elif key == "h":
        drone.toggle_hover()
    elif key == "f":
        drone.fire()
    elif key == "m":
        mission.toggle_mode()
    elif key == "p":
        paused = not paused
        application.time_scale = 0 if paused else 1
        drone.pressed_keys.clear()
        drone.status = "SIMULATION PAUSED" if paused else "SIMULATION RESUMED"
    elif key == "escape":
        application.quit()


if __name__ == "__main__":
    app.run()
