from __future__ import annotations

import numpy as np
import json
import typing as tp
from dataclasses import dataclass
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from random import random
import math
import plotly.graph_objects as go

Coordinates = tp.List[tp.List[tp.List[float]]]


def load_data(path: str) -> tp.Dict:
    with open(path) as f:
        return json.load(f)


def scatter_plot_from_coordinates(coordinates: Coordinates):
    _, ax = plt.subplots()
    for c1 in coordinates:
        for c2 in c1:
            x = c2[0]
            y = c2[1]
            ax.scatter(x, y, c='k')
    return ax


def plot_world(
    all_countries: tp.List[Country],
    area_lower_bound: float = 0.0,
    area_upper_bound: float = float('inf')) -> None:
    all_traces = []
    theta = np.linspace(0, 2 * np.pi, 100)
    for country in all_countries:
        color = (random(), random(), random())
        for p in country.geo_shape.geometry.polygons:
            x, y = p.polygon.exterior.xy

            trace = go.Scatter(x=list(x),
                               y=list(y),
                               fillcolor=f'rgb{color}',
                               mode='lines')

            # filter polygons
            if p.area > area_lower_bound and p.area < area_upper_bound:
                all_traces.append(trace)

                c = p.centroid
                trace = go.Scatter(
                    x=[c.x],
                    y=[c.y],
                    mode='text',
                    text=[
                        f"Circularity: {p.isoperimetric_quotient}\n Area: {round(p.area,2)}"
                    ],
                    textposition='bottom center')

                all_traces.append(trace)

                # draw circle of same area on centroid
                trace = go.Scatter(
                    x=np.cos(theta) * p.radius_of_same_area + c.x,
                    y=np.sin(theta) * p.radius_of_same_area + c.y,
                    mode='lines',
                    line=dict(color=f'rgb{color}', width=2, dash='dash'))
                all_traces.append(trace)

    fig = go.Figure(
        data=all_traces,
        layout=go.Layout(title='World Map with Isoperimetric Circles'))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.show()


@dataclass
class LongLat:
    lon: str
    lat: str

    @staticmethod
    def from_dict(d: tp.Dict) -> LongLat:
        return LongLat(d['lon'], d['lat'])


# a bit absurd, but shapely doesn't have stubs
@dataclass
class Centroid:
    x: float
    y: float

    @staticmethod
    def from_polygon_centroid(c):
        Centroid(c.x, c.y)


@dataclass
class PolygonInfo:
    polygon: Polygon
    area: float
    centroid: Centroid
    isoperimetric_quotient: float
    radius_of_same_area: float

    @staticmethod
    def from_polygon(p: Polygon):
        isoperimetric_quotient = round((4 * math.pi * p.area) / (p.length**2),
                                       2)
        radius_of_same_area = (p.area / math.pi)**0.5
        return PolygonInfo(polygon=p,
                           area=np.pi * radius_of_same_area**2,
                           centroid=p.centroid,
                           isoperimetric_quotient=isoperimetric_quotient,
                           radius_of_same_area=radius_of_same_area)


@dataclass
class Geometry:
    type: str
    coordinates: Coordinates
    polygons: tp.List[PolygonInfo]

    @staticmethod
    def from_dict(d: tp.Dict) -> Geometry:

        if d['type'] == 'Polygon':
            return Geometry(d['type'], d['coordinates'], [
                PolygonInfo.from_polygon(Polygon(p)) for p in d['coordinates']
            ])
        else:
            polygons = []
            for c in d['coordinates']:
                for c2 in c:
                    polygons.append(PolygonInfo.from_polygon(Polygon(c2)))

            return Geometry(d['type'], d['coordinates'], polygons)


@dataclass
class GeoShape:
    type: str
    geometry: Geometry
    properties: tp.Dict

    @staticmethod
    def from_dict(d: tp.Dict) -> GeoShape:
        return GeoShape(d['type'], Geometry.from_dict(d['geometry']),
                        d['properties'])


@dataclass
class Country:
    geo_point_2d: LongLat
    geo_shape: GeoShape
    iso3: str
    status: str
    color_code: str
    name: str
    continent: str
    region: str
    iso_3166_1_alpha_2_codes: str
    french_short: str

    @staticmethod
    def from_dict(d: tp.Dict) -> Country:
        return Country(
            LongLat.from_dict(d['geo_point_2d']),
            GeoShape.from_dict(d['geo_shape']),
            d['iso3'],
            d['status'],
            d['color_code'],
            d['name'],
            d['continent'],
            d['region'],
            d['iso_3166_1_alpha_2_codes'],
            d['french_short'],
        )
