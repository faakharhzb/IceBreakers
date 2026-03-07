import random
import pygame as pg
from pygame.typing import Point

from src.gui_elements import Button
from src.utilities import get_random_position


class SkillCheck:
    def __init__(self, size: Point, pos: Point) -> None:
        self.surf = pg.Surface(size, pg.SRCALPHA)
        self.surf.fill((63, 63, 64, 150))

        self.size = pg.Vector2(size)
        self.rect = self.surf.get_rect(topleft=pos)

        self.bar = pg.Rect(
            self.rect.left + self.size.x // 8,
            self.rect.top + self.size.y // 2 - self.size.y // 10,
            self.size.x * 3 // 4,
            self.size.y // 5,
        )

        self.block = pg.Surface((50, self.bar.h))
        self.block.fill("green")
        self.block_rect = self.block.get_rect(midleft=self.bar.midleft)

        self.goal = pg.Surface((100, self.bar.h))
        self.goal.fill("grey")
        self.goal_rect = self.goal.get_rect(
            topleft=(
                random.randint(
                    int(self.bar.left + self.block_rect.w + 20),
                    int(self.bar.right),
                ),
                self.bar.top,
            )
        ).clamp(self.bar)
        self.goal_moving = False
        self.goal_move_speed = 15
        self.goal_target_pos = None

        self.block_in_goal_timer = 0
        self.block_in_goal_max = 1.25

        self.block_in_goal_surf = pg.Surface(
            (self.bar.w - 50, self.bar.h // 2)
        )
        self.block_in_goal_surf.fill("red")

        self.block_in_goal_rect = pg.Rect(
            self.bar.left,
            self.bar.top - 150,
            self.bar.w - 50,
            self.bar.h // 2,
        )
        self.block_in_goal_outline = self.block_in_goal_rect.copy()

    def update(self, dt: float) -> bool:
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            if self.block_rect.colliderect(self.goal_rect):
                speed = 100
            else:
                speed = 10
            self.block_rect.x += speed * dt
        else:
            self.block_rect.x -= 6.5 * dt

        self.block_rect.clamp_ip(self.bar)

        if self.goal_rect.colliderect(self.block_rect):
            self.block_in_goal_timer += dt / 60
        else:
            self.block_in_goal_timer -= dt / 60

        self.block_in_goal_timer = max(
            0, min(self.block_in_goal_max, self.block_in_goal_timer)
        )

        if self.block_in_goal_timer >= self.block_in_goal_max:
            return True

        progress = self.block_in_goal_timer / self.block_in_goal_max
        self.block_in_goal_rect.w = max(
            0,
            min(
                self.block_in_goal_outline.w,
                progress * self.block_in_goal_outline.w,
            ),
        )
        return False

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.surf, self.rect)

        pg.draw.rect(screen, "black", self.bar, 5)

        pg.draw.rect(screen, "red", self.block_in_goal_rect)
        pg.draw.rect(screen, "black", self.block_in_goal_outline, 2)

        screen.blit(self.goal, self.goal_rect)
        screen.blit(self.block, self.block_rect)


class Clicker:
    def __init__(
        self,
        pos: Point,
        size: Point,
        max_exist_time: int = 1250,
        max_used: int = 5,
    ) -> None:
        self.surf = pg.Surface(size, pg.SRCALPHA)
        self.surf.fill((63, 63, 64, 100))
        self.rect = self.surf.get_rect(topleft=pos)

        self.max_spots = 5
        self.spots = []

        self.clicked = 0

        self.spot_surf = pg.Surface((50, 50), pg.SRCALPHA)
        self.spot_surf.fill((250, 250, 250, 150))

        self.new_spot_delay = 1400
        self.new_spot_timer = pg.time.get_ticks()
        self.exist_max_time = max_exist_time

        self.used = 0
        self.max_used = max_used

        self.is_clicked = False

    def update(self, dt: float) -> bool:
        if (
            pg.time.get_ticks() - self.new_spot_timer
            >= self.new_spot_delay
            and len(self.spots) < self.max_spots
        ):
            self.spots.append(
                Button(
                    self.spot_surf,
                    get_random_position(
                        [button.position for button in self.spots],
                        self.spot_surf.get_size(),
                        150,
                        self.rect,
                    ),
                    None,
                    False,
                )
            )
            if len(self.spots) < self.max_spots:
                self.new_spot_timer = pg.time.get_ticks()

        clicks = 0
        for spot in self.spots[:]:
            if spot.clicked(circle=True):
                self.spots.remove(spot)
                self.clicked += 1
                self.used += 1
                clicks += 1

            if (
                pg.time.get_ticks() - spot.start_time
                >= self.exist_max_time
            ):
                return True

        if clicks:
            self.is_clicked = True
        else:
            self.is_clicked = False

        return False

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.surf, self.rect)
        for spot in self.spots:
            spot.radius += 0.07
            pg.draw.circle(
                screen, (48, 46, 44), spot.rect.center, spot.radius
            )
            spot.draw(screen, circle=True)
