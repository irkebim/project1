import bpy
from mathutils import Vector
from bpy.types import Operator

def offset_edge(p1, p2, distance, direction='OUT'):
    edge_vec = (p2 - p1).to_2d()
    normal = Vector((-edge_vec.y, edge_vec.x)).normalized()
    offset = Vector((normal.x, normal.y, 0)) * distance
    return (p1 - offset, p2 - offset) if direction == 'OUT' else (p1 + offset, p2 + offset)

def intersect_edges(a1, a2, b1, b2):
    x1, y1 = a1.x, a1.y
    x2, y2 = a2.x, a2.y
    x3, y3 = b1.x, b1.y
    x4, y4 = b2.x, b2.y
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return Vector((px, py, 0))

class IRKEBIM_OT_OffsetCurve(Operator):
    bl_idname = "irkebim.offset_curve"
    bl_label = "Create Exact Offset Curve"
    bl_description = "Generate a precise offset from selected curve or mesh"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type in {'CURVE', 'MESH'}

    def execute(self, context):
        scene = context.scene
        distance = scene.offset_distance / 1000.0  # mm → m
        direction = scene.offset_direction
        obj = context.active_object

        if obj.type == 'MESH':
            bpy.ops.object.convert(target='CURVE')
            obj = context.active_object

        if obj.type != 'CURVE':
            self.report({'ERROR'}, "Only curve or mesh (plane) supported")
            return {'CANCELLED'}

        curve = obj.data
        matrix = obj.matrix_world

        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            points = spline.points
            is_cyclic = spline.use_cyclic_u
            world_points = [(matrix @ Vector((pt.co.x, pt.co.y, pt.co.z))) for pt in points]
            if is_cyclic:
                world_points.append(world_points[0])
            offset_edges_list = []
            for i in range(len(world_points) - 1):
                p1, p2 = world_points[i], world_points[i+1]
                offset_p1, offset_p2 = offset_edge(p1, p2, distance, direction)
                offset_edges_list.append((offset_p1, offset_p2))
            new_points = []
            for i in range(len(offset_edges_list)):
                a1, a2 = offset_edges_list[i - 1]
                b1, b2 = offset_edges_list[i]
                inter = intersect_edges(a1, a2, b1, b2)
                if inter is None:
                    inter = b1
                new_points.append(inter)
            new_curve_data = bpy.data.curves.new(name=obj.name + "_Offset", type='CURVE')
            new_curve_data.dimensions = '3D'
            new_spline = new_curve_data.splines.new(type='POLY')
            new_spline.points.add(len(new_points) - 1)
            for i, pt in enumerate(new_points):
                new_spline.points[i].co = (pt.x, pt.y, pt.z, 1)
            new_spline.use_cyclic_u = is_cyclic
            new_obj = bpy.data.objects.new(obj.name + "_Offset", new_curve_data)
            context.collection.objects.link(new_obj)

        self.report({'INFO'}, "Offset curve created")
        return {'FINISHED'}

# 자동 등록용 Scene 프로퍼티
Property_Scene_offset_distance = bpy.props.FloatProperty(
    name="Offset Distance (mm)",
    description="Distance in mm",
    default=500.0,
    min=1.0
)

Property_Scene_offset_direction = bpy.props.EnumProperty(
    name="Offset Direction",
    items=[
        ('OUT', "Outward", "Offset to outside"),
        ('IN', "Inward", "Offset to inside")
    ],
    default='OUT'
)
