"""Entry point, arena, and mission flow for Drone Simulation Phase 4."""

from ursina import Entity, Sky, Ursina, Vec3, application, color, window

import config
from drone import Drone
from hud import FlightHUD
from target import TrainingTarget


app = Ursina(title=config.WINDOW_TITLE, borderless=False)
window.size = config.WINDOW_SIZE
window.color = color.rgb32(120, 180, 220)


def create_tree(position: tuple[float, float, float], scale: float = 1.0) -> None:
    """Create a stylized evergreen with a collidable trunk."""
    x, y, z = position
    Entity(model="cube", color=color.rgb32(92, 62, 38), position=(x, y + 1.2 * scale, z),
           scale=(.38 * scale, 2.4 * scale, .38 * scale), collider="box")
    for height, width in ((2.0, 2.3), (2.8, 1.8), (3.5, 1.25)):
        Entity(model="diamond", color=color.rgb32(38, 105, 54),
               position=(x, y + height * scale, z),
               scale=(width * scale, 1.5 * scale, width * scale))


def create_hangar(position: tuple[float, float, float], size, accent) -> None:
    """Create an industrial hangar with a recessed dark doorway."""
    x, y, z = position
    width, height, depth = size
    Entity(model="cube", color=color.rgb32(118, 130, 138), position=position,
           scale=size, collider="box")
    Entity(model="cube", color=color.rgb32(47, 54, 59),
           position=(x, y - .15, z - depth / 2 - .03),
           scale=(width * .62, height * .7, .08))
    Entity(model="cube", color=accent, position=(x, y + height / 2 + .08, z),
           scale=(width + .35, .18, depth + .35))
    for offset in (-width * .32, 0, width * .32):
        Entity(model="cube", color=color.rgb32(185, 205, 214),
               position=(x + offset, y + height * .25, z - depth / 2 - .08),
               scale=(width * .15, .35, .05))


