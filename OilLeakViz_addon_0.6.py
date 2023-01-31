bl_info = {
    "name": "OilLeakViz",
    "author": "Emil K.",
    "version": (0, 5),
    "blender": (2, 90, 0),
    "location": "3D View > Sidebar > OilLeakViz",
    "description": "Визуализация подводных струй",
    "category": "3D View",
}


import bpy
import math
from bpy.types import Panel, Operator, PropertyGroup, FloatProperty, PointerProperty
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ImportHelper
from bpy.props import IntProperty, PointerProperty, BoolProperty
import bpy.utils.previews

import bmesh
from bpy_extras.object_utils import AddObjectHelper

import pandas as pd
import numpy


def clear_scene():
    bpy.context.space_data.shading.type = 'MATERIAL'
    bpy.context.space_data.overlay.show_floor = False
    bpy.context.space_data.overlay.show_floor = True
    bpy.context.space_data.overlay.show_floor = False
    bpy.context.space_data.overlay.show_axis_z = True
    bpy.context.space_data.overlay.show_text = False
    bpy.context.space_data.overlay.show_cursor = False
    bpy.context.space_data.overlay.show_annotation = False
    bpy.context.space_data.overlay.show_extras = False
    bpy.context.space_data.overlay.show_relationship_lines = False
    bpy.context.space_data.overlay.show_outline_selected = False
    bpy.context.space_data.overlay.show_object_origins = False
    bpy.context.space_data.overlay.show_motion_paths = False
    bpy.context.space_data.overlay.show_bones = False
    bpy.context.space_data.overlay.show_wireframes = True
    bpy.context.space_data.overlay.wireframe_threshold = 0
    bpy.context.space_data.overlay.wireframe_opacity = 0.99

    bpy.ops.object.select_pattern(pattern="Circle*")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_pattern(pattern="Cube*")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_pattern(pattern="MyObj*")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_pattern(pattern="Grid*")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_pattern(pattern="Text*")
    bpy.ops.object.delete(use_global=False)


def sunflower(n, alpha):   #  example: n=500, alpha=2
    b = round(alpha*math.sqrt(n))      # number of boundary points
    phi = (math.sqrt(5)+1)/2           # golden ratio
    x = []
    y = []
    for k in range(1,n):
        r = radius(k,n,b)
        theta = 2*math.pi*k/phi**2
        x.append(r*math.cos(theta))
        y.append(r*math.sin(theta))
    return x,y

def radius(k,n,b):
    if (k>n-b):
        return 1            # put on the boundary
    else:
        return( math.sqrt(k-1/2)/math.sqrt(n-(b+1)/2) )    # apply square root

