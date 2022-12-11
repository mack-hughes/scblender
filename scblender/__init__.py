from os import setegid
import bpy
from . import setting
import math
import numpy as np
import pandas as pd


class Particle:
    """This class create a particle with the following characteristics:
    Parameters
    ----------
    name : string
    position : array (x,y,z)
    rotation : array (yz,zx,xy)
    scale : array (sx,sy,sz)
    collection : string : (It is the name of the collection to which the particle belongs),
    data (For when we want to link this particle with a database contanins informations such as the path, the momento, charge, and so on)
    """

    def __init__(
        self, name="particle", position=None, rotation=None, scale=None, data=None
    ) -> None:
        self.name = name
        self.data = data
        try:
            self.position = (
                position
                if position != None
                else (
                    bpy.data.objects[self.name].location[0],
                    bpy.data.objects[self.name].location[1],
                    bpy.data.objects[self.name].location[2],
                )
            )
            self.rotation = (
                rotation
                if rotation != None
                else (
                    bpy.data.objects[self.name].rotation_euler[0],
                    bpy.data.objects[self.name].rotation_euler[1],
                    bpy.data.objects[self.name].rotation_euler[2],
                )
            )
            self.scale = (
                scale
                if scale != None
                else (
                    bpy.data.objects[self.name].scale[0],
                    bpy.data.objects[self.name].scale[1],
                    bpy.data.objects[self.name].scale[2],
                )
            )
        except:
            pass

    @property
    def vertices(self):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[self.name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        return [v.co for v in bpy.context.active_object.data.vertices]

    def set_vertices(self, vertex: list, new_coordinate):
        if bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[self.name].select_set(True)
        bpy.context.active_object.data.vertices[vertex].co = new_coordinate

    def move(self, x=0, y=0, z=0):
        bpy.data.objects[self.name].location = (x, y, z)
        self.position = (x, y, z)
        return self.position

    def rotate(self, yz=0, zx=0, xy=0):
        bpy.data.objects[self.name].rotation_euler = (yz, zx, xy)
        self.rotation = (yz, zx, xy)
        return self.rotation

    def resize(self, sx=1, sy=1, sz=1) -> list:
        bpy.data.objects[self.name].scale = (sx, sy, sz)
        self.scale = (sx, sy, sz)
        return self.scale

    def subdivide(self):
        setting.select_particle(self.name)
        setting.set_object_mode("edit")
        return bpy.ops.mesh.subdivide()

    def create_modifier(
        self, name_of_modifier="My_Modifier", type_of_modifier="SUBSURF"
    ):
        return setting.set_particle_visibility(
            self.name
        ), bpy.context.active_object.modifiers.new(name_of_modifier, type_of_modifier)

    def create_skin(self, name_of_modifier="Skin"):
        return setting.set_particle_visibility(
            self.name
        ), bpy.context.active_object.modifiers.new(name_of_modifier, "SKIN")

    def apply_shade_smooth(self):
        return setting.set_particle_visibility(self.name), bpy.ops.object.shade_smooth()


class Sphere(Particle):
    def __init__(
        self,
        name="sphere",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        data=None,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale, data=data
        )
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.name


class Vertice(Particle):
    def __init__(self, name="vertice", position=(0, 0, 0), data=None):
        super().__init__(name=name, position=position, data=data)
        bpy.ops.mesh.primitive_vert_add()
        bpy.context.object.name = self.name
        setting.set_object_mode("OBJECT"), self.move(
            position[0], position[1], position[2]
        )


class Mesh(Particle):
    def __init__(
        self,
        name="mesh",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        verts=[],
        edges=[],
        faces=[],
        data=None,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale, data=data
        )
        self.verts = verts
        self.edges = edges
        self.faces = faces
        # verts = bpy.context.active_object.data.vertices
        # edges = bpy.context.active_object.data.edges
        # faces = bpy.context.active_object.data.polygons
        mesh = bpy.data.meshes.new(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        col = bpy.data.collections.get("Collection")
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh.from_pydata(self.verts, self.edges, self.faces)


class Path_curve(Particle):
    def __init__(self, name="path_curve", position=(0, 0, 0), data=None):
        super().__init__(name=name, position=position, data=data)
        bpy.ops.curve.primitive_nurbs_path_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.name


class Bezier_curve(Particle):
    def __init__(
        self,
        name="bezier",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        data=None,
    ):
        super().__init__(name=name, position=position, scale=scale, data=data)
        bpy.ops.curve.primitive_bezier_curve_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.name


class Camera(Particle):
    def __init__(
        self,
        name="camera",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        focal_length=85,
        data=None,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale, data=data
        )
        self.focal_length = focal_length
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align="VIEW",
            location=self.position,
            rotation=self.rotation,
            scale=self.scale,
        )
        bpy.context.object.name = self.name
        bpy.context.object.data.lens = self.focal_length


class Timer(Particle):
    def __init__(
        self,
        name="timer",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        frame=24,
        data=None,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale, data=data
        )
        self.frame = frame
        bpy.ops.object.text_add(
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            rotation=self.rotation,
            scale=self.scale,
        )
        bpy.ops.object.modifier_add(type="SOLIDIFY")
        bpy.context.object.modifiers["Solidify"].thickness = 0.02
        bpy.context.object.data.align_x = "CENTER"
        bpy.context.object.data.align_y = "CENTER"
        bpy.context.object.name = self.name
        scene = bpy.context.scene
        obj = scene.objects[self.name]

        def recalculate_text(scene):
            if scene.frame_current in range(0, 60 * self.frame):
                obj.data.body = (
                    str(int(bpy.context.scene.frame_current / self.frame)) + "s"
                )
            else:
                min = int(bpy.context.scene.frame_current / self.frame) // 60
                obj.data.body = (
                    str(min)
                    + "min  "
                    + str(int(bpy.context.scene.frame_current / self.frame) - 60 * min)
                    + "s"
                )

        bpy.app.handlers.frame_change_post.append(recalculate_text)


if __name__ == "__main__":
    m = Mesh(
        verts=((0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0)),
        edges=([0, 1], [1, 2], [0, 2], [0, 3], [2, 3]),
        faces=([0, 1, 2], [2, 0, 3]),
    )


# verts = ((0,1,0),(1,0,0),(0,0,1),(-1,0,0))
# edges = ([0,1],[1,2],[0,2],[0,3],[2,3])
# faces = ([0,1,2],[2,0,3])

# name = "New Object"
# mesh = bpy.data.meshes.new(name)
# obj = bpy.data.objects.new(name, mesh)
# col = bpy.data.collections.get("Collection")
# col.objects.link(obj)
# bpy.context.view_layer.objects.active = obj
# mesh.from_pydata(verts,edges,faces)
