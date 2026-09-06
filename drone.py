"""Player-controlled drone and its simple arcade flight behavior."""

from __future__ import annotations

from time import monotonic

from ursina import Entity, Vec3, camera, color, destroy, invoke, raycast, time
from ursina.collider import BoxCollider

import config


class VirtualProjectile(Entity):
    """A bright fictional training bolt with short-range raycast collision."""

    def __init__(self, owner: "Drone", position: Vec3, direction: Vec3) -> None:
        super().__init__(
            name="virtual_training_bolt",
            model="cube",
            color=color.lime,
            position=position,
            scale=(.10, .10, .55),
        )
        self.owner = owner
        self.direction = Vec3(direction).normalized()
        self.look_at(self.position + self.direction)
        invoke(destroy, self, delay=config.PROJECTILE_LIFETIME)

    def update(self) -> None:
        """Advance the bolt and apply damage to a fictional target on contact."""
        travel = config.PROJECTILE_SPEED * time.dt
        hit = raycast(
            self.world_position,
            self.direction,
            distance=travel + .35,
            ignore=[self, self.owner],
        )
        if hit.hit:
            if hasattr(hit.entity, "take_hit"):
                hit.entity.take_hit(config.PROJECTILE_DAMAGE)
            destroy(self)
            return
        self.position += self.direction * travel


