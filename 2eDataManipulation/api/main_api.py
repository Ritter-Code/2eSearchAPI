from fastapi import FastAPI
from .db.connection import conn
from .db.view_registration import register_views
from .routes.spells_routes import route

app = FastAPI()

register_views()
app.include_router(route)
