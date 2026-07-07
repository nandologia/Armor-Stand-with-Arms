# Armor Stand with Arms

An armor stand that has **arms** — so it can show off your armor **and** hold
a **weapon** in one hand and a **shield** in the other. A mod for
[Mineclonia](https://content.luanti.org/packages/ryvnf/mineclonia/).

It works just like the normal armor stand you already know, but now your
gear has somewhere to pose. Set up a knight by the door, show off your best
sword, or build a little armory room where every stand holds a different
weapon.

## How to craft it

Put **8 sticks** around a **Smooth Stone Slab** in the crafting table:

```
Stick   Stick   Stick
Stick   Stick   Stick
Stick   Slab    Stick
```

(That is the same recipe as the normal armor stand, just with extra sticks
down the sides to make the arms.)

## How to use it

- **Put armor on it** — hold a helmet, chestplate, leggings, or boots and
  use them on the stand, exactly like the normal armor stand.
- **Give it a weapon** — hold a sword, axe, mace, bow, or crossbow and use
  it on the stand. The weapon appears in its right hand.
- **Give it a shield** — hold a shield and use it on the stand. The shield
  appears on its other arm.
- Other items (blocks, food, tools) are handed back — the stand only takes
  armor, weapons, and shields.
- **Take things back** — with an empty hand, use the place key on the stand.
  Aim at a piece of armor to take that piece; aim at an empty spot to take
  the weapon first, then the shield.
- **Turn it** — use a screwdriver to rotate the stand; the weapon and shield
  turn with it.
- Break the stand and everything it was holding drops on the ground.

## Requirements

Made for **Mineclonia**. It needs the game's own armor stand mod
(`mcl_armor_stand`) to be present, which it always is in Mineclonia.

## Credits & license

This mod is based on Mineclonia's built-in armor stand by **Stuart Jones**
(stujones11). The stand model and icon are extended versions of Mineclonia's
originals.

- Code: **LGPL 2.1 or later**
- Models & textures: **CC BY-SA 3.0**

See [LICENSE.txt](LICENSE.txt) for the full details.

---

### For modders

The extra arms on the model and the inventory icon are generated from
Mineclonia's own files by the scripts in `tools/`, so they always match the
game's art:

- `tools/gen_mesh.py` — adds the two arms to Mineclonia's armor stand model.
- `tools/gen_icon.py` — adds the arms to Mineclonia's stand icon.
- `tools/test_load.py` — loads `init.lua` under a stub API (via `lupa`) and
  checks the placing/taking/rotating/dropping logic without launching the
  game.

Re-run the `gen_*` scripts after a Mineclonia update if the game ever
changes its armor stand model or icon. The weapon and shield positions live
in the `HANDS` table at the top of `init.lua`.
