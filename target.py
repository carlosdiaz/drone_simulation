"""Fictional non-human training targets for Phase 3."""

from collections.abc import Callable
from math import sin

from ursina import Entity, Vec3, color, invoke, time

import config


class TrainingTarget(Entity):
    """A floating robotic target with health, reactions, and respawning."""

    def __init__(
        self,
        position: Vec3,
        target_id: int,
        on_destroyed: Callable[["TrainingTarget"], None],
    ) -> None:
        super().__init__(
            name=f"training_target_{target_id}",
            model="cube",
            color=color.orange,
            position=position,
            scale=(1.25, 1.25, .35),
            collider="box",
        )
        self.target_id = target_id
        self.spawn_position = Vec3(position)
        self.health = config.TARGET_HEALTH
        self.is_active = True
        self.on_destroyed = on_destroyed
        self.float_time = target_id * .7

        # Layered built-in shapes make the object clearly robotic and non-human.
        Entity(parent=self, model="cube", color=color.yellow,
               position=(0, 0, -.12), scale=(.72, .72, .25))
        Entity(parent=self, model="cube", color=color.red,
               position=(0, 0, -.3), scale=(.28, .28, .16))
        Entity(parent=self, model="cube", color=color.dark_gray,
               position=(0, -.72, 0), scale=(.18, .42, .18))

    def update(self) -> None:
        """Give active targets a subtle floating, rotating game effect."""
        if not self.is_active:
            return
        self.float_time += time.dt
        self.rotation_y += 24 * time.dt
        self.y = self.spawn_position.y + sin(self.float_time * 1.7) * .2

    def take_hit(self, damage: float) -> bool:
        """Apply virtual damage and return whether this hit destroyed the target."""
        if not self.is_active:
            return False
        self.health = max(0.0, self.health - damage)
        self.color = color.red
        self.scale *= 1.12
        invoke(self._finish_hit_flash, delay=.12)
        if self.health <= 0:
            self._deactivate()
            return True
        return False

    def _finish_hit_flash(self) -> None:
        if self.is_active:
            self.color = color.orange
            self.scale = (1.25, 1.25, .35)

    def _deactivate(self) -> None:
        """Hide a destroyed target and schedule its return."""
        self.is_active = False
        self.on_destroyed(self)
        self.color = color.lime
        self.scale = (1.8, 1.8, .5)
        invoke(self._hide, delay=.14)
        invoke(self.respawn, delay=config.TARGET_RESPAWN_DELAY)

    def _hide(self) -> None:
        self.enabled = False

    def respawn(self) -> None:
        """Restore the target at its original training location."""
        self.position = Vec3(self.spawn_position)
        self.rotation = Vec3(0, 0, 0)
        self.scale = (1.25, 1.25, .35)
        self.color = color.orange
        self.health = config.TARGET_HEALTH
        self.is_active = True
        self.enabled = True
