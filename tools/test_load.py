#!/usr/bin/env python3
"""Stub-execute init.lua under lupa (no lua on PATH; Luanti not launched).

Stubs enough of the Luanti + Mineclonia API to load the mod and exercise:
place, put weapon in hand, take weapon back, armor routing, screwdriver
rotate, dig drops, and the LBM respawn. Run: python3 tools/test_load.py
"""
import os
from lupa import LuaRuntime

HERE = os.path.dirname(os.path.abspath(__file__))
INIT = os.path.join(HERE, "..", "init.lua")

HARNESS = r"""
local checks = {}
local function check(name, cond)
    checks[#checks+1] = {name, cond and true or false}
    if not cond then error("CHECK FAILED: " .. name, 2) end
end

-- ========== vector ==========
local vmeta
local function vnew(x, y, z)
    return setmetatable({x=x, y=y, z=z}, vmeta)
end
vmeta = {
    __add = function(a, b) return vnew(a.x+b.x, a.y+b.y, a.z+b.z) end,
    __sub = function(a, b) return vnew(a.x-b.x, a.y-b.y, a.z-b.z) end,
    __mul = function(a, s) return vnew(a.x*s, a.y*s, a.z*s) end,
    __index = {},
}
vector = {
    new = function(x, y, z)
        if type(x) == "table" then return vnew(x.x, x.y, x.z) end
        return vnew(x or 0, y or 0, z or 0)
    end,
    add = function(a, b) return vnew(a.x+b.x, a.y+b.y, a.z+b.z) end,
    offset = function(v, x, y, z) return vnew(v.x+x, v.y+y, v.z+z) end,
    round = function(v)
        return vnew(math.floor(v.x+0.5), math.floor(v.y+0.5), math.floor(v.z+0.5))
    end,
    equals = function(a, b) return a.x==b.x and a.y==b.y and a.z==b.z end,
    distance = function(a, b)
        local dx, dy, dz = a.x-b.x, a.y-b.y, a.z-b.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    end,
    rotate = function(v, rot)
        -- y-rotation only (all the mod uses)
        local c, s = math.cos(rot.y), math.sin(rot.y)
        return vnew(v.x*c - v.z*s, v.y, v.x*s + v.z*c)
    end,
}

-- ========== ItemStack ==========
local registered_items = {
    ["mcl_tools:sword_iron"] = {groups = {weapon = 1, sword = 1}},
    ["mcl_shields:shield"] = {groups = {shield = 1, weapon = 2}},
    ["mcl_armor:helmet_iron"] = {_mcl_armor_element = "head"},
    ["mcl_core:apple"] = {groups = {food = 2}},
}
local StackMeta
local function ItemStack(init)
    local name, count = "", 0
    if type(init) == "table" then
        name, count = init.name or "", init.count or 0
    elseif type(init) == "string" and init ~= "" then
        name = init:match("^(%S+)")
        count = tonumber(init:match("%s(%d+)")) or 1
    end
    return setmetatable({_name = name, _count = count}, StackMeta)
end
StackMeta = {__index = {
    get_name = function(self) return self._name end,
    get_count = function(self) return self._count end,
    is_empty = function(self) return self._name == "" or self._count == 0 end,
    get_definition = function(self) return registered_items[self._name] end,
    take_item = function(self, n)
        n = math.min(n or 1, self._count)
        self._count = self._count - n
        local taken = ItemStack({name = self._name, count = n})
        if self._count == 0 then self._name = "" end
        return taken
    end,
    copy = function(self) return ItemStack({name = self._name, count = self._count}) end,
}}
_G.ItemStack = ItemStack

-- ========== inventory / meta ==========
local function Inventory()
    local lists = {}
    return {
        set_size = function(_, listname, size)
            lists[listname] = lists[listname] or {}
            for i = 1, size do
                lists[listname][i] = lists[listname][i] or ItemStack()
            end
        end,
        get_size = function(_, listname)
            return lists[listname] and #lists[listname] or 0
        end,
        get_stack = function(_, listname, i)
            return (lists[listname] and lists[listname][i] or ItemStack()):copy()
        end,
        set_stack = function(_, listname, i, stack)
            if type(stack) ~= "table" then stack = ItemStack(stack) end
            lists[listname][i] = stack:copy()
        end,
        get_list = function(_, listname) return lists[listname] end,
        get_lists = function(_) return lists end,
    }
end

-- ========== world state ==========
local nodes = {}       -- "x,y,z" -> node table
local metas = {}       -- "x,y,z" -> meta
local objects = {}     -- live entity objects
local drops = {}       -- itemstrings dropped via core.add_item
local function poskey(p) return p.x .. "," .. p.y .. "," .. p.z end

local registered_nodes, registered_entities, registered_lbms, registered_crafts = {}, {}, {}, {}

local face_pos_y = 0.5 -- what pointed_thing_to_face_pos reports (test-tunable)

core = {
    get_current_modname = function() return "armor_stand_arms" end,
    get_translator = function() return function(s) return s end end,
    register_node = function(name, def) registered_nodes[name] = def end,
    register_entity = function(name, def) registered_entities[name] = def end,
    register_lbm = function(def) registered_lbms[#registered_lbms+1] = def end,
    register_craft = function(def) registered_crafts[#registered_crafts+1] = def end,
    get_node = function(pos)
        return nodes[poskey(vector.round(pos))] or {name = "air", param2 = 0}
    end,
    swap_node = function(pos, node) nodes[poskey(vector.round(pos))] = node end,
    get_meta = function(pos)
        local k = poskey(vector.round(pos))
        if not metas[k] then metas[k] = {inv = Inventory()} end
        local m = metas[k]
        return {get_inventory = function() return m.inv end}
    end,
    is_protected = function() return false end,
    record_protection_violation = function() end,
    facedir_to_dir = function(fd)
        local dirs = {
            [0] = vnew(0, 0, 1), [1] = vnew(1, 0, 0),
            [2] = vnew(0, 0, -1), [3] = vnew(-1, 0, 0),
        }
        return dirs[fd % 4]
    end,
    dir_to_yaw = function(dir) return math.atan(-dir.x, dir.z) end,
    pointed_thing_to_face_pos = function(clicker, pt)
        return vnew(pt.above.x, pt.under.y + face_pos_y, pt.above.z)
    end,
    pos_to_string = function(p) return "(" .. p.x .. "," .. p.y .. "," .. p.z .. ")" end,
    string_to_pos = function(s)
        local x, y, z = s:match("%((%-?%d+),(%-?%d+),(%-?%d+)%)")
        if x then return vnew(tonumber(x), tonumber(y), tonumber(z)) end
    end,
    objects_inside_radius = function(pos, radius)
        local found, i = {}, 0
        for _, obj in ipairs(objects) do
            if not obj._removed and vector.distance(obj._pos, pos) <= radius + 1e-9 then
                found[#found+1] = obj
            end
        end
        return function()
            i = i + 1
            return found[i]
        end
    end,
    add_entity = function(pos, name, staticdata)
        local def = registered_entities[name]
        if not def then error("no such entity " .. name) end
        local obj
        obj = {
            _pos = vnew(pos.x, pos.y, pos.z),
            _removed = false,
            _properties = {},
            _rotation = vnew(0, 0, 0),
            is_player = function() return false end,
            get_pos = function(self) return self._pos end,
            set_pos = function(self, p) self._pos = vnew(p.x, p.y, p.z) end,
            set_yaw = function(self, yaw) self._rotation = vnew(0, yaw, 0) end,
            set_rotation = function(self, r) self._rotation = vnew(r.x, r.y, r.z) end,
            set_properties = function(self, props)
                for k, v in pairs(props) do self._properties[k] = v end
            end,
            set_armor_groups = function() end,
            remove = function(self) self._removed = true end,
        }
        local luaentity = setmetatable({object = obj, name = name}, {__index = def})
        obj.get_luaentity = function() return luaentity end
        objects[#objects+1] = obj
        if def.on_activate then luaentity:on_activate(staticdata or "") end
        return obj
    end,
    add_item = function(pos, stack)
        if type(stack) == "string" then stack = ItemStack(stack) end
        if stack and not stack:is_empty() then
            drops[#drops+1] = stack:get_name() .. " " .. stack:get_count()
        end
    end,
    log = function() end,
}

-- ========== game stubs (VoxeLibre-minimal surface) ==========
-- NOTE: this mock exposes only the SMALLER (VoxeLibre) mcl_armor / mcl_util
-- surface -- no has_piece, unequip, head_entity_equip/unequip,
-- drop_item_stack or float_random. If init.lua loads and every scenario
-- passes against this, it is compatible with both VoxeLibre and Mineclonia
-- (whose API is a superset).
local armor_calls = {}
mcl_armor = {
    elements = {
        head = {index = 2}, torso = {index = 3},
        legs = {index = 4}, feet = {index = 5},
    },
    equip = function(itemstack, obj, swap)
        armor_calls[#armor_calls+1] = "equip:" .. itemstack:get_name()
        return ItemStack()
    end,
    on_unequip = function(itemstack, obj)
        armor_calls[#armor_calls+1] = "unequip:" .. itemstack:get_name()
    end,
    update = function() end,
}
mcl_util = {}
mcl_sounds = {node_sound_wood_defaults = function() return {} end}
screwdriver = {ROTATE_FACE = 1, ROTATE_AXIS = 2}

-- ========== load the mod ==========
dofile(INIT_PATH)

local NODE = "armor_stand_arms:armor_stand"
local nodedef = registered_nodes[NODE]
check("node registered", nodedef ~= nil)
check("armor entity registered", registered_entities["armor_stand_arms:armor_entity"] ~= nil)
check("item entity registered", registered_entities["armor_stand_arms:item_entity"] ~= nil)
check("craft registered", #registered_crafts == 1)
check("recipe is 7 sticks + slab", (function()
    local r = registered_crafts[1].recipe
    local sticks, slabs = 0, 0
    for _, row in ipairs(r) do
        for _, it in ipairs(row) do
            if it == "mcl_core:stick" then sticks = sticks + 1 end
            if it == "mcl_stairs:slab_stone" then slabs = slabs + 1 end
        end
    end
    return sticks == 8 and slabs == 1
end)())
check("mesh is armor_stand_arms.obj", nodedef.mesh == "armor_stand_arms.obj")

-- place the stand at (10, 5, 10), facing param2 = 0
local pos = vnew(10, 5, 10)
nodes[poskey(pos)] = {name = NODE, param2 = 0}
nodedef.on_construct(pos)
local function live(name)
    local n = 0
    for _, o in ipairs(objects) do
        if not o._removed and o:get_luaentity().name == name then n = n + 1 end
    end
    return n
end
check("stand entity spawned on construct", live("armor_stand_arms:armor_entity") == 1)
check("no item entity while hands empty", live("armor_stand_arms:item_entity") == 0)

local player = {
    is_player = function() return true end,
    get_player_name = function() return "nando" end,
    _wielded = ItemStack(),
    get_wielded_item = function(self) return self._wielded:copy() end,
}
local node = nodes[poskey(pos)]
local pt = {type = "node", under = pos, above = vnew(10, 5, 11)} -- side face

local function item_entity_for(slot)
    for _, o in ipairs(objects) do
        local le = o:get_luaentity()
        if not o._removed and le.name == "armor_stand_arms:item_entity" and le.slot == slot then
            return o
        end
    end
end

-- 1. right-click with a sword -> goes into the main hand
player._wielded = ItemStack("mcl_tools:sword_iron")
local ret = nodedef.on_rightclick(pos, node, player, ItemStack("mcl_tools:sword_iron"), pt)
local inv = core.get_meta(pos):get_inventory()
check("sword stored in hand slot", inv:get_stack("hand", 1):get_name() == "mcl_tools:sword_iron")
check("empty stack returned", ret:is_empty())
check("one item entity spawned", live("armor_stand_arms:item_entity") == 1)
local sword_obj = item_entity_for("main")
check("weapon entity is in the main slot", sword_obj ~= nil)
check("item entity shows the sword", sword_obj._properties.textures[1] == "mcl_tools:sword_iron")
check("item entity off node center", vector.distance(sword_obj._pos, pos) > 0.2)
check("item entity x offset rounds home", math.abs(sword_obj._pos.x - pos.x) < 0.5)
check("item entity z offset rounds home", math.abs(sword_obj._pos.z - pos.z) < 0.5)
-- simulate an activation without staticdata at the item's current position
local orphan = core.add_entity(sword_obj._pos, "armor_stand_arms:item_entity")
check("staticdata-less activation finds its node",
    vector.equals(orphan:get_luaentity().node_pos, pos))
orphan:remove()

-- 2. non-weapon (apple) is REJECTED: hand keeps the sword, apple returned
player._wielded = ItemStack("mcl_core:apple")
ret = nodedef.on_rightclick(pos, node, player, ItemStack("mcl_core:apple"), pt)
check("apple rejected (returned unchanged)", ret:get_name() == "mcl_core:apple")
check("hand still holds the sword", inv:get_stack("hand", 1):get_name() == "mcl_tools:sword_iron")

-- 3. shield -> goes into the OFF hand, second entity spawns
player._wielded = ItemStack("mcl_shields:shield")
ret = nodedef.on_rightclick(pos, node, player, ItemStack("mcl_shields:shield"), pt)
check("shield stored in offhand slot", inv:get_stack("offhand", 1):get_name() == "mcl_shields:shield")
check("shield returns empty", ret:is_empty())
check("two item entities now", live("armor_stand_arms:item_entity") == 2)
local shield_obj = item_entity_for("off")
check("shield entity is in the off slot", shield_obj ~= nil)
check("shield entity shows the shield", shield_obj._properties.textures[1] == "mcl_shields:shield")
check("weapon and shield on opposite arms (mirrored x)",
    (sword_obj._pos.x - pos.x) * (shield_obj._pos.x - pos.x) < 0)

-- 4. screwdriver rotate moves BOTH item entities
local old_sword = vnew(sword_obj._pos.x, sword_obj._pos.y, sword_obj._pos.z)
local old_shield = vnew(shield_obj._pos.x, shield_obj._pos.y, shield_obj._pos.z)
check("on_rotate handled", nodedef.on_rotate(pos, {name = NODE, param2 = 0}, nil, screwdriver.ROTATE_FACE) == true)
node = nodes[poskey(pos)]
check("param2 rotated", node.param2 == 1)
check("weapon moved with rotation", not vector.equals(sword_obj._pos, old_sword))
check("shield moved with rotation", not vector.equals(shield_obj._pos, old_shield))

-- 5. empty hand at bare torso height -> takes WEAPON first
player._wielded = ItemStack()
face_pos_y = 0.5 -- torso band, no armor there
ret = nodedef.on_rightclick(pos, node, player, ItemStack(), pt)
check("took weapon first", ret:get_name() == "mcl_tools:sword_iron")
check("hand slot empty again", inv:get_stack("hand", 1):is_empty())
check("weapon entity removed, shield remains", live("armor_stand_arms:item_entity") == 1)

-- 6. empty hand again -> takes the SHIELD next
ret = nodedef.on_rightclick(pos, node, player, ItemStack(), pt)
check("took shield next", ret:get_name() == "mcl_shields:shield")
check("offhand slot empty again", inv:get_stack("offhand", 1):is_empty())
check("all item entities removed", live("armor_stand_arms:item_entity") == 0)

-- 7. empty hand over a torso piece -> unequips it via mcl_armor.on_unequip
inv:set_stack("armor", 3, ItemStack("mcl_armor:helmet_iron")) -- torso index = 3
armor_calls = {}
ret = nodedef.on_rightclick(pos, node, player, ItemStack(), pt)
check("took the armor piece", ret:get_name() == "mcl_armor:helmet_iron")
check("armor slot cleared", inv:get_stack("armor", 3):is_empty())
check("on_unequip fired", armor_calls[1] == "unequip:mcl_armor:helmet_iron")

-- 8. helmet routes to mcl_armor.equip
armor_calls = {}
player._wielded = ItemStack("mcl_armor:helmet_iron")
ret = nodedef.on_rightclick(pos, node, player, ItemStack("mcl_armor:helmet_iron"), pt)
check("helmet routed to mcl_armor.equip", armor_calls[1] == "equip:mcl_armor:helmet_iron")

-- 9. LBM respawn: wipe entities, run action, both hands refilled
inv:set_stack("hand", 1, ItemStack("mcl_tools:sword_iron"))
inv:set_stack("offhand", 1, ItemStack("mcl_shields:shield"))
for _, o in ipairs(objects) do o._removed = true end
registered_lbms[1].action(pos, node)
check("LBM respawns stand entity", live("armor_stand_arms:armor_entity") == 1)
check("LBM respawns both item entities", live("armor_stand_arms:item_entity") == 2)

-- 10. dig: drops armor + weapon + shield
inv:set_stack("armor", 2, ItemStack("mcl_armor:helmet_iron"))
nodedef.on_destruct(pos)
local dropped = table.concat(drops, ";")
check("drops include weapon", dropped:match("sword_iron") ~= nil)
check("drops include shield", dropped:match("shield") ~= nil)
check("drops include armor", dropped:match("helmet_iron") ~= nil)
check("all item entities removed on destruct", live("armor_stand_arms:item_entity") == 0)

return #checks
"""


def main():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals()["INIT_PATH"] = os.path.abspath(INIT)
    n = lua.execute(HARNESS)
    print("OK: %d checks passed" % n)


if __name__ == "__main__":
    main()
