import math
import random
import typing
import pygame as pg
from pygame.typing import ColorLike

from src.ice import Crystal, Block
from src.particles import Particle
from src.entities import Player
from src.tilemap import TileMap
from src.utilities import load_image, load_images
from src.gui_elements import Button
from src.puzzles import Clicker, SkillCheck
from src.key import Key


class Main:
    def __init__(self) -> None:
        pg.init()

        self.w, self.h = 1280, 720
        self.size = pg.Vector2(self.w, self.h)
        self.screen = pg.display.set_mode(self.size)
        pg.display.set_caption("IceBreakers")

        self.clock = pg.time.Clock()
        self.fps_update_delay = pg.time.get_ticks()

        self.images = {
            "player": {
                "idle": load_images("player/idle", "alpha", 2.7),
                "moving": load_images("player/moving", "alpha", 2.7),
            },
            "snow": load_images("snow", "black", 1.5),
            "offgrid": [
                load_image("offgrid/tree.png", "alpha", 5),
                load_image("offgrid/rock.png", "alpha", 2),
            ],
            "crystal": load_image("crystal.png", "alpha", 2.5),
            "block": load_images("blocks", "alpha", 4.2),
            "key": load_image("key.png", "alpha", 3),
            "small_key": load_image("key.png", "alpha", 1.7),
        }

        self.tilemap = TileMap(32, 1.5)
        self.load_level(0)

        self.font = pg.Font(size=40)

        self.message = 0
        self.message_rect = 0
        self.message_start = 0
        self.message_duration = 0

        self.offset = pg.Vector2()

        self.extract_button_surf = self.font.render(
            "[E] Extract", True, (0, 0, 100), "white"
        )
        self.extract_button = Button(
            self.extract_button_surf, (0, 0), show_surround=False
        )

        self.break_button_surf = self.font.render(
            "[E] Break", True, (0, 0, 100), "white"
        )
        self.break_button = Button(
            self.break_button_surf, (0, 0), show_surround=False
        )

        self.collect_key_button_surf = self.font.render(
            "[E] Collect Key", True, (0, 0, 100), "white"
        )
        self.collect_key_button = Button(
            self.collect_key_button_surf, (0, 0), show_surround=False
        )

        self.clicker_active = False
        self.skill_check_active = False

        self.particles = []
        self.spawn_snow()
        self.spawn_snow_delay = pg.time.get_ticks()

        self.max_keys = 5
        self.current_keys = 0
        self.prev_keys_text = ""
        self.prev_keys = -1

        self.dt = 1
        self.running = True

    def respawn(self) -> None:
        self.player.position = self.player_pos
        self.player.crystal_amount = 0

        self.skill_check_active = False
        self.clicker_active = False

        self.message = 0
        self.message_rect = 0
        self.message_start = 0
        self.message_duration = 0

        self.current_crystal = None
        self.crystal_used = 0
        for crystal in self.crystals:
            crystal.exists = True

        self.block.surf = self.images["block"][0]

        if hasattr(self, "key"):
            self.key.exists = True

    def load_level(self, map_id: typing.SupportsInt) -> None:
        self.tilemap.read("assets/maps/" + str(map_id) + ".json")

        self.crystal_pos = []

        self.clicker_max_exist_time = 1290
        self.clicker_max_exist_time -= (map_id + 1) * 40

        for spawner in self.tilemap.extract(
            [("spawners", 0), ("spawners", 1), ("spawners", 2)]
        ):
            if spawner["variant"] == 0:
                self.player_pos = pg.Vector2(spawner["pos"])
                self.player = Player(
                    self.player_pos, self.images["player"], 6.5, 150, 2
                )
            elif spawner["variant"] == 1:
                pos = spawner["pos"]
                self.crystal_pos.append(pos)
            elif spawner["variant"] == 2:
                need_to_advance = 1 + (map_id + 2)
                self.block = Block(
                    self.images["block"],
                    spawner["pos"],
                    need_to_advance,
                )
                self.advance_block = False

                self.max_crystals_needed = (
                    self.player.crystal_amount * 2
                )

                self.clicks_per_crystal = (
                    (
                        (len(self.images["block"]))
                        * self.block.need_to_advance
                    )
                    // self.max_crystals_needed
                ) + 1

        self.crystals = []
        self.spawn_crystals()
        self.current_crystal = None
        self.crystal_used = 0

    def show_message(
        self, message: str, colour: ColorLike = "white", dur: int = 1000
    ) -> None:
        self.message = self.font.render(message, True, colour)
        self.message_rect = self.message.get_rect(
            center=(self.w // 2, self.h - self.h // 7)
        )

        self.message_start = pg.time.get_ticks()
        self.message_duration = dur

    def manage_extract_button(self, crystal: Crystal) -> None:
        if crystal.position.distance_to(self.player.position) >= 125:
            return
        elif self.player.crystal_amount >= self.player.crystal_max:
            return
        elif self.skill_check_active:
            return

        self.extract_button.position = crystal.position.copy()
        self.extract_button.position.y -= 50

        if (
            self.extract_button.clicked(self.offset)
            or pg.key.get_just_pressed()[pg.K_e]
        ):
            self.current_crystal = self.crystals.index(crystal)
            size = self.size - (self.size // 10)
            pos = (self.size - size) // 2
            self.skill_check = SkillCheck(size, pos)
            self.skill_check_active = True
        else:
            self.current_crystal = None

        self.extract_button.draw(self.screen, self.offset)

    def manage_break_button(self) -> None:
        if self.block.position.distance_to(self.player.position) >= 125:
            return
        elif self.clicker_active:
            return
        elif not self.block.exists:
            return

        self.break_button.position = self.block.position.copy()
        self.break_button.position.y = (
            self.block.start_y
            + math.sin(pg.time.get_ticks() * 0.0065) * 5
        ) - 50

        if (
            self.break_button.clicked(self.offset)
            or pg.key.get_just_pressed()[pg.K_e]
        ):
            if not self.player.crystal_amount:
                self.show_message("You have no crystals.", dur=1500)
                return

            size = self.size - (self.size // 10)
            pos = (self.size - size) // 2
            self.clicker = Clicker(pos, size)
            self.clicker_active = True

        self.break_button.draw(self.screen, self.offset)

    def manage_collect_key_button(self) -> None:
        if self.key.position.distance_to(self.player.position) >= 125:
            return
        if self.block.exists:
            return
        if not self.key.exists:
            return

        self.collect_key_button.position = self.key.position.copy()
        self.collect_key_button.position.y = (
            self.block.start_y
            + math.sin(pg.time.get_ticks() * 0.0065) * 5
        ) - 50

        if (
            self.collect_key_button.clicked(self.offset)
            or pg.key.get_just_pressed()[pg.K_e]
        ):
            self.current_keys += 1
            self.key.exists = False
            self.show_message("+1 key collected.", dur=1500)

        self.collect_key_button.draw(self.screen, self.offset)

    def spawn_crystals(self) -> None:
        self.crystals.extend(
            [
                Crystal(self.images["crystal"], pos)
                for pos in self.crystal_pos
            ]
        )

    def spawn_snow(self) -> None:
        self.particles.extend(
            [
                Particle(
                    (i, -20 + self.offset.y), random.uniform(1.3, 3.5)
                )
                for i in range(
                    -100, self.w + 100, random.randint(10, 100)
                )
            ]
        )

    def check_particle_collision(self) -> None:
        for particle in self.particles[:]:
            if particle.rect.top >= self.h:
                self.particles.remove(particle)

    def manage_skill_check(self) -> None:
        if not self.skill_check_active:
            return

        won = self.skill_check.update(self.dt)
        self.skill_check.draw(self.screen)

        if won:
            self.crystals[self.current_crystal].exists = False
            self.player.crystal_amount += 1
            self.skill_check_active = False
            self.show_message("+1 crystal.")

        if self.player.velocity.x != 0:
            self.skill_check_active = False

    def manage_clicker(self) -> None:
        if not self.clicker_active:
            return
        if not self.player.crystal_amount:
            self.clicker_active = False
            return

        if self.player.velocity.x != 0:
            self.clicker_active = False

        lost = self.clicker.update(self.dt)
        if lost:
            self.clicker_active = False
            self.show_message("Too slow, try again.", dur=1500)

        if self.clicker.is_clicked:
            self.crystal_used += 1
        if self.crystal_used >= self.clicks_per_crystal:
            self.player.crystal_amount = min(
                self.player.crystal_max,
                max(0, self.player.crystal_amount - 1),
            )
            self.clicker.used -= self.clicks_per_crystal
            self.crystal_used = 0
            self.show_message("-1. Your crystal broke.")

        self.clicker.draw(self.screen)

    def draw_current_crystals(self) -> None:
        pos = pg.Vector2(10, 5)
        for i in range(self.player.crystal_amount):
            self.screen.blit(self.images["crystal"], pos)
            pos.x += 20 + self.images["crystal"].get_width()

    def draw_current_keys(self) -> None:
        pos = pg.Vector2(self.w - self.w // 5, 5)

        if self.prev_keys != self.current_keys:
            self.prev_keys_text = self.font.render(
                f"{self.current_keys} / {self.max_keys}", True, "white"
            )
            self.prev_keys = self.current_keys

        self.screen.blit(self.prev_keys_text, pos)

        pos.x += 20 + self.prev_keys_text.get_width()
        self.screen.blit(self.images["small_key"], pos)

    def manage_block_break(self) -> None:
        if not self.clicker_active:
            return
        if not self.player.crystal_amount:
            return

        clicked = self.clicker.clicked

        if clicked >= self.block.need_to_advance:
            self.advance_block = True
            self.clicker.clicked -= self.block.need_to_advance
        else:
            self.advance_block = False

    def run(self) -> None:
        while self.running:
            self.screen.fill((0, 0, 20))

            self.offset += (
                self.player.position - self.size // 2 - self.offset
            ) // 30
            self.offset = pg.Vector2(
                int(self.offset.x), int(self.offset.y)
            )

            self.tilemap.draw(self.screen, self.images, self.offset)

            for particle in self.particles:
                particle.update(self.dt)
                particle.draw(self.screen, self.offset)

            for crystal in self.crystals:
                crystal.update()
                self.manage_extract_button(crystal)
                crystal.draw(self.screen, self.offset)

            self.check_particle_collision()

            if pg.time.get_ticks() - self.spawn_snow_delay >= 1000:
                self.spawn_snow()
                self.spawn_snow_delay = pg.time.get_ticks()

            self.draw_current_crystals()
            self.draw_current_keys()

            self.manage_block_break()

            broken = self.block.update(self.advance_block)
            if broken:
                self.show_message("You broke the ice block!", dur=2000)
                self.block.exists = False
                self.clicker_active = False

            if not self.block.exists:
                if not hasattr(self, "key"):
                    pos = self.block.position.copy()
                    pos.y -= 8
                    self.key = Key(self.images["key"], pos)

                self.key.update()
                self.key.draw(self.screen, self.offset)

                self.manage_collect_key_button()

            self.block.draw(self.screen, self.offset)

            self.manage_break_button()

            self.player.update(
                self.dt,
                self.tilemap.get_physics_tiles(
                    pg.Vector2(self.player.rect.center)
                ),
            )

            if self.player.velocity.y >= 40:
                self.respawn()

            self.player.draw(self.screen, self.offset)

            self.manage_skill_check()
            self.manage_clicker()

            if (
                self.message
                and self.message_rect
                and self.message_start
                and self.message_duration
            ):
                elapsed = pg.time.get_ticks() - self.message_start
                if elapsed < self.message_duration:
                    if elapsed > self.message_duration / 2:
                        message = self.message.copy()
                        alpha = (
                            (1 - (elapsed / self.message_duration))
                            * 255
                        ) % 255
                        message.set_alpha(alpha)
                    else:
                        message = self.message

                    self.screen.blit(message, self.message_rect)
                else:
                    self.message = 0
                    self.message_rect = 0
                    self.message_start = 0
                    self.message_duration = 0

            self.dt = (self.clock.tick() / 1000) * 60
            pg.display.flip()

            if pg.time.get_ticks() - self.fps_update_delay >= 500:
                pg.display.set_caption(
                    f"IceBreakers | FPS: {self.clock.get_fps():.1f}"
                )
                self.fps_update_delay = pg.time.get_ticks()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

        pg.quit()
        raise SystemExit


if __name__ == "__main__":
    main = Main()
    main.run()
