"""Player-controlled drone and its simple arcade flight behavior."""

from __future__ import annotations

from ursina import Entity, Vec3, camera, color, raycast, time

import config


class Drone(Entity):
    """A compact drone entity with keyboard flight and a chase camera."""

    def __init__(self, spawn_position: Vec3 = Vec3(0, 1, -20)) -> None:
        super().__init__(
            model="cube",
            color=color.azure,
            scale=(1.6, 0.35, 1.2),
            position=spawn_position,
            collider="box",
        )
        self.spawn_position = Vec3(spawn_position)
        self.velocity = Vec3(0, 0, 0)
        self.forward_speed = 0.0
        self.battery = config.BATTERY_CAPACITY
        self.hover_enabled = True
        self.camera_mode = "THIRD PERSON"
        self.pressed_keys: set[str] = set()
        self.rotors: list[Entity] = []

        # A bright body, cockpit, arms, and flat rotor blades give a clear silhouette.
        Entity(parent=self, model="cube", color=color.dark_gray, scale=(1.6, .12, .12))
        Entity(parent=self, model="cube", color=color.dark_gray, scale=(.12, .12, 1.8))
        Entity(parent=self, model="cube", color=color.cyan,
               position=(0, .12, .48), scale=(.62, .3, .28))
        Entity(parent=self, model="cube", color=color.lime,
               position=(0, .03, .69), scale=(.18, .16, .08))
        Entity(parent=self, model="cube", color=color.red,
               position=(0, .03, -.69), scale=(.18, .16, .08))
        for x, z in ((-.7, -.75), (.7, -.75), (-.7, .75), (.7, .75)):
            hub = Entity(parent=self, position=(x, .22, z))
            Entity(parent=hub, model="cube", color=color.black, scale=(.12, .16, .12))
            Entity(parent=hub, model="cube", color=color.rgba(40, 40, 45, 210),
                   scale=(.9, .025, .10))
            Entity(parent=hub, model="cube", color=color.rgba(40, 40, 45, 210),
                   scale=(.10, .025, .9))
            self.rotors.append(hub)

        self.reset()

    def update_flight(self) -> None:
        """Read keyboard state and apply simplified acceleration and collision."""
        dt = time.dt
        is_down = self.pressed_keys.__contains__
        self.rotation_y += (is_down("right arrow") - is_down("left arrow")) * config.ROTATION_SPEED * dt

        move_axis = is_down("up arrow") - is_down("down arrow")
        # Movement exists only while an arrow is held. With no interpolation
        # there is no stored momentum to pull the drone sideways during a turn.
        self.forward_speed = move_axis * config.DRONE_SPEED if self.battery > 0 else 0.0

        # Horizontal velocity always follows the drone's nose. This deliberate
        # arcade behavior prevents unwanted sideways drift while steering.
        horizontal_velocity = self.forward * self.forward_speed
        self.velocity.x = horizontal_velocity.x
        self.velocity.z = horizontal_velocity.z

        vertical = is_down("space") - is_down("left shift")
        if self.battery <= 0:
            vertical = 0
        if vertical:
            self.velocity.y = vertical * config.VERTICAL_SPEED
        elif self.hover_enabled and self.battery > 0:
            self.velocity.y = 0
        else:
            self.velocity.y = max(-config.VERTICAL_SPEED,
                                  self.velocity.y - config.GRAVITY * dt)
        displacement = self.velocity * dt
        self._move_with_collisions(displacement)
        self.y = max(config.MIN_ALTITUDE, min(config.MAX_ALTITUDE, self.y))
        rotor_speed = 900 * dt if (abs(self.forward_speed) > .1 or vertical) else 250 * dt
        for rotor in self.rotors:
            rotor.rotation_y += rotor_speed
        activity = abs(self.forward_speed) / config.DRONE_SPEED + abs(vertical)
        drain = config.BATTERY_IDLE_DRAIN + config.BATTERY_FLIGHT_DRAIN * activity
        self.battery = max(0.0, self.battery - drain * dt)

    def handle_key(self, key: str) -> None:
        """Track key presses explicitly for consistent movement on macOS."""
        if key.endswith(" up"):
            self.pressed_keys.discard(key[:-3])
        elif key in {"up arrow", "down arrow", "left arrow", "right arrow",
                     "space", "left shift"}:
            self.pressed_keys.add(key)

    def toggle_hover(self) -> None:
        """Switch automatic altitude hold on or off."""
        self.hover_enabled = not self.hover_enabled
        if self.hover_enabled:
            self.velocity.y = 0

    def switch_camera(self) -> None:
        """Toggle between chase and nose-mounted views."""
        self.camera_mode = (
            "FIRST PERSON" if self.camera_mode == "THIRD PERSON" else "THIRD PERSON"
        )

    def _move_with_collisions(self, displacement: Vec3) -> None:
        """Move on each axis while preventing travel through arena obstacles."""
        for axis in ("x", "y", "z"):
            amount = getattr(displacement, axis)
            if abs(amount) < .0001:
                continue
            direction = Vec3(0, 0, 0)
            setattr(direction, axis, 1 if amount > 0 else -1)
            hit = raycast(self.world_position, direction, distance=abs(amount) + .9,
                          ignore=[self], traverse_target=self.scene)
            if not hit.hit:
                setattr(self, axis, getattr(self, axis) + amount)
            else:
                setattr(self.velocity, axis, 0)
                if axis in {"x", "z"}:
                    self.forward_speed = 0

    @property
    def scene(self) -> Entity:
        """Return the root scene used by raycasts."""
        from ursina import scene
        return scene

    def update_camera(self) -> None:
        """Place the camera in the selected stable view."""
        if self.camera_mode == "FIRST PERSON":
            camera.position = self.world_position + self.forward * .82 + Vec3(0, .18, 0)
            camera.look_at(camera.position + self.forward * 20)
        else:
            target_position = self.world_position - self.forward * config.CAMERA_DISTANCE
            target_position += Vec3(0, config.CAMERA_HEIGHT, 0)
            camera.position = target_position
            camera.look_at(self.world_position + Vec3(0, .7, 0))

    def reset(self) -> None:
        """Return the drone to its starting position and orientation."""
        self.position = Vec3(self.spawn_position)
        self.rotation = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.forward_speed = 0.0
        self.battery = config.BATTERY_CAPACITY
        self.hover_enabled = True
        self.camera_mode = "THIRD PERSON"
        self.pressed_keys.clear()
        camera.position = self.position - self.forward * config.CAMERA_DISTANCE
        camera.y += config.CAMERA_HEIGHT
        camera.look_at(self)
