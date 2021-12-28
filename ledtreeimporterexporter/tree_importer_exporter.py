import bpy
from mathutils import Matrix, Vector
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

#Modified helper function from https://blender.stackexchange.com/questions/31693/how-to-find-if-a-point-is-inside-a-mesh
def point_inside_mesh(point, obj):
    cur = obj.matrix_world.inverted() @ point
    cpom = obj.closest_point_on_mesh(cur)
    vec = cur - cpom[1]
    dot = cpom[2].dot(vec)
    if dot < 0.0:
        return True
    else:
        return False

def read_data(context, filepath):
    #TODO: Fix this to make a grease pencil instead of a path.
    print("Attempting to import LED Tree...")
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    
    tree_mesh = bpy.data.curves.new("LED Tree", type='CURVE')
    tree_mesh.dimensions = '3D'

    
    # Divvy up the vertices
    verts = data.split("\n")
    
    
    tree_data = tree_mesh.splines.new('POLY')
    tree_data.points.add(len(verts)-1)
    
    i = 0
    for vert in verts:
        # There's some dumb character in the csv files that we need to get rid of:
        n_vert = vert.replace("﻿", "").split(",")
        
        # Now we actually create the data:
        tree_data.points[i].co = (float(n_vert[0]), float(n_vert[1]), float(n_vert[2]), 1)
        i += 1
    
    tree_obj = bpy.data.objects.new('LED Tree', tree_mesh)
    scn = bpy.context.scene
    scn.collection.objects.link(tree_obj)

    return {'FINISHED'}

def get_parker_tree_colors(context, filepath):
    # Step 1: Get the grease pencil
    # Step 2: Get the vertex color for each of the grease pencil vertices
    # Step 3: Export that data in to the csv
    scn = bpy.context.scene
    
    tree = None
    
    selected = bpy.context.selected_objects
    for obj in selected:
        if "LED Tree" in obj.name:
            tree = obj
    
    if tree == None:
        print("LED tree not found among selected objects")
        return {'CANCELLED'}
            
    # Get the tree data:
    tree_curve = tree.data.splines.active
            
    # Set up the file:
    f = open(filepath, 'w')
    f.write("FRAME_ID")
    
    for p in range(len(tree_curve.points)):
        i = str(p)
        f.write(",R_" + i + ",G_" + i + ",B_" + i)
    f.write("\n")
    
    # Now for each frame:
    for frame in range(scn.frame_start, scn.frame_end + 1, scn.frame_step):
        scn.frame_set(frame)
        f.write(str(frame - 1))
        # Then we go through each point:
        for p in range(len(tree_curve.points)):
            i = str(p)
            
            # We only want the 3D coordinates:
            coordinates = tree_curve.points[p].co
            
            coordinates_actual = Vector((coordinates[0], coordinates[1], coordinates[2]))
            # Now we get all objects:
            for ob in scn.objects:
                inside_objs = []
                if ob.type == 'MESH' and hasattr(ob, "active_material") and point_inside_mesh(coordinates_actual, ob):
                    inside_objs.append(ob)
                
                col = (0, 0, 0)
                if len(inside_objs) > 0:
                    # Average all the colors the point is inside:
                    for inside in inside_objs:
                        get_color = (inside.active_material.diffuse_color[0], inside.active_material.diffuse_color[1], inside.active_material.diffuse_color[2])
                        col = (col[0] + get_color[0], col[1] + get_color[1], col[2] + get_color[2])
                    col = (col[0] * 255 / len(inside_objs), col[1] * 255 / len(inside_objs), col[2] * 255 / len(inside_objs))
                    
            # Now we multiply the colors by 255, because that's what the CSV takes:
            f.write("," + str(int(col[0])) + "," +  str(int(col[1])) + "," + str(int(col[2])))
        if frame != scn.frame_end:
            f.write("\n")
    f.close()
    
    return {'FINISHED'}

class ImportParkerTree(Operator, ImportHelper):
    """Import this year's LED tree coordinates."""
    bl_idname = "led_tree_locations.load"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import LED Coordinates"

    # ImportHelper mixin class uses this
    filename_ext = ".csv"

    def execute(self, context):
        return read_data(context, self.filepath)
    
class ExportParkerTree(Operator, ExportHelper):
    """Export the color the LED tree coordinates detect at each point."""
    bl_idname = "parker_tree_colors.load"
    bl_label = "Export Color CSV"
    
    filename_ext = ".csv"
    
    def execute(self, context):
        return get_parker_tree_colors(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportParkerTree.bl_idname, text="Import LED Tree Coordinates")
    
def menu_func_export(self, context):
    self.layout.operator(ExportParkerTree.bl_idname, text="Export Light CSV")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    bpy.utils.register_class(ImportParkerTree)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ExportParkerTree)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportParkerTree)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportParkerTree)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)