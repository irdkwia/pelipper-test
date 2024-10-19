from structure.database import *


def format_floor(db, dungeon_id, floor):
    dng = db.get_elements(DungeonData, {"did": dungeon_id}, limit=1)
    if len(dng) > 0:
        dungeon = dng[0].name
        direction = dng[0].direction
    else:
        dungeon = f"Unknown dungeon #{dungeon_id}"
        direction = DIR_DOWN

    if direction == DIR_UP:
        return f"{dungeon} {floor}F"
    else:
        return f"{dungeon} B{floor}F"


def format_rescue_code(rid):
    rid_str = f"{rid:012d}"
    return f"{rid_str[:4]}-{rid_str[4:8]}-{rid_str[8:]}"
