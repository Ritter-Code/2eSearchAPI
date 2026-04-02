from ..db.connection import conn
from ..utils import df_to_records

def get_ancestry_list_query():
    ancestry_list = conn.execute(f"""
        SELECT name, rarity, hp, size, LEFT(description, 200) AS description
        FROM ancestry_main
        GROUP BY name, rarity, description, hp, size
        ORDER BY CASE rarity
        WHEN 'common' THEN 1
        WHEN 'uncommon' THEN 2
        WHEN 'rare' THEN 3
        ELSE 4
        END, name
    """).fetchdf()
    return df_to_records(ancestry_list)

def get_ancestry_filter_query(rarity=None, hp=None, size=None, boost=None):
    params = []

    rarity_clause = "AND LOWER(m.rarity) = LOWER(?)" if rarity else ""
    if rarity:
        params.append(rarity)

    hp_clause = "AND m.hp = ?" if hp is not None else ""
    if hp is not None:
        params.append(hp)

    size_clause = "AND LOWER(m.size) = LOWER(?)" if size else ""
    if size:
        params.append(size)

    boost_clause = "AND EXISTS (SELECT 1 FROM ancestry_boosts WHERE id = m.id AND LOWER(stat) = LOWER(?))" if boost else ""
    if boost:
        params.append(boost)

    ancestry_filter = conn.execute(f"""
        SELECT m.name, m.rarity, m.hp, m.size, LEFT(m.description, 200) AS description
        FROM ancestry_main m
        WHERE 1=1
        {rarity_clause}
        {hp_clause}
        {size_clause}
        {boost_clause}
        ORDER BY CASE m.rarity
        WHEN 'common' THEN 1
        WHEN 'uncommon' THEN 2
        WHEN 'rare' THEN 3
        ELSE 4
        END, m.name
    """, params).fetchdf()
    return df_to_records(ancestry_filter)

def get_ancestry_info_query(name):
    ancestry_info = conn.execute("""
        SELECT
            m.name, m.rarity, m.hp, m.description, m.size, m.reach, m.speed, m.vision,
            (SELECT LIST(stat) FROM ancestry_boosts WHERE id = m.id) AS boosts,
            (SELECT LIST(flaw) FROM ancestry_flaw WHERE id = m.id) AS flaw,
            (SELECT LIST(trait) FROM ancestry_traits WHERE id = m.id) AS traits,
            (SELECT LIST(language) FROM ancestry_languages WHERE id = m.id) AS languages,
            (SELECT LIST(language) FROM ancestry_additional_languages WHERE id = m.id) AS additional_languages,
            (SELECT LIST(feature) FROM ancestry_race_features WHERE id = m.id) AS race_features
        FROM ancestry_main m
        WHERE LOWER(m.name) = LOWER(?)
    """, [name]).fetchdf()
    return df_to_records(ancestry_info)[0]