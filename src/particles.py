import pygame as pg
import random

from pygame.typing import Point


class Particle:
    def __init__(self, position: Point, speed: float) -> None:
        self.position = pg.Vector2(position)
        self.fall_speed = speed
        self.colour = "white"

        self.surf = pg.Surface((7, 7))
        self.surf.fill(self.colour)
        self.rect = self.surf.get_rect(center=position)

        self.shift = random.uniform(1, 5)

    def update(self, dt: float) -> None:
        self.position.y += self.fall_speed * dt
        self.rect.centery = self.position.y

    def draw(
        self, screen: pg.Surface, offset: pg.Vector2 = pg.Vector2()
    ) -> None:
        screen.blit(self.surf, self.position)
