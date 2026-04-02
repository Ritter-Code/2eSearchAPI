from ..db.connection import conn
from ..utils import df_to_records

def get_feat_list_query():
    feat_list = conn.execute("""
        SELECT m.name, m.level, m.category, m.rarity, m.action_type, m.actions, LIST(DISTINCT t.trait) AS traits
        FROM feat_main m
        LEFT JOIN feat_traits t ON t.id = m.id
        GROUP BY m.name, m.level, m.category, m.rarity, m.action_type, m.actions
        ORDER BY m.level, m.name
    """).fetchdf()
    return df_to_records(feat_list)

def get_feat_filter_query(level_min=None, level_max=None, category=None, rarity=None, trait=None, action_type=None):
    conditions = []
    params = []

    if level_min is not None:
        conditions.append("m.level >= ?")
        params.append(level_min)

    if level_max is not None:
        conditions.append("m.level <= ?")
        params.append(level_max)

    if category is not None:
        conditions.append("LOWER(m.category) = LOWER(?)")
        params.append(category)

    if rarity is not None:
        conditions.append("LOWER(m.rarity) = LOWER(?)")
        params.append(rarity)

    if trait is not None:
        conditions.append("m.id IN (SELECT id FROM feat_traits WHERE LOWER(trait) = LOWER(?))")
        params.append(trait)

    if action_type is not None:
        conditions.append("LOWER(m.action_type) = LOWER(?)")
        params.append(action_type)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    feat_list = conn.execute(f"""
        SELECT m.name, m.level, m.category, m.rarity, m.action_type, m.actions, LIST(DISTINCT t.trait) AS traits
        FROM feat_main m
        LEFT JOIN feat_traits t ON t.id = m.id
        {where_clause}
        GROUP BY m.name, m.level, m.category, m.rarity, m.action_type, m.actions
        ORDER BY m.level, m.name
    """, params).fetchdf()
    return df_to_records(feat_list)

def get_feat_info_query(name):
    feat_info = conn.execute("""
        SELECT
            m.name, m.level, m.category, m.rarity, m.action_type, m.actions,
            d.description,
            (SELECT LIST(trait) FROM feat_traits WHERE id = m.id) AS traits,
            (SELECT LIST(prerequisite) FROM feat_prerequisites WHERE id = m.id) AS prerequisites,
            mt.source, mt.remaster
        FROM feat_main m
        JOIN feat_details d ON d.id = m.id
        JOIN feat_meta mt ON mt.id = m.id
        WHERE LOWER(m.name) = LOWER(?)
    """, [name]).fetchdf()
    if feat_info.empty:
        raise IndexError(f"Feat '{name}' not found")
    return df_to_records(feat_info)[0]
