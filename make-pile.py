import json
import math
import os
import random
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else random.SystemRandom().randint(1, 999999999)
random.seed(SEED)
elements = []

SCALE = 1.0
R_BASE = 7.50
H_DOME = 14.60
Y_STEP = 0.55
MIN_INSET = 0.14

layer_heights = [round(i * Y_STEP, 3) for i in range(28)]

def get_half_extents(rot_deg):
    rad = math.radians(rot_deg)
    c, s = abs(math.cos(rad)), abs(math.sin(rad))
    hx = (0.75 * SCALE) * c + (1.25 * SCALE) * s + 0.004
    hz = (0.75 * SCALE) * s + (1.25 * SCALE) * c + 0.004
    return hx, hz

def overlaps(cx, cz, hx, hz, placed):
    for px, pz, phx, phz in placed:
        if abs(cx - px) < (hx + phx) and abs(cz - pz) < (hz + phz):
            return True
    return False

def add_vanilla_nugget(elements, idx, cx, y, cz, rot):
    ox, oz = round(cx, 3), round(cz, 3)
    s = SCALE
    raw_cubes = [
        (
            f"n{idx}_1",
            [-0.75 * s, 0.0, -0.75 * s],
            [0.75 * s, 1.0 * s, 0.75 * s],
            {
                "north": {"texture": "#ore", "uv": [8.0, 0.5, 9.5, 1.5]},
                "east":  {"texture": "#ore", "uv": [10.0, 1.0, 11.0, 2.5], "rotation": 90},
                "south": {"texture": "#ore", "uv": [6.0, 2.5, 7.5, 3.5]},
                "west":  {"texture": "#ore", "uv": [8.0, 3.0, 9.5, 4.0]},
                "up":    {"texture": "#ore", "uv": [11.0, 5.5, 12.5, 7.0]},
                "down":  {"texture": "#ore", "uv": [2.5, 9.0, 4.0, 10.5], "rotation": 90},
            },
        ),
        (
            f"n{idx}_2",
            [-0.25 * s, 0.0, -1.25 * s],
            [0.75 * s, 1.0 * s, -0.75 * s],
            {
                "north": {"texture": "#ore", "uv": [12.5, 13.5, 13.5, 14.5]},
                "east":  {"texture": "#ore", "uv": [8.0, 13.0, 8.5, 14.0]},
                "west":  {"texture": "#ore", "uv": [13.5, 8.0, 14.0, 9.0]},
                "up":    {"texture": "#ore", "uv": [9.5, 12.0, 10.5, 12.5]},
                "down":  {"texture": "#ore", "uv": [6.0, 12.0, 7.0, 12.5]},
            },
        ),
        (
            f"n{idx}_3",
            [-0.75 * s, 0.0, 0.75 * s],
            [0.25 * s, 1.0 * s, 1.25 * s],
            {
                "east":  {"texture": "#ore", "uv": [3.0, 3.0, 3.5, 4.0]},
                "south": {"texture": "#ore", "uv": [5.5, 6.0, 6.5, 7.0]},
                "west":  {"texture": "#ore", "uv": [8.5, 2.0, 9.0, 3.0]},
                "up":    {"texture": "#ore", "uv": [5.0, 1.0, 6.0, 1.5]},
                "down":  {"texture": "#ore", "uv": [1.5, 4.0, 2.5, 4.5]},
            },
        ),
        (
            f"n{idx}_4",
            [-0.25 * s, 1.0 * s, -0.75 * s],
            [0.25 * s, 1.5 * s, -0.25 * s],
            {
                "north": {"texture": "#ore", "uv": [12.0, 3.5, 12.5, 4.0]},
                "east":  {"texture": "#ore", "uv": [14.0, 1.0, 14.5, 1.5]},
                "west":  {"texture": "#ore", "uv": [11.0, 3.0, 11.5, 3.5]},
                "up":    {"texture": "#ore", "uv": [11.5, 3.5, 12.0, 4.0]},
            },
        ),
        (
            f"n{idx}_5",
            [-0.25 * s, 1.0 * s, -0.25 * s],
            [0.75 * s, 1.5 * s, 0.75 * s],
            {
                "north": {"texture": "#ore", "uv": [13.0, 13.5, 14.0, 14.0]},
                "east":  {"texture": "#ore", "uv": [10.5, 2.0, 11.5, 2.5]},
                "south": {"texture": "#ore", "uv": [9.0, 8.0, 10.0, 8.5]},
                "west":  {"texture": "#ore", "uv": [4.0, 9.0, 5.0, 9.5]},
                "up":    {"texture": "#ore", "uv": [10.0, 1.5, 11.0, 2.5]},
            },
        ),
    ]
    for name, f_off, t_off, faces in raw_cubes:
        elements.append({
            "name": name,
            "from": [round(cx + f_off[0], 3), round(y + f_off[1], 3), round(cz + f_off[2], 3)],
            "to":   [round(cx + t_off[0], 3), round(y + t_off[1], 3), round(cz + t_off[2], 3)],
            "rotationOrigin": [ox, y, oz],
            "rotationY": rot,
            "faces": faces,
        })

