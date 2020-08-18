"""
app main
"""

# import pathlib

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse

from .routers import (
    api_gpd,
)


def create_app():
    """create app"""
    _app = FastAPI()

    # api using GeoPandas (not using DB)
    _app.include_router(
        api_gpd.router,
        prefix="/api_gpd",
        tags=["api_gpd"],
        responses={404: {"description": "not found"}},
    )

    return _app


app = create_app()


@app.get('/', response_class=HTMLResponse)
async def main_menu():
    return RedirectResponse("/client/index.html")



@app.get('/hello_world')
async def hello_world():
    """root"""
    return {"message": "Hello, WORLD!"}
