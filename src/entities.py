import pygame as pg
from itertools import cycle


class Entity:
    def __init__(
        self,
        pos: list[int],
        image: pg.Surface | dict[str, list[pg.Surface]],
        speed: float,
        frame_delay: int = 250,
    ) -> None:
        self.animations: dict[str, cycle] = {}
        self.flipped_animations: dict[str, cycle] = {}

        self.image_iter: cycle | None = None
        self.state = "idle"
        self._flipped = False

        if isinstance(image, pg.Surface):
            self.image = image
            self.flipped_image = pg.transform.flip(image, True, False)
        elif isinstance(image, dict):
            for state, frames in image.items():
                self.animations[state] = cycle(frames)
                self.flipped_animations[state] = cycle(
                    [
                        pg.transform.flip(frame, True, False)
                        for frame in frames
                    ]
                )

            self.state = next(iter(image))
            self.image_iter = self.animations[self.state]
            self.image = next(self.image_iter)

        else:
            raise TypeError(
                "image must be Surface or dict[str, list[Surface]]"
            )

        self.rect = self.image.get_rect(center=pos)
        self.position = pg.Vector2(pos)
        self.velocity = pg.Vector2()
        self.terminal_velocity = 40

        self.collisions = {
            "top": False,
            "bottom": False,
            "right": False,
            "left": False,
        }

        self.speed = speed
        self.frame_delay = frame_delay
        self.frame_timer = pg.time.get_ticks()

    def set_flipped(self, flipped: bool) -> None:
        if self._flipped != flipped:
            self._flipped = flipped
            if self.image_iter:
                animations = (
                    self.flipped_animations
                    if flipped
                    else self.animations
                )
                self.image_iter = animations[self.state]
                self.image = next(self.image_iter)

    def set_state(self, state: str) -> None:
        animations = (
            self.flipped_animations
            if self._flipped
            else self.animations
        )

        if state != self.state and state in animations:
            self.state = state
            self.image_iter = animations[state]
            self.image = next(self.image_iter)
            self.frame_timer = pg.time.get_ticks()

    def update(self, dt: float, surround_tiles: list[pg.Rect]) -> None:
        self.collisions = {
            "top": False,
            "bottom": False,
            "right": False,
            "left": False,
        }

        self.velocity.y = min(
            self.velocity.y + 0.045, self.terminal_velocity
        )

        self.position.x += self.velocity.x * self.speed * dt
        self.rect.x = self.position.x

        for tile in surround_tiles:
            if self.rect.colliderect(tile):
                if self.velocity.x > 0:
                    self.rect.right = tile.left
                    self.collisions["right"] = True
                if self.velocity.x < 0:
                    self.rect.left = tile.right
                    self.collisions["left"] = True

                self.position.x = self.rect.x

        self.position.y += self.velocity.y * dt
        self.rect.y = self.position.y

        for tile in surround_tiles:
            if self.rect.colliderect(tile):
                if self.velocity.y > 0:
                    self.rect.bottom = tile.top
                    self.collisions["bottom"] = True
                if self.velocity.y < 0:
                    self.rect.top = tile.bottom
                    self.collisions["top"] = True

                self.velocity.y = 0
                self.position.y = self.rect.y

        self.velocity.x = 0

        if self.collisions["bottom"]:
            self.velocity.y = 0

        if self.image_iter:
            if (
                pg.time.get_ticks() - self.frame_timer
                >= self.frame_delay
            ):
                self.image = next(self.image_iter)
                self.frame_timer = pg.time.get_ticks()

    def draw(
        self, screen: pg.Surface, offset: pg.Vector2 = pg.Vector2()
    ) -> None:
        screen.blit(self.image, self.position - offset)


class Player(Entity):
    def __init__(
        self,
        pos: list[int],
        image: pg.Surface | dict[str, list[pg.Surface]],
        speed: float,
        frame_delay: int = 250,
        crystal_amount: int = 0,
    ) -> None:
        super().__init__(pos, image, speed, frame_delay)

        self.crystal_amount = crystal_amount
        self.crystal_max = 2

        self.jumped = False

    def update(self, dt: float, surround_tiles: list[pg.Rect]) -> None:
        if self.velocity.x != 0:
            self.set_state("moving")
            self.set_flipped(self.velocity.x < 0)
        else:
            self.set_state("idle")

        super().update(dt, surround_tiles)

        key = pg.key.get_pressed()

        if (
            key[pg.K_w]
            and self.collisions["bottom"]
            and not self.collisions["top"]
        ):
            self.velocity.y = -6.8
            self.jumped = True
        else:
            self.jumped = False

        if key[pg.K_a]:
            self.velocity.x = -1
        if key[pg.K_d]:
            self.velocity.x = 1

        self.crystal_amount = max(
            0, min(self.crystal_max, self.crystal_amount)
        )
