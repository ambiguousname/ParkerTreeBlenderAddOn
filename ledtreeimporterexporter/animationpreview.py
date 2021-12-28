import bpy
import bmesh
import math
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
from bpy.types import Operator

def create_lights(points, light_arr):
    
    # Let's create a collection for easy deletion:
    led_coll = bpy.data.collections.new("LED Collection")
    bpy.context.scene.collection.children.link(led_coll)
    
    objects = led_coll.objects
    
    #Alright, now we can add the cube object as much as we'd like.
    for point in points:
        # We need to do these steps each time so that we can have a unique material:
        
        # Create the LED cube object:
        cube_mesh = bpy.data.meshes.new('LED Cube')
        
        # Create the cube itself:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=0.05)
        bm.to_mesh(cube_mesh)
        bm.free()
        
        # Create the material for the cube to use:
        mat = bpy.data.materials.new(name = "LED Mat")
        mat.use_nodes = False
        
        cube_mesh.materials.append(mat)
        
        cube = bpy.data.objects.new('LED Cube', cube_mesh)
        cube.location = Vector((point.co[0], point.co[1], point.co[2]))
        objects.link(cube)
        light_arr.append(cube)
        

def read_led_data(context, filepath):
    print("Attempting to import LED Animation...")
    
    tree = None
    
    selected = bpy.context.selected_objects
    for obj in selected:
        if "LED Tree" in obj.name:
            tree = obj

    if tree == None:
        print("LED tree not found among selected objects")    
        return {'CANCELLED'}
    
    tree_curve = tree.data.splines.active
        
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    
    light_arr = []
    
    # There's some dumb character in the csv files that we need to get rid of, I think.
    # It doesn't hurt to be safe either way:
    data = data.replace("﻿", "")
    
    rows = data.split("\n")
    
    light_arr = []
    
    # Set up the lights for us to use:
    create_lights(tree_curve.points, light_arr)
    
    scn = context.scene
    first_row = rows[0].split(",")
    for row in rows:
        cols = row.split(",")
        # Ignore the first row:
        if cols[0] != "FRAME_ID":
            for i in range(0, math.floor(len(cols)/3)):
                # Get the color for the first light:
                actual_position = (i * 3) + 1
                color = (float(cols[actual_position])/255, float(cols[actual_position + 1])/255, float(cols[actual_position + 2])/255, 1.0)
                
                actual_column = int(first_row[actual_position][2:])
                light_arr[actual_column].active_material.diffuse_color = color
                light_arr[actual_column].active_material.keyframe_insert(data_path = "diffuse_color", frame=int(cols[0]))
    return {'FINISHED'}
            
    

class LoadLEDAnim(Operator, ImportHelper):
    """Import the LED animation."""
    bl_idname = "led_data.load"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import LED Animation"

    # ImportHelper mixin class uses this
    filename_ext = ".csv"

    def execute(self, context):
        return read_led_data(context, self.filepath)

def menu_func_import(self, context):
    self.layout.operator(LoadLEDAnim.bl_idname, text="Import LED Animation")

def register():
    bpy.utils.register_class(LoadLEDAnim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(LoadLEDAnim)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