def create_2D_grid(grid_name, grid_size, grid_pos, grid_rot, x_sub, y_sub, grid_material=(1, 1, 1, 1)):
        """
        Create a Grid of provided size. It will be of square of size provided in grid_size.
        Arguments:
            grid_name        : The name of grid.
            grid_size        : The size of grid.
            grid_pos         : The global position of grid.
            x_sub           : The subdivisions in x axis.
            y_sub           : The subdivisions in y axis.
            grid_material    : The material color of grid. Default value gives White diffuse material
        Imported User Defined Functions :
            create_material  : The materials were created and assigned if not exist.
        """



        bpy.ops.mesh.primitive_grid_add(
            size=grid_size, location=grid_pos, rotation=grid_rot,
            x_subdivisions=x_sub, y_subdivisions=y_sub)
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True)
        bpy.context.active_object.name = "Grid " + grid_name
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.faces.active = None

        # Changing origin to origin of plot.
        for v in bm.verts:
            if v.index == 0:
                v.select = True
                co = v.co
                bpy.context.scene.cursor.location = (co.x, co.y, co.z)
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.origin_set(
                    type='ORIGIN_CURSOR', center='MEDIAN')
                break
        if co.y == co.z:
            bpy.ops.transform.translate(
                value=(0, 0-co.y, 0-co.z), orient_type='GLOBAL',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        elif co.x == co.y:
            bpy.ops.transform.translate(
                value=(0-co.x, 0-co.y, 0), orient_type='GLOBAL',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        elif co.x == co.z:
            bpy.ops.transform.translate(
                value=(0-co.x, 0, 0-co.z), orient_type='GLOBAL',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))

        # Adding wireframe modifier to get grid structure.
        bpy.ops.object.modifier_add(type='WIREFRAME')
        bpy.context.object.modifiers["Wireframe"].thickness = 0.01 if (grid_size>1) else 0.001
        #text_material = PrincipleMaterial("GridMaterial", grid_material)
        #activeObject = bpy.context.active_object
        #activeObject.data.materials.append(
            #text_material.create_principle_bsdf())
        return

def grid_text(grid_size):

    grid_material = ''
    create_2D_grid(grid_name="GRID_Y_Z", grid_size=grid_size, grid_pos=(0, 0, 0),grid_rot=(math.radians(0), math.radians(-90), math.radians(0)),x_sub=11, y_sub=11, grid_material=grid_material)
    create_2D_grid( grid_name="GRID_X_Y", grid_size=grid_size, grid_pos=(0, 0, 0),grid_rot=(math.radians(0), math.radians(0), math.radians(0)),x_sub=11, y_sub=11, grid_material=grid_material)
    create_2D_grid(grid_name="GRID_Z_X", grid_size=grid_size, grid_pos=(0, 0, 0),grid_rot=(math.radians(90), math.radians(0), math.radians(0)),x_sub=11, y_sub=11, grid_material=grid_material)

    bpy.ops.object.text_add(radius = grid_size/8.0, enter_editmode=False, align='WORLD', location=(grid_size + grid_size/5.0, 0, 0), scale=(1,1,1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
    bpy.ops.transform.rotate(value=3.14159, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
    text = bpy.context.object
    text.data.body = str(grid_size)+"m"

    bpy.ops.object.text_add(radius = grid_size/8.0, enter_editmode=False, align='WORLD', location=(0, grid_size, 0), scale=(1,1,1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
    text = bpy.context.object
    text.data.body = str(grid_size)+"m"

    bpy.ops.object.text_add(radius = grid_size/8.0, enter_editmode=False, align='WORLD', location=(0,0,grid_size), scale=(1,1,1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
    text = bpy.context.object
    text.data.body = str(grid_size)+"m"


class DeleteContext(bpy.types.Operator):
    bl_idname = "object.run_delete_operator"
    bl_label = "Run Delete Operator"

    def execute(self, context):
        clear_scene()
        return {'FINISHED'}


class GeometryNodesSetup(bpy.types.Operator):
    bl_idname = "object.run_geonodes_setup"
    bl_label = "Run Geometry Nodes Operator"

    def execute(self, context):
        bpy.ops.node.new_geometry_nodes_modifier()
        return {'FINISHED'}

class RenderBubbles(bpy.types.Operator):
    bl_idname = "object.run_render_bubbles"
    bl_label = "Run Bubbles Operator"

    def execute(self, context):
        props = bpy.context.scene.sf_props

        clear_scene()
        if(props.selected_file != None):
            filename = props.selected_file
            columns_to_keep = ['z','x', 'y', 'r', 'Phi(rad)', 'N_gas', 'N_oil', 'N_hydrate']
            z_const = 0
            x_const = 1
            y_const = 2
            r = 3
            Phi_rad = 4
            N_gas = 5
            N_oil = 6
            N_hydrate = 7

            df = pd.read_table(filename, sep="\s+", usecols=columns_to_keep)
            data = df.to_numpy()

            verts = []
            s = []
            ss = []
            last_row = data[-1]
            grid_size = 1 if (last_row[0]<=1) else 10


            grid_text(grid_size)

            for data_item in data:
                x,y = sunflower(int(data_item[N_gas]/1000), 1)
                x_len = len(x)
                for j in range(x_len):
                    x_generated = float(x[j]*data_item[r]+data_item[x_const])
                    y_generated = float(y[j]*data_item[r]+data_item[y_const])
                    z_generated = float(data_item[z_const])


                    x_rotated = x_generated
                    y_rotated = - y_generated*math.cos(math.pi/2-data_item[Phi_rad ])
                    z_rotated =  z_generated + y_generated*math.sin(math.pi/2-data_item[Phi_rad ])

                    verts.append((x_rotated, y_rotated, z_rotated))
                    s.append(True)
                    ss.append(False)
                x,y = sunflower(int(data_item[N_oil]/1000), 1)
                x_len = len(x)
                for j in range(x_len):
                    x_generated = float(x[j]*data_item[r]+data_item[x_const])
                    y_generated = float(y[j]*data_item[r]+data_item[y_const])
                    z_generated = float(data_item[z_const])

                    x_rotated = x_generated
                    y_rotated = - y_generated*math.cos(math.pi/2-data_item[Phi_rad ])
                    z_rotated = z_generated + y_generated*math.sin(math.pi/2-data_item[Phi_rad ])

                    verts.append((x_rotated, y_rotated, z_rotated))
                    s.append(False)
                    ss.append(False)
                x,y = sunflower(int(data_item[N_hydrate]/1000), 1)
                x_len = len(x)
                for j in range(x_len):
                    x_generated = float(x[j]*data_item[r]+data_item[x_const])
                    y_generated = float(y[j]*data_item[r]+data_item[y_const])
                    z_generated = float(data_item[z_const])


                    x_rotated = x_generated
                    y_rotated = - y_generated*math.cos(math.pi/2-data_item[Phi_rad ])
                    z_rotated = z_generated + y_generated*math.sin(math.pi/2-data_item[Phi_rad ])

                    verts.append((x_rotated, y_rotated, z_rotated))
                    s.append(False)
                    ss.append(True)

            obj_name = "MyObj"
            mesh_data = bpy.data.meshes.new(obj_name + "_data")
            obj = bpy.data.objects.new(obj_name, mesh_data)
            bpy.context.scene.collection.objects.link(obj)
            mesh_data.from_pydata(verts, [], [])
            scale = numpy.array(s)
            obj.data.attributes.new(name='gas_oil', type='BOOLEAN', domain='POINT')
            obj.data.attributes['gas_oil'].data.foreach_set('value', scale)

            scale = numpy.array(ss)
            obj.data.attributes.new(name='hydrate', type='BOOLEAN', domain='POINT')
            obj.data.attributes['hydrate'].data.foreach_set('value', scale)
            bpy.ops.object.select_pattern(pattern="MyObj*")
        return {'FINISHED'}



def install():
    """ Install MediaPipe and dependencies behind the scenes """
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "numpy"])


def makeNewMaterial(name):

    mat = bpy.data.materials.get(name)

    if mat is None:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True

    if mat.node_tree:
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        bsdf = nodes.get("ShaderNodeBsdfPrincipled")
    return mat

def draw_file_opener(self, context):
    layout = self.layout
    scn = context.scene
    col = layout.column()
    row = col.row(align=True)
    row.prop(scn.settings, 'file_path', text='directory:')
    row.operator("something.identifier_selector", icon="FILE_FOLDER", text="")


class SelectFileProp():
    selected_file = None



class RenderSettings(PropertyGroup):
    lines = IntProperty(
        name="Lines",
        min=0
    )
    bubbles = IntProperty(
        name="Bubbles",
        min=0
    )
    gas = BoolProperty(
        name="Gas"
    )

class RunFileSelector(bpy.types.Operator, ImportHelper):
    bl_idname = "something.identifier_selector"
    bl_label = "select file"
    filename_ext = ""
    file_dir = ""

    def execute(self, context):
        props = bpy.context.scene.sf_props
        props.selected_file = self.properties.filepath
        print(props.selected_file)
        return {'FINISHED'}



class ColorCollection(bpy.types.PropertyGroup):
    # name: bpy.props.StringProperty
    active: bpy.props.BoolProperty(default=False)
    icon: bpy.props.IntProperty()
    color: bpy.props.FloatVectorProperty(
         name = "Color",
         subtype = "COLOR",
         default = (1.0,1.0,1.0,1.0),
         size = 4)

class Settings(PropertyGroup):
    # Capture only body pose if True, otherwise capture hands, face and body


    color:bpy.props.FloatVectorProperty(name = "myColor",
                                     subtype = "COLOR",
                                     size = 4,
                                     min = 0.0,
                                     max = 1.0
                                     )


    type_enum: bpy.props.EnumProperty(
                name = "Тип визуализации",
                description = "Выбор типа",
                items=[("T", "Температура", ""),
                       ("O", "Концентрация нефти", ""),
                       ("G", "Концентрация газа", ""),
                       ("H", "Концентрация гидрата", ""),
                       ("W", "Концентрация воды", "")
                        ]
                )

class DebugOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.run_debug_operator"
    bl_label = "Run Debug Operator"

    def execute(self, context):
        #bpy.ops.object.select_all(action='SELECT')

        clear_scene()

        props = bpy.context.scene.sf_props
        enums = bpy.context.scene.settings
        filename = props.selected_file # "/home/tatyana/Документы/Универ Эмиль/Грант//jet_data.dat"


        if(props.selected_file != None):
            columns_to_keep = ['z','x', 'y', 'r', 'T', 'Phi(rad)', 'Phi(deg)', 'alfao', 'alfag', 'alfah', 'alfaw']
            z_const = 0
            x_const = 1
            y_const = 2
            r_const = 3
            T_const = 4
            Phi_rad = 5
            Phi_deg = 6
            alfao_const = 7
            alfag_const = 8
            alfah_const = 9
            alfaw_const = 10
            df = pd.read_table(filename, sep="\s+", usecols=columns_to_keep)
            data = df.to_numpy()

            last_row = data[-1]
            grid_size = 1 if (last_row[z_const]<=1) else 10

            grid_text(grid_size)

            i = 0
            for data_item in data:
                bpy.ops.mesh.primitive_cube_add(size=0.25, enter_editmode=False, align='WORLD', location=(data_item[x_const], data_item[y_const], data_item[z_const]), scale=(1, 1, 1))

        return {'FINISHED'}



class RunOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.run_oil_operator"
    bl_label = "Run Oil Operator"

    def execute(self, context):
        #bpy.ops.object.select_all(action='SELECT')

        clear_scene()

        props = bpy.context.scene.sf_props
        enums = bpy.context.scene.settings
        filename = props.selected_file # "/home/tatyana/Документы/Универ Эмиль/Грант//jet_data.dat"


        if(props.selected_file != None):
            columns_to_keep = ['z','x', 'y', 'r', 'T', 'Phi(rad)', 'Phi(deg)', 'alfao', 'alfag', 'alfah', 'alfaw']
            z_const = 0
            x_const = 1
            y_const = 2
            r_const = 3
            T_const = 4
            Phi_rad = 5
            Phi_deg = 6
            alfao_const = 7
            alfag_const = 8
            alfah_const = 9
            alfaw_const = 10
            df = pd.read_table(filename, sep="\s+", usecols=columns_to_keep)
            data = df.to_numpy()

            last_row = data[-1]
            grid_size = 1 if (last_row[z_const]<=1) else 10

            grid_text(grid_size)

            i = 0
            for data_item in data:
                bpy.ops.mesh.primitive_circle_add(radius=data_item[r_const], fill_type='NGON', enter_editmode=False, align='WORLD', location=(data_item[x_const], data_item[y_const], data_item[z_const]), scale=(1, 1, 1))
                radius = math.radians(90 - data_item[Phi_deg])
                x_radians = (math.pi/2) - data_item[Phi_rad]

                bpy.context.active_object.rotation_euler = (-x_radians, 0, 0)
                #bpy.ops.transform.rotate(value=radius, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',  mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)


                name = "Material-" + str(i)
                temperature = data_item[T_const]
                oil = data_item[alfao_const]
                gas = data_item[alfag_const]
                hydrate = data_item[alfah_const]
                water = data_item[alfao_const]

                mat = makeNewMaterial(name)
                bpy.context.active_object.data.materials.append(mat)
                if(enums.type_enum == "T"):
                    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.01*temperature, 0, 1-0.01*temperature, 1)
                if(enums.type_enum == "O"):
                    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, oil, 0, 1)
                if(enums.type_enum == "G"):
                    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, gas, 0, 1)
                if(enums.type_enum == "H"):
                    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, hydrate, 0, 1)
                if(enums.type_enum == "W"):
                    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, water, 0, 1)

                i += 1

        return {'FINISHED'}


class MessageBox(bpy.types.Operator):
    bl_idname = "message.messagebox"
    bl_label = ""

    message = bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = 'Устанавливаем библиотеки...'
    )

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        self.layout.label(text=self.message)


