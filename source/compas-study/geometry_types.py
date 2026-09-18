"""Minimal COMPAS Model adapter for an already constructed source mesh."""
from compas_model.elements import Element
from compas.datastructures import Mesh
from compas.geometry import Point, Vector
import math


class MeshElement(Element):
    @property
    def __data__(self):
        data = super().__data__
        data['geometry'] = self.geometry
        return data

    def compute_elementgeometry(self, include_features=False):
        if include_features and self.features:
            raise NotImplementedError('Mesh import adapter does not process fabrication features')
        return self.geometry.copy()


class MemberElement(Element):
    """Rectangular concept member generated from endpoints and section dimensions.

    Section envelopes reproduce the source visualization; these are not selected
    solid steel sections. Orientation follows the original transverse generator.
    """
    def __init__(self, start, end, width, depth, **kwargs):
        super().__init__(**kwargs)
        self.start = Point(*start)
        self.end = Point(*end)
        self.width = float(width)
        self.depth = float(depth)
        self.check_parameters()

    def check_parameters(self):
        if not all(math.isfinite(x) for x in [*self.start,*self.end,self.width,self.depth]):
            raise ValueError(f'{self.name}: nonfinite member parameter')
        if min(self.width,self.depth) <= 0:
            raise ValueError(f'{self.name}: section dimensions must be positive')
        if self.start.distance_to_point(self.end) < 1e-8:
            raise ValueError(f'{self.name}: zero-length member')

    @property
    def __data__(self):
        data = super().__data__
        data.update(start=self.start,end=self.end,width=self.width,depth=self.depth)
        return data

    def compute_elementgeometry(self, include_features=False):
        self.check_parameters()
        d = Vector.from_start_end(self.start,self.end).unitized()
        ref = Vector(1,0,0) if abs(d.z)>.95 else Vector(0,0,1)
        u = d.cross(ref).unitized()
        v = d.cross(u)
        vertices = [p+u*(su*self.width/2)+v*(sv*self.depth/2)
                    for p in (self.start,self.end)
                    for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        return Mesh.from_vertices_and_faces(vertices,
            [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
