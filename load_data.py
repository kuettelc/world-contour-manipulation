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


def plot_world(all_countries: tp.List[Country]):
    all_traces = []
    theta = np.linspace(0, 2 * np.pi, 100)
    for country in all_countries:
        color = (random(), random(), random())
        for p in country.geo_shape.geometry.polygons:
            x, y = p.exterior.xy
            isoperimetric_quotient = round(
                (4 * math.pi * p.area) / (p.length**2), 2)
            r = (p.area / math.pi)**0.5
            trace = go.Scatter(x=list(x), y=list(y), fillcolor=f'rgb{color}')

            if p.area > 1.0:
                all_traces.append(trace)

                c = p.centroid
                trace = go.Scatter(x=[c.x],
                                   y=[c.y],
                                   mode='text',
                                   text=[isoperimetric_quotient],
                                   textposition='bottom center')

                all_traces.append(trace)
                trace = go.Scatter(x=np.cos(theta) * r + c.x,
                                   y=np.sin(theta) * r + c.y,
                                   mode='lines',
                                   line=dict(color=f'rgb{color}',
                                             width=2,
                                             dash='dash'))
                all_traces.append(trace)

    fig = go.Figure(data=all_traces)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.show()

    return fig


@dataclass
class LongLat:
    lon: str
    lat: str

    @staticmethod
    def from_dict(d: tp.Dict) -> LongLat:
        return LongLat(d['lon'], d['lat'])


@dataclass
class Geometry:
    type: str
    coordinates: Coordinates
    polygons: tp.List[Polygon]

    @staticmethod
    def from_dict(d: tp.Dict) -> Geometry:

        if d['type'] == 'Polygon':
            return Geometry(d['type'], d['coordinates'],
                            [Polygon(p) for p in d['coordinates']])
        else:
            polygons = []
            for c in d['coordinates']:
                for c2 in c:
                    polygons.append(Polygon(c2))

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
