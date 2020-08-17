"""
test api using GeoPandas(NOT using DB)
"""

# import pathlib

from fastapi import (
    APIRouter,
)
import geopandas as gpd
import shapely.geometry


# サブアプリ
router = APIRouter()


@router.get("/")
async def site_root():
    """test"""
    return {"message": "Hello, API using GeoPandas"}
