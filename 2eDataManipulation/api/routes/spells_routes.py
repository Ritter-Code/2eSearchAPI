from fastapi import APIRouter, HTTPException
from ..db.connection import conn
from ..queries.spells_queries import get_spell_list_query
from ..queries.spells_queries import get_spell_info_query
from ..queries.spells_queries import get_spell_filter_query

route = APIRouter(prefix="/spells")

@route.get("/")
def get_spell_list():
    return get_spell_list_query()

@route.get("/filter")
def get_filter_spell_list(level_min: int = None, level_max: int = None, tradition: str = None, trait: str = None, action: str = None):
    return get_spell_filter_query(level_min, level_max, tradition, trait, action)


@route.get("/{name}")
def get_spell(name: str):
    try:
       return get_spell_info_query(name)
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Spell '{name}' not found")