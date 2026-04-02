from fastapi import FastAPI
from .db.connection import conn
from .db.view_registration import register_views
from .routes.spells_routes import route as spell_route
from .routes.ancestries_routes import route as ancestry_route
from .routes.feats_routes import route as feats_route

app = FastAPI()

register_views()
app.include_router(spell_route)
app.include_router(ancestry_route)
app.include_router(feats_route)
