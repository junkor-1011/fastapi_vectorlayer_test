"""
test api using GeoPandas(NOT using DB)
"""

import json
import math
# import pathlib
from typing import (
    Optional,
    List,
)

from fastapi import (
    APIRouter,
    HTTPException,
)
import geopandas as gpd
import shapely.geometry


router = APIRouter()


# const
EXT_DATA_PATH = "/app/data"

# TMP: Test-Data

# japan_ver821 (only valid)
tmp = gpd.read_file(
    EXT_DATA_PATH + "/japan_ver821/japan_ver821.shp"
)
gdf_japan_ver821 = tmp[tmp.is_valid].copy()
del tmp


@router.get("/")
async def site_root():
    """test"""
    return {"message": "Hello, API using GeoPandas"}


@router.get("/tmp.geojson")
async def tmp_intersect_geojson():
    # read test-data
    # tmp = gpd.read_file(
    #     EXT_DATA_PATH + "/japan_ver821/japan_ver821.shp"
    # )
    # gdf = tmp[tmp.is_valid]     # intersectionなどのクエリが動かなくなる
    gdf = gdf_japan_ver821.copy()

    # intersections
    bbox = shapely.geometry.Polygon( # TMP
        [
            (134.80, 35.2),
            (135.20, 35.2),
            (135.20, 35.4),
            (134.80, 35.4),
        ]
    )

    # filtering
    intersections = gdf.geometry.intersection(bbox)
    gs_filtered = intersections[~intersections.is_empty] # geoseries

    # return geojson
    return json.loads(
        gs_filtered.to_json()
    )


@router.get("/japan_ver821/test0/{z}/{x}/{y}.geojson")
async def esri_japan_ver821_test0(
    z: int,
    x: int,
    y: int,
    KEN: Optional[str] = None,
) -> dict:
    """
    ***
    """
    gdf = gdf_japan_ver821.copy()

    # get bbox
    nw = tile_coord(z, x, y)
    se = tile_coord(z, x+1, y+1)
    bbox = shapely.geometry.Polygon(
        [
            nw, (se[0], nw[1]),
            se, (nw[0], se[1]), nw
        ]
    )

    # filter by KEN
    if KEN is not None:
        gdf = gdf[gdf.KEN == KEN]

    # filtering
    intersections = gdf.geometry.intersection(bbox)
    gs_filtered = intersections[~intersections.is_empty] # geoseries

    # NO DATA
    if len(gs_filtered) == 0:
        raise HTTPException(status_code=404, detail="No Data")

    # return geojson
    return json.loads(
        gs_filtered.to_json()
    )


def tile_coord(
    zoom: int,
    xtile: int,
    ytile: int,
) -> (float, float):
    """
    This returns the NW-corner of the square. Use the function
    with xtile+1 and/or ytile+1 to get the other corners.
    With xtile+0.5 & ytile+0.5 it will return the center of the tile.
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)
