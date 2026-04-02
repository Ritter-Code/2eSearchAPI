from fastapi import APIRouter, HTTPException
from ..db.connection import conn
from ..queries.ancestries_queries import get_ancestry_list_query
from ..queries.ancestries_queries import get_ancestry_info_query
from ..queries.ancestries_queries import get_ancestry_filter_query

route = APIRouter(prefix='/ancestry')

@route.get('/')
def get_ancestry_list():
    return get_ancestry_list_query()

@route.get('/filter')
def get_ancestry_filter(rarity: str = None, hp: int = None, size: str = None, boost: str = None):
    return get_ancestry_filter_query(rarity, hp, size, boost)

@route.get('/{name}')
def get_ancestry_info(name: str):
    try:
       return get_ancestry_info_query(name)
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Ancestry '{name}' not found")