class Drone(Entity):
    """A compact drone entity with keyboard flight and a chase camera."""

    def __init__(self, spawn_position: Vec3 = Vec3(0, 1, -20)) -> None:
        super().__init__(position=spawn_position)
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(2.2, .85, 2.5))
        self.spawn_position = Vec3(spawn_position)
        self.velocity = Vec3(0, 0, 0)
        self.forward_speed = 0.0
        self.lateral_speed = 0.0
        self.battery = config.BATTERY_CAPACITY
        self.health = config.DRONE_HEALTH
        self.hover_enabled = True
        self.camera_mode = "THIRD PERSON"
        self.crashed = False
        self.is_grounded = False
        self.collision_latched = False
        self.status = "READY — TAKE OFF"
        self.last_fire_time = -100.0
        self.pressed_keys: set[str] = set()
        self.rotors: list[Entity] = []
        self.shell_parts: list[tuple[Entity, object]] = []

        # Smooth shells and carefully proportioned primitives create a compact
        # camera-drone silhouette without requiring any external assets.
        shell_color = color.rgb32(32, 145, 205)
        belly_color = color.rgb32(20, 28, 36)
        body = Entity(parent=self, model="sphere", color=shell_color,
                      texture="white_cube", position=(0, .02, 0),
                      scale=(1.0, .42, 1.28))
        belly = Entity(parent=self, model="sphere", color=belly_color,
                       texture="white_cube", position=(0, -.18, -.04),
                       scale=(.82, .25, .96))
        self.shell_parts.extend(((body, shell_color), (belly, belly_color)))

        # A raised canopy and nose-mounted gimbal establish a clear front.
        Entity(parent=self, model="sphere", color=color.rgb32(18, 54, 72),
               texture="white_cube", position=(0, .23, .26), scale=(.58, .22, .62))
        Entity(parent=self, model="sphere", color=color.dark_gray,
               texture="white_cube", position=(0, -.16, .92), scale=(.30, .28, .30))
        Entity(parent=self, model="sphere", color=color.rgb32(20, 95, 130),
               texture="white_cube", position=(0, -.16, 1.14), scale=(.15, .15, .09))

        # Diagonal carbon arms connect the body to four distinct motor pods.
        Entity(parent=self, model="cube", color=color.rgb32(35, 38, 42),
               texture="white_cube", scale=(2.38, .10, .11), rotation_y=42)
        Entity(parent=self, model="cube", color=color.rgb32(35, 38, 42),
               texture="white_cube", scale=(2.38, .10, .11), rotation_y=-42)
        for index, (x, z) in enumerate(((-.88, -.82), (.88, -.82), (-.88, .82), (.88, .82))):
            hub = Entity(parent=self, position=(x, .12, z))
            Entity(parent=hub, model="sphere", color=color.rgb32(28, 30, 33),
                   texture="white_cube", scale=(.25, .20, .25))
            Entity(parent=hub, model="circle", color=color.rgba32(30, 34, 38, 105),
                   texture="white_cube", position=(0, .16, 0), rotation_x=90, scale=.92,
                   double_sided=True)
            Entity(parent=hub, model="cube", color=color.rgba32(28, 30, 34, 225),
                   texture="white_cube", position=(0, .18, 0), scale=(.95, .025, .075))
            Entity(parent=hub, model="cube", color=color.rgba32(28, 30, 34, 225),
                   texture="white_cube", position=(0, .18, 0), scale=(.075, .025, .95))
            light_color = color.lime if z > 0 else color.red
            Entity(parent=hub, model="sphere", color=light_color,
                   texture="white_cube", position=(0, -.04, z / abs(z) * .22), scale=.07)
            self.rotors.append(hub)

        # Twin landing skids sit below four short angled-looking supports.
        for x in (-.52, .52):
            Entity(parent=self, model="cube", color=color.dark_gray,
                   texture="white_cube", position=(x, -.37, 0), scale=(.07, .44, .07))
            Entity(parent=self, model="cube", color=color.black,
                   texture="white_cube", position=(x, -.58, 0), scale=(.09, .07, 1.18))

        self.reset()

    def update_flight(self) -> None:
        """Read keyboard state and apply simplified acceleration and collision."""
        dt = time.dt
        if self.crashed:
            self.velocity = Vec3(0, 0, 0)
            return

        is_down = self.pressed_keys.__contains__
        turn_axis = (
            is_down("right arrow") - is_down("left arrow")
            + is_down("e") - is_down("q")
        )
        self.rotation_y += turn_axis * config.ROTATION_SPEED * dt

        move_axis = is_down("up arrow") - is_down("down arrow")
        strafe_axis = is_down("d") - is_down("a")
        if not move_axis and not strafe_axis:
            self.collision_latched = False
        # Acceleration applies only while an arrow is held. Releasing it stops
        # immediately, so there is no stored momentum after movement input.
        if move_axis and self.battery > 0:
            desired_speed = move_axis * config.DRONE_SPEED
            speed_step = config.DRONE_ACCELERATION * dt
            difference = desired_speed - self.forward_speed
            self.forward_speed += max(-speed_step, min(speed_step, difference))
        else:
            self.forward_speed = 0.0

        if strafe_axis and self.battery > 0:
            desired_strafe = strafe_axis * config.DRONE_SPEED
            speed_step = config.DRONE_ACCELERATION * dt
            difference = desired_strafe - self.lateral_speed
            self.lateral_speed += max(-speed_step, min(speed_step, difference))
        else:
            self.lateral_speed = 0.0

        # Horizontal velocity always follows the drone's nose. This deliberate
        # arcade behavior prevents unwanted sideways drift while steering.
        horizontal_velocity = (
            self.forward * self.forward_speed + self.right * self.lateral_speed
        )
        self.velocity.x = horizontal_velocity.x
        self.velocity.z = horizontal_velocity.z

        vertical = is_down("space") - is_down("left shift")
        if self.battery <= 0:
            vertical = 0
        if vertical:
            self.velocity.y = vertical * config.VERTICAL_SPEED
            if vertical > 0:
                self.is_grounded = False
                self.status = "FLYING"
        elif self.hover_enabled and self.battery > 0:
            self.velocity.y = 0
        else:
            self.velocity.y = max(-config.VERTICAL_SPEED,
                                  self.velocity.y - config.GRAVITY * dt)
        displacement = self.velocity * dt
        self._move_with_collisions(displacement)
        self.y = max(config.MIN_ALTITUDE, min(config.MAX_ALTITUDE, self.y))
        moving = abs(self.forward_speed) > .1 or abs(self.lateral_speed) > .1
        rotor_speed = 900 * dt if (moving or vertical) else 250 * dt
        for rotor in self.rotors:
            rotor.rotation_y += rotor_speed
        horizontal_activity = max(abs(self.forward_speed), abs(self.lateral_speed)) / config.DRONE_SPEED
        activity = horizontal_activity + abs(vertical)
        drain = config.BATTERY_IDLE_DRAIN + config.BATTERY_FLIGHT_DRAIN * activity
        self.battery = max(0.0, self.battery - drain * dt)

    def handle_key(self, key: str) -> None:
        """Track key presses explicitly for consistent movement on macOS."""
        if key.endswith(" up"):
            self.pressed_keys.discard(key[:-3])
        elif key in {"up arrow", "down arrow", "left arrow", "right arrow",
                     "a", "d", "q", "e", "space", "left shift"}:
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

    def fire(self) -> bool:
        """Launch one harmless virtual training projectile."""
        now = monotonic()
        if self.crashed or self.battery <= 0:
            return False
        if now - self.last_fire_time < config.PROJECTILE_COOLDOWN:
            return False
        self.last_fire_time = now
        origin = self.world_position + self.forward * 1.38 + Vec3(0, -.1, 0)
        VirtualProjectile(self, origin, self.forward)
        return True

    def aimed_target_distance(self) -> float | None:
        """Return distance to the fictional target under the crosshair."""
        hit = raycast(self.world_position, self.forward, distance=100, ignore=[self])
        if hit.hit and hasattr(hit.entity, "target_id"):
            return hit.distance
        return None

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
                impact_speed = abs(getattr(self.velocity, axis))
                setattr(self.velocity, axis, 0)
                if axis in {"x", "z"}:
                    self.forward_speed = 0
                    self.lateral_speed = 0
                    if not self.collision_latched:
                        self._apply_impact(impact_speed, landed_on_pad=False)
                        self.collision_latched = True
                elif amount < 0:
                    self.is_grounded = True
                    self._handle_ground_contact(impact_speed)

    def _handle_ground_contact(self, impact_speed: float) -> None:
        """Classify a downward contact as a safe landing or a hard impact."""
        pad_x, pad_z = config.LANDING_PAD_CENTER
        on_pad = (
            abs(self.x - pad_x) <= config.LANDING_PAD_HALF_SIZE
            and abs(self.z - pad_z) <= config.LANDING_PAD_HALF_SIZE
        )
        if impact_speed <= config.SAFE_LANDING_SPEED and on_pad:
            self.status = "SAFE LANDING — TRAINING COMPLETE"
        elif impact_speed > config.SAFE_LANDING_SPEED:
            self._apply_impact(impact_speed, landed_on_pad=on_pad)
        elif not on_pad:
            self.status = "LANDED OUTSIDE THE PAD"

    def _apply_impact(self, impact_speed: float, landed_on_pad: bool) -> None:
        """Convert impact speed into arcade damage and possibly crash."""
        if impact_speed < config.IMPACT_DAMAGE_THRESHOLD:
            return
        damage = (impact_speed - config.IMPACT_DAMAGE_THRESHOLD) * config.IMPACT_DAMAGE_MULTIPLIER
        self.health = max(0.0, self.health - damage)
        if impact_speed >= config.CRASH_IMPACT_SPEED or self.health <= 0:
            self._crash()
            return
        location = "HARD LANDING" if landed_on_pad or self.is_grounded else "COLLISION"
        self.status = f"{location} — {damage:.0f} DAMAGE"
        for part, _ in self.shell_parts:
            part.color = color.orange
        invoke(self._restore_color, delay=.25)

    def _restore_color(self) -> None:
        """Restore the normal body color after a nonfatal impact flash."""
        if not self.crashed:
            for part, normal_color in self.shell_parts:
                part.color = normal_color

    def _crash(self) -> None:
        """Lock controls and show a clear fictional crash state."""
        self.crashed = True
        self.health = 0.0
        self.forward_speed = 0.0
        self.lateral_speed = 0.0
        self.velocity = Vec3(0, 0, 0)
        self.pressed_keys.clear()
        for part, _ in self.shell_parts:
            part.color = color.red
        self.rotation_x = 18
        self.rotation_z = 28
        self.status = "DRONE CRASHED — PRESS R TO RESTART"

    @property
    def scene(self) -> Entity:
        """Return the root scene used by raycasts."""
        from ursina import scene
        return scene

    def update_camera(self) -> None:
        """Place the camera in the selected stable view."""
        if self.camera_mode == "FIRST PERSON":
            camera.position = self.world_position + self.forward * 1.32 + Vec3(0, -.12, 0)
            camera.look_at(camera.position + self.forward * 20)
            camera.rotation_z = 0
        else:
            target_position = self.world_position - self.forward * config.CAMERA_DISTANCE
            target_position += Vec3(0, config.CAMERA_HEIGHT, 0)
            camera.position = target_position
            camera.look_at(self.world_position + Vec3(0, .7, 0))
            camera.rotation_z = 0

    def reset(self) -> None:
        """Return the drone to its starting position and orientation."""
        self.position = Vec3(self.spawn_position)
        self.rotation = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.forward_speed = 0.0
        self.lateral_speed = 0.0
        self.battery = config.BATTERY_CAPACITY
        self.health = config.DRONE_HEALTH
        self.hover_enabled = True
        self.camera_mode = "THIRD PERSON"
        self.crashed = False
        self.is_grounded = False
        self.collision_latched = False
        self.status = "READY — TAKE OFF"
        for part, normal_color in self.shell_parts:
            part.color = normal_color
        self.pressed_keys.clear()
        camera.position = self.position - self.forward * config.CAMERA_DISTANCE
        camera.y += config.CAMERA_HEIGHT
        camera.look_at(self)
        camera.rotation_z = 0
