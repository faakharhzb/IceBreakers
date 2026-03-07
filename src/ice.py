import pygame as pg
import math

from pygame.typing import Point
from typing import Sequence


class Crystal:
    def __init__(self, surf: pg.Surface, pos: Point) -> None:
        self.surf = surf
        self.rect = surf.get_rect(center=pos)

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
            screen.blit(self.surf, self.position - offset)


class Block:
    def __init__(
        self,
        surfs: Sequence[pg.Surface],
        pos: Point,
        need_to_advance: int = 4,
    ) -> None:
        self.surfs = iter(surfs)
        self.surf = next(self.surfs)
        self.rect = self.surf.get_rect(center=pos)

        self.position = pg.Vector2(pos)
        self.start_y = self.position.copy().y

        self.need_to_advance = need_to_advance
        self.exists = True

    def update(self, advance: bool = False) -> bool:
        if not self.exists:
            return

        if advance:
            try:
                self.surf = next(self.surfs)
                self.rect.size = self.surf.get_size()
            except StopIteration:
                return True

        self.rect.center = self.position

        return False

    def draw(
        self, screen: pg.Surface, offset: pg.Vector2 = pg.Vector2()
    ) -> None:
        if self.exists:
            screen.blit(self.surf, self.position - offset)