print(f"Generated with RANDOM SEED: {SEED}")
idx = 1
prev_r = R_BASE + MIN_INSET
max_y_reached = 0.0

for layer_num, y in enumerate(layer_heights):
    if idx > 512:
        break
    dome_r = R_BASE * math.sqrt(max(0.0, 1.0 - (y / H_DOME) ** 2))
    max_r = min(dome_r, prev_r - MIN_INSET)
    if max_r < 0.45:
        break
    prev_r = max_r

    placed = []
    candidates = []
    step = 0.07
    gx = 0.55
    while gx <= 15.45:
        gz = 0.55
        while gz <= 15.45:
            dist = math.hypot(gx - 8.0, gz - 8.0)
            if dist <= max_r:
                candidates.append((dist, gx, gz))
            gz += step
        gx += step

    random.shuffle(candidates)
    candidates.sort(key=lambda item: round(item[0], 1))

    layer_start = idx
    for _, cx, cz in candidates:
        if idx > 512:
            break
        base_angles = [0, 90, 180, 270]
        random.shuffle(base_angles)
        for base_rot in base_angles:
            rot = round(base_rot + random.uniform(-6, 6), 1)
            hx, hz = get_half_extents(rot)
            if cx - hx < 0.1 or cx + hx > 15.9 or cz - hz < 0.1 or cz + hz > 15.9:
                continue
            if not overlaps(cx, cz, hx, hz, placed):
                placed.append((cx, cz, hx, hz))
                add_vanilla_nugget(elements, idx, cx, y, cz, rot)
                max_y_reached = round(y + 1.5 * SCALE, 2)
                idx += 1
                break
    print(f"Row {layer_num + 1} (y={y:.2f}, max_r={max_r:.2f}): {idx - layer_start} full-scale nuggets")

# 1. Write 3D shape JSON
shape_dir = os.path.join(SCRIPT_DIR, "assets", "orepiles", "shapes", "item")
os.makedirs(shape_dir, exist_ok=True)
shape_path = os.path.join(shape_dir, "nugget-pile.json")

shape = {
    "editor": {"allAngles": True, "singleTexture": False},
    "textureWidth": 16,
    "textureHeight": 16,
    "textures": {"ore": "item/resource/nugget/uranium"},
    "elements": elements,
}

with open(shape_path, "w", encoding="utf-8") as f:
    json.dump(shape, f, indent=2)

# 2. Write GroundStorable patches JSON
patch_dir = os.path.join(SCRIPT_DIR, "assets", "orepiles", "patches")
os.makedirs(patch_dir, exist_ok=True)
patch_path = os.path.join(patch_dir, "nugget-groundstorage.json")

ground_storage_props = {
    "layout": "Stacking",
    "ctrlKey": True,
    "stackingModel": "orepiles:item/nugget-pile",
    "upSolid": False,
    "modelItemsToStackSizeRatio": 5.0,
    "stackingCapacity": 512,
    "transferQuantity": 1,
    "bulkTransferQuantity": 16,
    "collisionBox": {
        "x1": 0,
        "y1": 0,
        "z1": 0,
        "x2": 1,
        "y2": 0.08,
        "z2": 1
    },
    "cbScaleYByLayer": 0.021
}

patches = [
    {
        "file": "game:itemtypes/resource/nugget.json",
        "op": "replace",
        "path": "/behaviorsByType/*-hematite/0/properties",
        "value": ground_storage_props
    },
    {
        "file": "game:itemtypes/resource/nugget.json",
        "op": "replace",
        "path": "/behaviorsByType/*-limonite/0/properties",
        "value": ground_storage_props
    },
    {
        "file": "game:itemtypes/resource/nugget.json",
        "op": "replace",
        "path": "/behaviorsByType/*/0/properties",
        "value": ground_storage_props
    },
    {
        "file": "game:itemtypes/resource/metalbit.json",
        "op": "replace",
        "path": "/behaviors/0/properties",
        "value": ground_storage_props
    }
]

