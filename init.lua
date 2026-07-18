-- Armor Stand with Arms — one mod, multiple games.
--
-- The stand's arm geometry and the hand-display entities are the same
-- everywhere, but armor handling is game-specific: Mineclonia and VoxeLibre
-- use mcl_armor's right-click equip flow (mcl.lua), Minetest Game uses
-- 3d_armor's chest-style formspec inventory (minetest_game.lua). Exactly
-- one of the two files is loaded, picked by which game's armor-stand mod is
-- present.

local modpath = core.get_modpath(core.get_current_modname())

if core.get_modpath("mcl_armor_stand") then
	-- Mineclonia or VoxeLibre (told apart further inside mcl.lua)
	dofile(modpath .. "/mcl.lua")
elseif core.get_modpath("3d_armor_stand") then
	-- Minetest Game with the 3d_armor modpack
	dofile(modpath .. "/minetest_game.lua")
elseif core.get_modpath("default") then
	error("armor_stand_arms: on Minetest Game this mod needs the 3d_armor " ..
		"modpack (including its 3d_armor_stand mod) installed and enabled.")
else
	error("armor_stand_arms: unsupported game. This mod supports " ..
		"Mineclonia, VoxeLibre and Minetest Game (with 3d_armor).")
end
