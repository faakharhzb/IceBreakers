import json
import pygame as pg


class TileMap:
    def __init__(
        self, tile_size: int, render_scale: float = 1.0
    ) -> None:
        self.tile_size = tile_size
        self.render_scale = render_scale
        self.tilemap = {}
        self.offgrid_tiles = []

        self.directions = [
            pg.Vector2(0, 0),
            pg.Vector2(-1, 0),
            pg.Vector2(1, 0),
            pg.Vector2(0, -1),
            pg.Vector2(0, 1),
            pg.Vector2(-1, -1),
            pg.Vector2(1, -1),
            pg.Vector2(-1, 1),
            pg.Vector2(1, 1),
        ]
        self.ongrid_tiles = [
            "snow",
        ]

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= (
                    self.tile_size * self.render_scale
                )
                matches[-1]["pos"][1] *= (
                    self.tile_size * self.render_scale
                )
                if not keep:
                    del self.tilemap[loc]

        return matches

    def surrounding_tiles(self, pos: pg.Vector2) -> list[str]:
        pos = pg.Vector2(pos)
        tiles = []
        tile_pos = pg.Vector2(
            int(pos.x // (self.tile_size * self.render_scale)),
            int(pos.y // (self.tile_size * self.render_scale)),
        )

        for direction in self.directions:
            check_pos = f"{int(tile_pos.x + (direction.x))};{int(tile_pos.y + (direction.y))}"

            if (
                check_pos in self.tilemap
                and self.tilemap[check_pos]["type"] in self.ongrid_tiles
            ):
                tiles.append(self.tilemap[check_pos])

        return tiles

    def get_physics_tiles(self, pos):
        rects = []
        for tile in self.tilemap.values():
            if tile["type"] in self.ongrid_tiles:
                rects.append(
                    pg.Rect(
                        tile["pos"][0]
                        * self.tile_size
                        * self.render_scale,
                        tile["pos"][1]
                        * self.tile_size
                        * self.render_scale,
                        self.tile_size * self.render_scale,
                        self.tile_size * self.render_scale,
                    )
                )
        return rects

    def read(self, path: str) -> None:
        with open(path, "r") as f:
            data = json.load(f)

        self.tilemap = data["tilemap"]
        self.tile_size = data["tile_size"]
        self.offgrid_tiles = data["offgrid"]

    def write(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(
                {
                    "tilemap": self.tilemap,
                    "tile_size": self.tile_size,
                    "offgrid": self.offgrid_tiles,
                },
                f,
            )

    def draw(
        self,
        surf: pg.Surface,
        assets: dict,
        offset: pg.Vector2 = pg.Vector2(),
        show_spawners: bool = False,
    ) -> None:
        for tile in self.tilemap.values():
            if tile["type"] == "spawners":
                if show_spawners:
                    pass
                else:
                    continue

            position = (
                tile["pos"][0] * self.tile_size * self.render_scale
                - offset.x,
                tile["pos"][1] * self.tile_size * self.render_scale
                - offset.y,
            )
            surf.blit(
                assets[tile["type"]][tile["variant"]],
                position,
            )