def create_outdoor_range() -> None:
    """Build a detailed outdoor drone-training airfield from primitives."""
    arena = config.ARENA_SIZE
    Entity(name="ground", model="plane", texture="white_cube", texture_scale=(24, 24),
           scale=arena, color=color.rgb32(72, 122, 66), collider="box")

    # A paved service road, runway, shoulder markings, and central taxiway.
    asphalt = color.rgb32(54, 60, 64)
    Entity(model="cube", color=asphalt, position=(25, .035, 0), scale=(16, .035, 88))
    Entity(model="cube", color=asphalt, position=(0, .04, -20), scale=(52, .04, 8))
    for z in range(-42, 45, 8):
        Entity(model="cube", color=color.rgba32(245, 235, 185, 210),
               position=(25, .07, z), scale=(.22, .025, 3.2))
    for x in range(-22, 24, 5):
        Entity(model="cube", color=color.rgba32(245, 210, 60, 220),
               position=(x, .075, -20), scale=(2.4, .025, .12))

    # Two distinct training compounds create depth and navigation landmarks.
    create_hangar((-27, 3, -3), (13, 6, 12), color.rgb32(35, 140, 185))
    create_hangar((10, 2.5, 28), (12, 5, 9), color.rgb32(220, 145, 45))
    create_hangar((36, 2.2, 22), (9, 4.4, 11), color.rgb32(75, 165, 100))

    # Control tower with wraparound blue observation windows and roof antenna.
    Entity(model="cube", color=color.rgb32(185, 187, 180), position=(-38, 4.5, 25),
           scale=(5, 9, 5), collider="box")
    Entity(model="cube", color=color.rgb32(45, 105, 135), position=(-38, 9.5, 25),
           scale=(7, 2.1, 7), collider="box")
    Entity(model="cube", color=color.rgb32(43, 48, 52), position=(-38, 10.7, 25),
           scale=(7.5, .25, 7.5))
    Entity(model="cube", color=color.rgb32(210, 75, 55), position=(-38, 12.2, 25),
           scale=(.12, 3, .12))

    # Cargo stacks and safety barriers make the low-altitude course readable.
    container_colors = (color.rgb32(190, 68, 52), color.rgb32(42, 105, 150),
                        color.rgb32(205, 145, 40))
    for index, (x, z) in enumerate(((-19, 16), (-13, 16), (-16, 21), (15, -3))):
        Entity(model="cube", color=container_colors[index % 3],
               position=(x, 1.25, z), scale=(5.2, 2.5, 2.4), collider="box")
        for stripe in (-1.8, -.6, .6, 1.8):
            Entity(model="cube", color=color.rgba32(235, 235, 225, 90),
                   position=(x + stripe, 1.25, z - 1.23), scale=(.07, 2.1, .03))

    # Trees frame the play area while keeping the mission route unobstructed.
    tree_positions = (
        (-44, 0, -36), (-35, 0, -38), (-24, 0, -40), (-12, 0, -42),
        (40, 0, -35), (43, 0, -22), (44, 0, -8), (43, 0, 8),
        (-45, 0, 5), (-44, 0, 15), (-30, 0, 40), (-18, 0, 43),
        (18, 0, 43), (31, 0, 40), (43, 0, 36),
    )
    for index, tree_position in enumerate(tree_positions):
        create_tree(tree_position, .8 + (index % 3) * .14)

    # Distant low-poly hills hide the invisible safety boundary.
    for x, z, height, width in (
        (-45, 47, 18, 24), (-20, 49, 13, 22), (8, 50, 17, 27),
        (35, 48, 14, 22), (-49, -20, 11, 18), (49, 8, 13, 20),
    ):
        Entity(model="diamond", color=color.rgb32(72, 96, 70),
               position=(x, height * .33, z), scale=(width, height, width))

    # Boundary posts imply fencing; transparent colliders enforce the geofence.
    fence_color = color.rgb32(150, 158, 158)
    for offset in range(-48, 49, 6):
        for x, z in ((offset, -49), (offset, 49), (-49, offset), (49, offset)):
            Entity(model="cube", color=fence_color, position=(x, 1.25, z),
                   scale=(.10, 2.5, .10))
    for position, scale in (
        ((0, 2, 50), (100, 4, .4)), ((0, 2, -50), (100, 4, .4)),
        ((50, 2, 0), (.4, 4, 100)), ((-50, 2, 0), (.4, 4, 100)),
    ):
        Entity(model="cube", color=color.rgba32(0, 0, 0, 0),
               position=position, scale=scale, collider="box")

    # Layered clouds and a warm horizon give the sky visual depth without shaders.
    for x, y, z, cloud_scale in (
        (-30, 24, 18, 4), (15, 28, 38, 5), (38, 22, -18, 3.6), (-42, 27, -20, 4.5),
    ):
        for dx, dy, size in ((-1.6, 0, 1.5), (0, .45, 2.0), (1.8, 0, 1.4)):
            Entity(model="sphere", color=color.rgba32(245, 248, 250, 205),
                   position=(x + dx * cloud_scale / 3, y + dy, z),
                   scale=(size * cloud_scale, cloud_scale * .55, cloud_scale * .7))

    # Landing pad and beacon lights remain the mission's visual anchor.
    Entity(name="landing_pad", model="cube", color=color.rgb32(38, 43, 47),
           position=(0, .11, -20), scale=(8, .18, 8), collider="box")
    Entity(model="circle", color=color.rgb32(235, 202, 40), position=(0, .22, -20),
           rotation_x=90, scale=5.8, double_sided=True)
    Entity(model="cube", color=color.rgb32(38, 43, 47), position=(0, .24, -20),
           scale=(2.8, .04, .42))
    Entity(model="cube", color=color.rgb32(38, 43, 47), position=(0, .24, -20),
           scale=(.42, .04, 2.8))
    for x, z in ((-3.4, -23.4), (3.4, -23.4), (-3.4, -16.6), (3.4, -16.6)):
        Entity(model="sphere", color=color.lime, position=(x, .32, z), scale=.18)

    Sky(color=color.rgb32(105, 175, 225))


create_outdoor_range()
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
