#!/usr/bin/env python3
"""Generate textures/armor_stand_arms_trident.png: a tall (5x32) upright
trident wield-image, used to display a trident held on the stand's arm.

Why: on Mineclonia the trident item ships a tall vertical wield_image built
from its entity texture, so it shows "standing up" on the stand rather than
angled forward like a sword. VoxeLibre's trident has no such wield_image
(only a 16x16 diagonal icon), so it would render angled. This bundles the
same upright strip -- sliced from Mineclonia's trident entity texture, the
exact columns Mineclonia's own wield_image uses -- and the mod shows it for
tridents held on a VoxeLibre stand (see init.lua), matching the Mineclonia
look the way players expect.

Re-run after a Mineclonia update if its trident entity texture changes:
    python3 tools/gen_trident_texture.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.expanduser(
    "~/.var/app/org.luanti.luanti/.minetest/games/mineclonia/"
    "mods/ITEMS/mcl_tridents/textures/mcl_tridents_trident_entity.png"
)
OUT = os.path.join(HERE, "..", "textures", "armor_stand_arms_trident.png")

# Mineclonia's wield_image is "blank.png^[resize:5x32^[combine:5x32:-19,0=
# mcl_tridents_trident_entity.png" -- i.e. a 5-wide vertical slice of the
# entity texture starting at column 19 (prongs + crossbar + shaft).
SLICE_X0 = 19
SLICE_W = 5
SLICE_H = 32


def main():
    src = Image.open(SOURCE).convert("RGBA")
    strip = src.crop((SLICE_X0, 0, SLICE_X0 + SLICE_W, SLICE_H))
    strip.save(OUT)
    print("wrote %s (%dx%d slice of %s)" % (OUT, SLICE_W, SLICE_H, SOURCE))


if __name__ == "__main__":
    main()
