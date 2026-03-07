import pygame as pg
import math

from pygame.typing import Point


class Key:
    def __init__(self, image: pg.Surface, pos: Point) -> None:
        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.position = pg.Vector2(pos)
        self.start_y = self.position.copy().y

        self.exists = True

    def update(self) -> None:
        if not self.exists:
            return

        self.position.y = (
            self.start_y + math.sin(pg.time.get_ticks() * 0.0065) * 5
        )
        self.rect.centery = self.position.y

    def draw(
        self, screen: pg.Surface, offset: pg.Vector2 = pg.Vector2()
    ) -> None:
        if self.exists:
            screen.blit(self.image, self.position - offset)
