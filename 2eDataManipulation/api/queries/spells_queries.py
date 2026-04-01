from ..db.connection import conn

def get_spell_list_query():
    spell_list = conn.execute(f"SELECT m.name, m.level, LIST(t.tradition) AS traditions, LEFT(d.description, 200) AS description FROM spell_main m JOIN spell_details d ON m.id = d.id LEFT JOIN spell_traditions t ON m.id = t.id GROUP BY m.name, m.level, d.description ORDER BY m.level").fetchdf()
    spell_list["traditions"] = spell_list["traditions"].apply(lambda x: list(x) if x is not None else [])
    return spell_list.to_dict(orient="records")