class OilLeakPanel(bpy.types.Panel):
    bl_label = "OilLeakViz"
    bl_category = "OilLeakViz"
    bl_idname = "OilLeakViz"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Визуализация подводных струй"


    def draw(self, context):
        props = context.scene.settings
        props2 = context.scene.sf_props
        layout = self.layout
        obj = context.object
        row = layout.row()
        settings = context.scene.settings
        layout.label(text="Имя файла: {}".format('Не выбран файл' if (props2.selected_file==None) else props2.selected_file.split('/')[-1]))
        row = layout.row()
        row.operator(RunFileSelector.bl_idname, text="Выбрать файл")
        layout.prop(props, "type_enum")
        row = layout.row()
        row.operator(RunOperator.bl_idname, text="Создать блинчики")
        row = layout.row()
        row.operator(DebugOperator.bl_idname, text="Debug")
        row = layout.row()
        row.operator(RenderBubbles.bl_idname, text="Создать пузырьки")
        row = layout.row()
        #row.operator(GeometryNodesSetup.bl_idname, text="Визуализация ")
        row = layout.row()
        row.operator(DeleteContext.bl_idname, text="Очистить сцену")
        row = layout.row()
        row.label(text="Температурная шкала")
        row = layout.row()

        r = layout.row(align=True)
        for idx, item in enumerate(context.scene.color_collection, start=1):
            row.prop(item, "active", icon_value=item.icon, icon_only=True)
            if item.active == True:
                active_item = item
        row = layout.row(align=True)
        for i in range(0, 11):
            row.label(text=str(i*10))

        row = layout.row()
        row.label(text="Шкала концентрации")
        row = layout.row()

        r = layout.row(align=True)
        for idx, item in enumerate(context.scene.color_collection_2, start=1):
            r.prop(item, "active", icon_value=item.icon, icon_only=True)
            if item.active == True:
                active_item = item
        row = layout.row(align=True)
        for i in range(0, 11):
            row.label(text=str(i*10))








