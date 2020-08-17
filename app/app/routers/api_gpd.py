"""
test api using GeoPandas(NOT using DB)
"""

import json
import math
# import pathlib

from fastapi import (
    APIRouter,
)
import geopandas as gpd
import shapely.geometry


router = APIRouter()


# const
EXT_DATA_PATH = "/app/data"


@router.get("/")
async def site_root():
    """test"""
    return {"message": "Hello, API using GeoPandas"}


@router.get("/tmp.geojson")
async def tmp_intersect_geojson():
    # read test-data
    tmp = gpd.read_file(
        EXT_DATA_PATH + "/japan_ver821/japan_ver821.shp"
    )
    gdf = tmp[tmp.is_valid]     # intersectionなどのクエリが動かなくなる

    # intersections
    area = shapely.geometry.Polygon( # TMP
        [
            (134.80, 35.2),
            (135.20, 35.2),
            (135.20, 35.4),
            (134.80, 35.4),
        ]
    )

    # filtering
    intersections = gdf.geometry.intersection(area)
    gs_filtered = intersections[~intersections.is_empty] # geoseries

    # return geojson
    return json.loads(
        gs_filtered.to_json()
    )


@router.get("/japan_ver821/test0/{z}/{x}/{y}.geojson")
async def esri_japan_ver821_test0():
    return
