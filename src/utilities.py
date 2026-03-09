import sys
import pygame as pg
import os
import random

from pygame.typing import ColorLike, Point


def load_image(
    relpath: str,
    colorkey: ColorLike = "white",
    scale: float | tuple[float, float] = 1.0,
) -> pg.Surface:
    full_path = os.path.join(os.path.dirname(sys.argv[0]), "assets", "images", relpath)
    surf = pg.image.load(full_path)
    if colorkey == "alpha":
        surf = surf.convert_alpha()
    else:
        surf = surf.convert()
        surf.set_colorkey(colorkey)
    return pg.transform.scale_by(surf, scale)


def load_images(
    folder: str,
    colorkey: ColorLike = "white",
    scale: float | tuple[float, float] = 1.0,
) -> list[pg.Surface]:
    base_path = os.path.join(os.path.dirname(sys.argv[0]), "assets", "images", folder)
    images = []
    for filename in sorted(os.listdir(base_path)):
        relpath = os.path.join(folder, filename)
        images.append(load_image(relpath, colorkey, scale))

    return images


def load_audio(path: str, volume: float = 1.0) -> pg.Sound:
    full_path = os.path.join(os.path.dirname(sys.argv[0]), "assets", "audio", path)
    sound = pg.Sound(full_path)
    sound.set_volume(min(1, max(0, volume)))
    return sound


def get_random_position(
    points: list[pg.Vector2],
    size: Point,
    radius: int,
    max_rect: pg.Rect,
) -> pg.Vector2:
    while True:
        x = random.randint(max_rect.left + size[0], max_rect.right - size[0])
        y = random.randint(max_rect.top + size[1], max_rect.bottom - size[1])

        valid = True
        for point in points:
            dist = point.distance_to((x, y))
            if dist < radius:
                valid = False
                break

        if not valid:
            continue

        return pg.Vector2(x, y)
