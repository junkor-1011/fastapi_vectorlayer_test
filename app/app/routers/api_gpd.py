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
    Response,
)
import geopandas as gpd
import shapely.geometry
import mapbox_vector_tile
import geobuf


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

# osmnx highway nodes & edges sample
gdf_nodes_highway = gpd.read_file(
    EXT_DATA_PATH + "/nodes_highway/nodes.shp"
)
gdf_edges_highway = gpd.read_file(
    EXT_DATA_PATH + "/edges_highway/edges.shp"
)


@router.get("/")
async def site_root():
    """test"""
    return {"message": "Hello, API using GeoPandas"}


@router.get("/tmp.geojson")
async def tmp_intersect_geojson():
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


@router.get("/osmnx/highway/nodes/{z}/{x}/{y}.geojson")
async def osmnx_highway_nodes(
    z: int,
    x: int,
    y: int,
    highway: Optional[str] = None,
) -> dict:
    """
    ***
    """
    gdf = gdf_nodes_highway.copy()

    # get bbox
    nw = tile_coord(z, x, y)
    se = tile_coord(z, x+1, y+1)
    bbox = shapely.geometry.Polygon(
        [
            nw, (se[0], nw[1]),
            se, (nw[0], se[1]), nw
        ]
    )

    # filter by highway
    if highway is not None:
        # T.B.D
        gdf = gdf

    # filtering
    intersections = gdf.geometry.intersection(bbox)
    gs_filtered = intersections[~intersections.is_empty] # geoseries
    gdf_filtered = gpd.GeoDataFrame(
        gdf.loc[gs_filtered.index, :].drop(columns=['geometry']),
        geometry=gs_filtered,
    )

    # NO DATA
    if len(gs_filtered) == 0:
        raise HTTPException(status_code=404, detail="No Data")

    # return geojson
    return json.loads(
        gdf_filtered.to_json()
    )


@router.get("/osmnx/highway/edges/{z}/{x}/{y}.geojson")
async def osmnx_highway_edges(
    z: int,
    x: int,
    y: int,
    highway: Optional[str] = None,
) -> dict:
    """
    ***
    """
    gdf = gdf_edges_highway.copy()

    # get bbox
    nw = tile_coord(z, x, y)
    se = tile_coord(z, x+1, y+1)
    bbox = shapely.geometry.Polygon(
        [
            nw, (se[0], nw[1]),
            se, (nw[0], se[1]), nw
        ]
    )

    # filter by highway
    if highway is not None:
        # T.B.D
        gdf = gdf

    # filtering
    intersections = gdf.geometry.intersection(bbox)
    gs_filtered = intersections[~intersections.is_empty] # geoseries
    gdf_filtered = gpd.GeoDataFrame(
        gdf.loc[gs_filtered.index, :].drop(columns=['geometry']),
        geometry=gs_filtered,
    )

    # NO DATA
    if len(gs_filtered) == 0:
        raise HTTPException(status_code=404, detail="No Data")

    # return geojson
    return json.loads(
        gdf_filtered.to_json()
    )


@router.get(
    "/japan_ver821/mvt/{z}/{x}/{y}.mvt",
    responses={
        200: {"content": {"application/vnd.mapbox-vector-tile": {}}}
    }
)
async def esri_japan_ver821_mvt(
    z: int,
    x: int,
    y: int,
    limit_zmin: Optional[int] = 8,
):
    """
    mvt(pbf) binary vector TileLayer

    CAUTION:
        - NOT works well

    ToDo:
        - https://github.com/tilezen/mapbox-vector-tile#coordinate-transformations-for-encoding
    """
    if limit_zmin is not None:
        if z < limit_zmin:
            raise HTTPException(status_code=404, detail="Over limit of zoom")


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

    # filtering
    intersections = gdf.geometry.intersection(bbox)
    gs_filtered = intersections[~intersections.is_empty] # geoseries
    gdf_filtered = gpd.GeoDataFrame(
        gdf.loc[gs_filtered.index, :].drop(columns=['geometry']),
        geometry=gs_filtered,
    )

    # NO DATA
    if len(gs_filtered) == 0:
        raise HTTPException(status_code=404, detail="No Data")

    # encode
    tile_dict = json.loads(gdf_filtered.to_json())
    tile_dict['name'] = "japan_ver821" # layer name
    tile_mvt = mapbox_vector_tile.encode([tile_dict])

    # return tile
    return Response(
        content=tile_mvt,
        media_type="application/vnd.mapbox-vector-tile",
    )


@router.get(
    "/geobuf/japan_ver821.pbf",
    responses={
        200: {"content": {"application/vnd.mapbox-vector-tile": {}}}
    }
)
async def esri_japan_ver821_geobuf(
):
    """
    ***

    Refs:
        - https://github.com/pygeobuf/pygeobuf
    """

    gdf = gdf_japan_ver821.copy()

    # encode
    tile_dict = json.loads(gdf.to_json())
    tile_dict['name'] = "japan_ver821" # layer name
    pbf = geobuf.encode(tile_dict)

    # return tile
    return Response(
        content=pbf,
        media_type="application/vnd.mapbox-vector-tile",
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
