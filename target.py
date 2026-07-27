"""Fictional training-object foundation used by later simulator phases."""

from ursina import Entity, Vec3, color


class TrainingTarget(Entity):
    """A harmless colored marker that can already be placed in the arena."""

    def __init__(self, position: Vec3, target_id: int) -> None:
        super().__init__(model="cube", color=color.orange, position=position,
                         scale=(1.2, 1.2, 1.2), collider="box")
        self.target_id = target_id

