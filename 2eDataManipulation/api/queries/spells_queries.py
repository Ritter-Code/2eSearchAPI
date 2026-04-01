from ..db.connection import conn
from ..utils import df_to_records

def get_spell_list_query():
    spell_list = conn.execute(f"SELECT m.name, m.level, LIST(DISTINCT t.tradition) AS traditions, LIST(DISTINCT tr.trait) AS traits, LEFT(d.description, 200) AS description FROM spell_main m JOIN spell_details d ON m.id = d.id LEFT JOIN spell_traditions t ON m.id = t.id LEFT JOIN spell_traits tr ON m.id = tr.id GROUP BY m.name, m.level, d.description ORDER BY m.level").fetchdf()
    spell_list["traditions"] = spell_list["traditions"].apply(lambda x: list(x) if x is not None else [])
    spell_list["traits"] = spell_list["traits"].apply(lambda x: list(x) if x is not None else [])
    return df_to_records(spell_list)

def get_spell_info_query(name):

    ##Full Spell Data Query 
    ###Core Spell Info
    spell_core = conn.execute("""
        SELECT
            m.id, m.name, m.level, m.type, m.rarity, d.cast_time, d.cost, d.range, d.area_type, d.area_range, d.targets, d.duration, d.sustained, d.save, d.basic, d.description, LIST(DISTINCT t.trait) AS traits, LIST(DISTINCT tr.tradition) AS traditions
        FROM spell_main m
        JOIN spell_details d ON m.id = d.id
        LEFT JOIN spell_traits t ON t.id = m.id
        LEFT JOIN spell_traditions tr ON tr.id = m.id
        WHERE LOWER(m.name) = LOWER(?)
        GROUP BY m.id, m.name, m.level, m.type, m.rarity, d.cast_time, d.cost, d.range, d.area_type, d.area_range, d.targets, d.duration, d.sustained, d.save, d.basic, d.description
    """, [name]).fetchdf()

    spell_id = spell_core["id"][0]

    spell_damage = conn.execute("""
        SELECT damage_index, damage, damage_type, persistent, mod
        FROM spell_damage
        WHERE id = ?
        ORDER BY damage_index
    """, [spell_id]).fetchdf()

    spell_heightening = conn.execute("""
        SELECT type, interval FROM spell_heightening WHERE id = ?
    """, [spell_id]).fetchdf()

    spell_heighten_interval = conn.execute("""
        SELECT damage_index, damage FROM spell_heighten_interval WHERE id = ?
    """, [spell_id]).fetchdf()

    spell_heighten_levels = conn.execute("""
        SELECT hl.heighten_level, hl.area, hl.range, hl.target,
            LIST(hld.damage) AS damage, LIST(hld.damage_type) AS damage_types
        FROM spell_heighten_level hl
        LEFT JOIN spell_heighten_level_damage hld ON hl.id = hld.id 
            AND hl.heighten_level = hld.heighten_level
        WHERE hl.id = ?
        GROUP BY hl.heighten_level, hl.area, hl.range, hl.target
        ORDER BY hl.heighten_level
    """, [spell_id]).fetchdf()

    result = df_to_records(spell_core)[0]
    result["traits"] = list(result["traits"])
    result["traditions"] = list(result["traditions"])
    result["damage"] = df_to_records(spell_damage)
    result["heightening"] = {
        "type": spell_heightening["type"][0] if len(spell_heightening) else None,
        "interval": int(spell_heightening["interval"][0]) if len(spell_heightening) and spell_heightening["interval"][0] is not None else None,
        "interval_damage": df_to_records(spell_heighten_interval),
        "levels": df_to_records(spell_heighten_levels)
    }
    del result["id"]
    return result

def get_spell_filter_query(level_min, level_max, tradition, trait, action):
    conditions = []
    params = []

    if level_min is not None:
        conditions.append("m.level >= ?")
        params.append(level_min)

    if level_max is not None:
        conditions.append("m.level <= ?")
        params.append(level_max)

    if tradition is not None:
        conditions.append("m.id IN (SELECT id FROM spell_traditions WHERE tradition = ?)")
        params.append(tradition)

    if trait is not None:
        conditions.append("m.id IN (SELECT id FROM spell_traits WHERE trait = ?)")
        params.append(trait)

    if action is not None:
        conditions.append("d.cast_time = ?")
        params.append(action)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    spell_list = conn.execute(f"""
        SELECT m.name, m.level, LIST(DISTINCT t.tradition) AS traditions, LIST(DISTINCT tr.trait) AS traits, LEFT(d.description, 200) AS description
        FROM spell_main m
        JOIN spell_details d ON m.id = d.id
        LEFT JOIN spell_traditions t ON m.id = t.id
        LEFT JOIN spell_traits tr ON m.id = tr.id
        {where_clause}
        GROUP BY m.name, m.level, d.description ORDER BY m.level
    """, params).fetchdf()

    spell_list["traditions"] = spell_list["traditions"].apply(lambda x: list(x) if x is not None else [])
    spell_list["traits"] = spell_list["traits"].apply(lambda x: list(x) if x is not None else [])
    return df_to_records(spell_list)