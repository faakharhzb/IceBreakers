from itertools import cycle
import sys

import pygame as pg
from tkinter import filedialog

from src.utilities import load_image, load_images
from src.tilemap import TileMap

RENDER_SCALE = 1


class Editor:
    def __init__(self):
        pg.init()

        pg.display.set_caption("editor")
        self.screen = pg.display.set_mode((1280, 720))
        self.display = pg.Surface(self.screen.get_size())

        self.clock = pg.time.Clock()

        self.assets = {
            "snow": load_images("snow", "black", 1.5),
            "offgrid": [
                load_image("offgrid/tree.png", "alpha", 5),
                load_image("offgrid/rock.png", "alpha", 2),
            ],
            "spawners": [
                load_image("player/idle/0.png", "alpha", 2.7),
                load_image("crystal.png", "alpha", 2.5),
                load_images("blocks", "alpha", 4.2)[0],
            ],
        }
        self.movement = [False, False, False, False]

        self.tilemap = TileMap(32, 1.5)

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.state = "ongrid"
        self.states = cycle(["ongrid", "offgrid", "spawners"])

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.draw(
                self.display,
                self.assets,
                pg.Vector2(render_scroll),
                True,
            )

            current_tile_img = self.assets[
                self.tile_list[self.tile_group]
            ][self.tile_variant].copy()

            current_tile_img.set_alpha(100)

            mpos = (
                pg.Vector2(pg.mouse.get_pos())
                // self.tilemap.render_scale
                * self.tilemap.render_scale
            ).xy
            mpos = [
                int(mpos[0] + self.scroll[0]),
                int(mpos[1] + self.scroll[1]),
            ]

            self.display.blit(current_tile_img, mpos)

            tile_pos = (
                (mpos[0] // self.tilemap.tile_size)
                // self.tilemap.render_scale,
                (mpos[1] // self.tilemap.tile_size)
                // self.tilemap.render_scale,
            )

            if self.clicking and self.state == "ongrid":
                self.tilemap.tilemap[
                    str(tile_pos[0]) + ";" + str(tile_pos[1])
                ] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_pos,
                }
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile["type"]][
                        tile["variant"]
                    ]
                    tile_r = pg.Rect(
                        tile["pos"][0] - self.scroll[0],
                        tile["pos"][1] - self.scroll[1],
                        tile_img.get_width(),
                        tile_img.get_height(),
                    )
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if self.state == "offgrid":
                            self.tilemap.offgrid_tiles.append(
                                {
                                    "type": self.tile_list[
                                        self.tile_group
                                    ],
                                    "variant": self.tile_variant,
                                    "pos": (
                                        (mpos[0] + self.scroll[0]),
                                        (mpos[1] + self.scroll[1]),
                                    ),
                                }
                            )
                    elif self.state == "spawners":
                        self.tilemap.spawners.append(
                            {
                                "type": "spawners",
                                "variant": self.tile_variant,
                                "pos": (
                                    mpos[0] + self.scroll[0],
                                    mpos[1] + self.scroll[1],
                                ),
                            }
                        )
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (
                                self.tile_variant - 1
                            ) % len(
                                self.assets[
                                    self.tile_list[self.tile_group]
                                ]
                            )
                        if event.button == 5:
                            self.tile_variant = (
                                self.tile_variant + 1
                            ) % len(
                                self.assets[
                                    self.tile_list[self.tile_group]
                                ]
                            )
                    else:
                        if event.button == 4:
                            self.tile_group = (
                                self.tile_group - 1
                            ) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (
                                self.tile_group + 1
                            ) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a:
                        self.movement[0] = True
                    if event.key == pg.K_d:
                        self.movement[1] = True
                    if event.key == pg.K_w:
                        self.movement[2] = True
                    if event.key == pg.K_s:
                        self.movement[3] = True
                    if event.key == pg.K_g:
                        self.state = next(self.states)
                    if event.key == pg.K_t:
                        self.tilemap.autotile()
                    if event.key == pg.K_o:
                        path = filedialog.asksaveasfilename(
                            defaultextension=".json",
                            filetypes=[
                                ("JSON files", "*.json"),
                                ("All files", "*.*"),
                            ],
                        )
                        if path:
                            self.tilemap.write(path)
                    if event.key == pg.K_l:
                        path = filedialog.askopenfilename(
                            filetypes=[
                                ("JSON files", "*.json"),
                                ("All files", "*.*"),
                            ]
                        )
                        if path:
                            self.tilemap.read(path)
                    if event.key == pg.K_LSHIFT:
                        self.shift = True
                if event.type == pg.KEYUP:
                    if event.key == pg.K_a:
                        self.movement[0] = False
                    if event.key == pg.K_d:
                        self.movement[1] = False
                    if event.key == pg.K_w:
                        self.movement[2] = False
                    if event.key == pg.K_s:
                        self.movement[3] = False
                    if event.key == pg.K_LSHIFT:
                        self.shift = False

            self.screen.blit(
                pg.transform.scale(
                    self.display, self.screen.get_size()
                ),
                (0, 0),
            )
            pg.display.update()
            self.clock.tick(60)


Editor().run()