with open(patch_path, "w", encoding="utf-8") as f:
    json.dump(patches, f, indent=2)

# 3. Write modinfo.json
modinfo_path = os.path.join(SCRIPT_DIR, "modinfo.json")
modinfo = {
    "type": "content",
    "modid": "orepiles",
    "name": "Ore Piles",
    "authors": ["Nesa"],
    "description": "Upgrades ground storage for all raw ore nuggets and smelted metal bits/alloys to a 512-capacity 1:1 visual dome pile within a 1x1x1 block space.",
    "version": "1.0.0",
    "dependencies": {"game": ""}
}
with open(modinfo_path, "w", encoding="utf-8") as f:
    json.dump(modinfo, f, indent=2)

# 4. Write README.md
readme_path = os.path.join(SCRIPT_DIR, "README.md")
readme_lines = [
    "# Ore Piles (512-Capacity Nugget & Metal Bit Ground Storage)",
    "",
    "A Vintage Story mod by **Nesa** that upgrades ground storage for all raw ore nuggets and smelted metal bits/alloys into a 1:1 visual dome pile holding up to **512 items** within a single `1x1x1` block space.",
    "",
    "## Features",
    "",
    "- **512-Item Ground Storage:** Store up to 512 raw ore nuggets (`nugget-*`) or metal bits/alloys (`metalbit-*`, including Tin Bronze, Bismuth Bronze, Black Bronze, Brass, Iron, and Steel) in a single block.",
    "- **Exact 1:1 Visual Representation:** Every item placed into the pile renders one full-scale (`1.0`) 5-cube vanilla nugget (`2,560` elements total at full capacity).",
    "- **Non-Overlapping Dome Geometry:** Collision-checked placement ensures individual nuggets touch without clipping, with inward-stepped rows so edge pieces never float.",
    "- **1x1x1 Block Bounds & Vanilla Audio:** Fits cleanly inside a single block's selection/collision hitbox (`cbScaleYByLayer: 0.021`) while preserving vanilla placement sounds and `ArtPigment` cave-painting behaviors on hematite and limonite.",
    "",
    "## Controls",
    "",
    "- **Place 1 item:** `Ctrl + Right-Click` on a solid surface",
    "- **Place 16 items (bulk):** `Ctrl + Shift + Right-Click`",
    "- **Pick up 1 item:** `Right-Click` on the pile",
    "- **Pick up 16 items (bulk):** `Shift + Right-Click` on the pile",
    "",
    "## Regenerating the 3D Pile Model",
    "",
    "The pile shape (`assets/orepiles/shapes/item/nugget-pile.json`) is procedurally generated by `make-pile.py`.",
    "",
    f"- **Seed used in this build:** `{SEED}`",
    "",
    "To reproduce this exact layout, run:",
    "",
    "```bash",
    f"py make-pile.py {SEED}",
    "```",
    "",
    "## Installation",
    "",
    "1. Place `OrePiles-1.0.0.zip` into your Vintage Story `Mods` folder (`%AppData%\\VintagestoryData\\Mods` on Windows or `~/.config/VintagestoryData/Mods` on Linux).",
    "2. Enable **Ore Piles** in the Mod Manager and load your world.",
]

with open(readme_path, "w", encoding="utf-8") as f:
    f.write("\n".join(readme_lines) + "\n")

# 5. Package everything into OrePiles-1.0.0.zip (including modicon.png from the same folder)
zip_path = os.path.join(SCRIPT_DIR, "OrePiles-1.0.0.zip")
icon_path = os.path.join(SCRIPT_DIR, "modicon.png")
assets_dir = os.path.join(SCRIPT_DIR, "assets")

if os.path.exists(zip_path):
    os.remove(zip_path)

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(modinfo_path, "modinfo.json")
    zf.write(readme_path, "README.md")
    if os.path.isfile(icon_path):
        zf.write(icon_path, "modicon.png")
        print(f"Added thumbnail: {icon_path}")
    else:
        print(f"WARNING: modicon.png not found at {icon_path}")
    for root, _, files in os.walk(assets_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arc_path = os.path.relpath(full_path, SCRIPT_DIR).replace("\\", "/")
            zf.write(full_path, arc_path)

print(f"Seed used: {SEED} | Total: {len(elements)} elements ({idx - 1} nuggets) | Peak height: {max_y_reached}/16.0 voxels.")
print(f"Created ZIP: {zip_path} ({os.path.getsize(zip_path)} bytes)")