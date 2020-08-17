"""
app main
"""

# import pathlib

from fastapi import FastAPI

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


@app.get('/')
async def site_root():
    """root"""
    return {"message": "Hello, WORLD!"}
