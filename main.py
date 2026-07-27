"""Entry point and arena setup for Drone Simulation Phase 2."""

from ursina import AmbientLight, DirectionalLight, Entity, Sky, Ursina, Vec3, application, color, window

import config
from drone import Drone
from hud import FlightHUD


app = Ursina(title=config.WINDOW_TITLE, borderless=False)
window.size = config.WINDOW_SIZE
window.color = color.rgb(120, 180, 220)


def create_arena() -> None:
    """Build a compact arena entirely from Ursina primitives."""
    arena = config.ARENA_SIZE
    Entity(model="plane", texture="white_cube", texture_scale=(arena, arena),
           scale=arena, color=color.rgb(80, 135, 70), collider="box")
    # High-contrast strips make horizontal motion visible from the chase camera.
    for offset in range(-30, 31, 10):
        Entity(model="cube", color=color.rgba(220, 220, 190, 120),
               position=(offset, .025, 0), scale=(.08, .025, 68))
        Entity(model="cube", color=color.rgba(220, 220, 190, 120),
               position=(0, .026, offset), scale=(68, .025, .08))
    wall_color = color.rgb(105, 110, 120)
    for position, scale in (
        ((0, 2, arena / 2), (arena, 4, 1)),
        ((0, 2, -arena / 2), (arena, 4, 1)),
        ((arena / 2, 2, 0), (1, 4, arena)),
        ((-arena / 2, 2, 0), (1, 4, arena)),
    ):
        Entity(model="cube", color=wall_color, position=position, scale=scale, collider="box")

    for position, scale, building_color in (
        ((-15, 2, 2), (7, 4, 7), color.rgb(150, 130, 105)),
        ((12, 3, 8), (9, 6, 6), color.rgb(125, 140, 155)),
        ((0, 1.5, 20), (6, 3, 8), color.rgb(165, 145, 115)),
        ((20, 2, -10), (5, 4, 10), color.rgb(115, 130, 145)),
    ):
        Entity(model="cube", color=building_color, position=position,
               scale=scale, collider="box")

    Entity(model="cube", color=color.rgb(45, 45, 50), position=(0, .08, -20),
           scale=(7, .12, 7), collider="box")
    Entity(model="cube", color=color.yellow, position=(0, .16, -20),
           scale=(3.2, .03, .45))
    Entity(model="cube", color=color.yellow, position=(0, .16, -20),
           scale=(.45, .03, 3.2))

    Sky(color=color.rgb(120, 185, 235))
    AmbientLight(color=color.rgba(160, 160, 160, 255))
    sun = DirectionalLight(color=color.rgba(255, 245, 220, 255))
    sun.look_at(Vec3(1, -1, -1))


create_arena()
drone = Drone()
hud = FlightHUD()


def update() -> None:
    """Advance player flight and the chase camera once per frame."""
    drone.update_flight()
    drone.update_camera()
    hud.update(drone)


def input(key: str) -> None:
    """Handle one-shot global controls."""
    drone.handle_key(key)
    if key == "r":
        drone.reset()
    elif key == "c":
        drone.switch_camera()
    elif key == "h":
        drone.toggle_hover()
    elif key == "escape":
        application.quit()


if __name__ == "__main__":
    app.run()