_classes = [
    Settings,
    OilLeakPanel,
    RunOperator,
    RunFileSelector,
    MessageBox,
    RenderSettings,
    RenderBubbles,
    DeleteContext,
    GeometryNodesSetup,
    ColorCollection,
    DebugOperator
]


color_palette_temperature = [
    (0, 0, 1, 1),
    (0.1, 0, 0.9, 1),
    (0.2, 0, 0.8, 1),
    (0.3, 0, 0.7, 1),
    (0.4, 0, 0.6, 1),
    (0.5, 0, 0.5, 1),
    (0.6, 0, 0.4, 1),
    (0.7, 0, 0.3, 1),
    (0.8, 0, 0.2, 1),
    (0.9, 0, 0.1, 1),
    (1, 0, 0, 1)]

color_palette_percent = [
    (0, 0, 0, 1),
    (0, 0.1, 0, 1),
    (0, 0.2, 0, 1),
    (0, 0.3, 0, 1),
    (0, 0.4, 0, 1),
    (0, 0.5, 0, 1),
    (0, 0.6, 0, 1),
    (0, 0.7, 0, 1),
    (0, 0.8, 0, 1),
    (0, 0.9, 0, 1),
    (0, 1, 0, 1)]

def register():
    install()
    for c in _classes: register_class(c)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=Settings)
    bpy.types.Scene.sf_props = SelectFileProp()
    bpy.types.Scene.render_settings = PointerProperty(type=RenderSettings)
    bpy.types.Scene.color_collection = bpy.props.CollectionProperty(type=ColorCollection)
    bpy.types.Scene.color_collection_2 = bpy.props.CollectionProperty(type=ColorCollection)

    # clear the collection
    if hasattr(bpy.context.scene, "color_collection"):
        bpy.context.scene.color_collection.clear()
    if hasattr(bpy.context.scene, "color_collection_2"):
        bpy.context.scene.color_collection_2.clear()

    # generate colors and icons
    pcoll = bpy.utils.previews.new()

    size = 64, 64
    for i, color in enumerate(color_palette_temperature):

        color_name = f"Color{i}"
        pixels = [*color] * size[0] * size[1]
        icon = pcoll.new(color_name) # name has to be unique!
        icon.icon_size = size
        icon.is_icon_custom = True
        icon.icon_pixels_float = pixels

        # add the item to the collection
        color_item = bpy.context.scene.color_collection.add()
        color_item.name = color_name
        color_item.color = color
        color_item.icon = pcoll[color_name].icon_id

    for i, color in enumerate(color_palette_percent):

        color_name = f"Colour{i}"
        pixels = [*color] * size[0] * size[1]
        icon = pcoll.new(color_name) # name has to be unique!
        icon.icon_size = size
        icon.is_icon_custom = True
        icon.icon_pixels_float = pixels

        # add the item to the collection
        color_item = bpy.context.scene.color_collection_2.add()
        color_item.name = color_name
        color_item.color = color
        color_item.icon = pcoll[color_name].icon_id






def unregister():
    for c in _classes: unregister_class(c)
    del bpy.types.Scene.settings
    del bpy.types.Scene.sf_props
    del bpy.types.Scene.render_props
    del bpy.types.Scene.color_collection
    del bpy.types.Scene.color_collection_2
    bpy.utils.previews.remove()



if __name__ == "__main__":
    register()
