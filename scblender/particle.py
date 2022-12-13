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
    collection : string : (It is the name of the collection to which the particle belongs)
    """

    def __init__(
        self, name="particle", position=None, rotation=None, scale=None
    ) -> None:
        self.__name = name

        try:
            self.__position = (
                position
                if position != None
                else [bpy.data.objects[self.__name].location[i] for i in range(3)]
            )
            self.__rotation = (
                rotation
                if rotation != None
                else [bpy.data.objects[self.__name].rotation_euler[i] for i in range(3)]
                
            )
            self.__scale = (
                scale
                if scale != None
                else [bpy.data.objects[self.__name].scale[i] for i in range(3)]
            )
        except:
            pass

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name:str) -> None:
        bpy.data.objects[self.__name].name = name
        self.__name = name
        return None

    def get_position(self) -> list:
        return self.__position

    def set_position(self, position:list) -> None:
        if (self.__checking_the_type_and_the_dimensionality(position)):
            bpy.data.objects[self.__name].location = position
            self.__position = position
        return None

    def get_rotation(self)-> list:
        return self.__rotation

    def set_rotation(self, rotation:list)-> None:
        if (self.__checking_the_type_and_the_dimensionality(rotation)):
            bpy.data.objects[self.__name].rotation_euler = rotation
            self.__rotation = rotation
        return None

    def get_scale(self) -> list:
        return self.__scale

    def set_scale(self, scale:list) -> None:
        if (self.__checking_the_type_and_the_dimensionality(scale)):
            bpy.data.objects[self.__name].scale = scale
            self.__scale = scale
        return None


    def __checking_the_type_and_the_dimensionality(self, greatness) -> bool:
        if ((len(greatness) == 3) and (isinstance(greatness, list) or isinstance(greatness, np.ndarray))): 
            return True
        else:
            print("You must provide as input a list or a numpy array of length 3")
            return False



    @property
    def get_vertices(self):
        """
        Returns:
            array: It returns an array with the position of the vertices
        """
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[self.__name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[self.__name]
        return [v.co for v in bpy.context.active_object.data.vertices]

    def set_vertices(self, vertex: list, new_coordinate: list) -> None:
        if bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[self.__name].select_set(True)
        bpy.context.active_object.data.vertices[vertex].co = new_coordinate
        return None



    def rotate(self, yz=0, zx=0, xy=0):
        bpy.data.objects[self.__name].rotation_euler = (yz, zx, xy)
        self.rotation = (yz, zx, xy)
        return self.rotation

    def resize(self, sx=1, sy=1, sz=1) -> list:
        bpy.data.objects[self.__name].scale = (sx, sy, sz)
        self.scale = (sx, sy, sz)
        return self.scale

    def subdivide(self):
        setting.select_particle(self.__name)
        setting.set_object_mode("edit")
        return bpy.ops.mesh.subdivide()

    def create_modifier(
        self, name_of_modifier="My_Modifier", type_of_modifier="SUBSURF"
    ):
        return setting.set_particle_visibility(
            self.__name
        ), bpy.context.active_object.modifiers.new(name_of_modifier, type_of_modifier)

    def create_skin(self, name_of_modifier="Skin"):
        return setting.set_particle_visibility(
            self.__name
        ), bpy.context.active_object.modifiers.new(name_of_modifier, "SKIN")

    def apply_shade_smooth(self):
        return setting.set_particle_visibility(self.__name), bpy.ops.object.shade_smooth()


class Sphere(Particle):
    def __init__(
        self,
        name="sphere",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1)
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale
        )
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.__name


class Vertice(Particle):
    def __init__(self, name="vertice", position=(0, 0, 0)):
        super().__init__(name=name, position=position)
        bpy.ops.mesh.primitive_vert_add()
        bpy.context.object.name = self.__name
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
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale
        )
        self.verts = verts
        self.edges = edges
        self.faces = faces
        # verts = bpy.context.active_object.data.vertices
        # edges = bpy.context.active_object.data.edges
        # faces = bpy.context.active_object.data.polygons
        mesh = bpy.data.meshes.new(self.__name)
        obj = bpy.data.objects.new(self.__name, mesh)
        col = bpy.data.collections.get("Collection")
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh.from_pydata(self.verts, self.edges, self.faces)


class Path_curve(Particle):
    def __init__(self, name="path_curve", position=(0, 0, 0)):
        super().__init__(name=name, position=position)
        bpy.ops.curve.primitive_nurbs_path_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.__name


class Bezier_curve(Particle):
    def __init__(
        self,
        name="bezier",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
    ):
        super().__init__(name=name, position=position, scale=scale)
        bpy.ops.curve.primitive_bezier_curve_add(
            radius=1,
            enter_editmode=False,
            align="WORLD",
            location=self.position,
            scale=self.scale,
        )
        bpy.context.object.name = self.__name


class Camera(Particle):
    def __init__(
        self,
        name="camera",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        focal_length=85,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale
        )
        self.focal_length = focal_length
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align="VIEW",
            location=self.position,
            rotation=self.rotation,
            scale=self.scale,
        )
        bpy.context.object.name = self.__name
        bpy.context.object.data.lens = self.focal_length


class Timer(Particle):
    def __init__(
        self,
        name="timer",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        frame=24,
    ):
        super().__init__(
            name=name, position=position, rotation=rotation, scale=scale
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
        bpy.context.object.name = self.__name
        scene = bpy.context.scene
        obj = scene.objects[self.__name]

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
