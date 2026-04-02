from fastapi import APIRouter, HTTPException
from ..queries.feats_queries import get_feat_list_query, get_feat_filter_query, get_feat_info_query

route = APIRouter(prefix='/feats')

@route.get('/')
def get_feat_list():
    return get_feat_list_query()

@route.get('/filter')
def get_feat_filter(level_min: int = None, level_max: int = None, category: str = None, rarity: str = None, trait: str = None, action_type: str = None):
    return get_feat_filter_query(level_min, level_max, category, rarity, trait, action_type)

@route.get('/{name}')
def get_feat_info(name: str):
    try:
        return get_feat_info_query(name)
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Feat '{name}' not found")
