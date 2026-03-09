import pygame as pg

from pygame.typing import Point


class Button:
    def __init__(
        self,
        image: pg.Surface,
        position: Point,
        sound: pg.Sound | None = None,
        show_surround: bool = True,
        surround_size: Point | None = None,
    ) -> None:
        self.image = image
        self.rect = image.get_rect(center=position)
        if surround_size is not None:
            self.surround_rect = pg.Rect(0, 0, *surround_size)
            self.surround_rect.center = position
        elif surround_size is None and show_surround:
            self.surround_rect = pg.Rect(0, 0, 300, 70)
            self.surround_rect.center = position
        else:
            self.surround_rect = None

        self.position = position

        self.sound = sound

        self.show_outline = False
        self.show_surround = show_surround

        self.start_time = pg.time.get_ticks()

        self.base_radius = 20
        self.radius = 20

    def hovered(
        self,
        offset: pg.Vector2 = pg.Vector2(),
        circle: bool = False,
    ) -> bool:
        if circle:
            point = pg.Vector2(self.rect.center)
            mpos = pg.Vector2(pg.mouse.get_pos()) + offset

            hovered = True if point.distance_to(mpos) <= self.radius else False
        else:
            rect = self.surround_rect if self.show_surround else self.rect
            hovered = rect.collidepoint(pg.Vector2(pg.mouse.get_pos()) + offset)
        if hovered and self.show_surround:
            self.show_outline = True
        else:
            self.show_outline = False

        return hovered

    def clicked(self, offset: pg.Vector2 = pg.Vector2(), circle: bool = False) -> bool:
        clicked = (
            pg.mouse.get_just_pressed()[0] if self.hovered(offset, circle) else False
        )
        if clicked and self.sound is not None:
            self.sound.play()

        return clicked

    def draw(
        self,
        screen: pg.Surface,
        offset: pg.Vector2 = pg.Vector2(),
        circle: bool = False,
    ) -> None:
        self.rect.topleft = self.position
        if self.surround_rect is not None:
            self.surround_rect.topleft = self.position

        if circle:
            pg.draw.aacircle(screen, "grey", self.rect.center, self.base_radius)
        else:
            screen.blit(self.image, self.position - offset)

        if self.show_outline:
            pg.draw.rect(screen, "blue", self.surround_rect, 4)
