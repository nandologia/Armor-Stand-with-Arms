# Armor Stand with Arms

An armor stand that has **arms** — so it can show off your armor **and** hold
a **weapon** in one hand and a **shield** in the other. A mod for
[Mineclonia](https://content.luanti.org/packages/ryvnf/mineclonia/) and
[VoxeLibre](https://content.luanti.org/packages/Wuzzy/mineclone2/) (formerly
MineClone2).

> **Playing Minetest Game instead?** This version won't load there — get the
> separate **Armor Stand with Arms (Minetest Game)** mod
> (`armor_stand_arms_minetest`), built for Minetest Game with the 3d_armor
> mod.

It works just like the normal armor stand you already know, but now your
gear has somewhere to pose. Set up a knight by the door, show off your best
sword, or build a little armory room where every stand holds a different
weapon.

## How to craft it

Put **8 sticks** around a **smooth stone slab** in the crafting table:

```
Stick   Stick   Stick
Stick   Stick   Stick
Stick   Slab    Stick
```

The slab is the same one used to craft the normal armor stand — the "Smooth
Stone Slab" in Mineclonia, or the "Polished Stone Slab" in VoxeLibre. In
short: this is the normal armor stand recipe, plus extra sticks down the
sides to make the arms.

## How to use it

- **Put armor on it** — hold a helmet, chestplate, leggings, or boots and
  use them on the stand, exactly like the normal armor stand.
- **Give it a weapon** — hold a melee weapon (sword, mace, or trident in MCL; sword, hammer, or trident in VL)
  and use it on the stand. The weapon appears in its right hand.
- **Give it a shield** — hold a shield and use it on the stand. The shield
  appears on its other arm. (Only regular shield supported. Planned update: support for shields customized with banners)
- **Take things back** — with an empty hand, use the place key on the stand.
  Aim at the weapon or the shield to take it, or at a piece of armor to
  take that piece.
- **Turn it** — use a screwdriver to rotate the stand; the weapon and shield
  turn with it.
- Break the stand and everything it was holding drops on the ground.

## Requirements

Made for **Mineclonia** and **VoxeLibre**. It uses the game's own armor
stand mod (`mcl_armor_stand`) for the body model, which both games include
by default, so there is nothing extra to install.

## Credits & license

This mod is based on the built-in armor stand by **Stuart Jones**
(stujones11) that ships with both Mineclonia and VoxeLibre. The stand model
and icon are extended versions of that mod's originals.

- Code: **LGPL 2.1 or later**
- Models & textures: **CC BY-SA 3.0**

See [LICENSE.txt](LICENSE.txt) for the full details.

---

### For modders

The extra arms on the model and the inventory icon are generated from the
game's own armor stand art by the scripts in `tools/`, so they always match
it (the stand model is the same in Mineclonia and VoxeLibre):

- `tools/gen_mesh.py` — adds the two arms to Mineclonia's armor stand model.
- `tools/gen_icon.py` — adds the arms to Mineclonia's stand icon.
- `tools/gen_shield_texture.py` — copies Mineclonia's flat shield icon,
  used in place of VoxeLibre's own shield icon (which is drawn at an angle
  and looks skewed when shown flat on the stand's arm).
- `tools/test_load.py` — loads `init.lua` under a stub API (via `lupa`) and
  checks the placing/taking/rotating/dropping logic without launching the
  game.

Re-run the `gen_*` scripts after a Mineclonia update if the game ever
changes its armor stand model, icon, or shield icon. The weapon and shield
positions live in the `HANDS` table at the top of `init.lua`.
