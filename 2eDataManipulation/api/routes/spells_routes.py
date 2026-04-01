from fastapi import APIRouter
from ..db.connection import conn
from ..queries.spells_queries import get_spell_list_query

route = APIRouter(prefix="/spells")

@route.get("/")
def get_spell_list():
    return get_spell_list_query()