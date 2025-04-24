import bpy
import os
from ..config import ADDON_ID

class IRKEBIM_OT_ImportImage(bpy.types.Operator):
    bl_idname = "irkebim.import_image"
    bl_label = "Import Plan Image"
    bl_description = "Import image with exact size. Center_Line (semi-transparent) is parent of Plan_Main (opaque)."
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file path specified")
            return {'CANCELLED'}

        filename = os.path.basename(self.filepath)
        image_name = os.path.splitext(filename)[0]

        try:
            img = bpy.data.images.load(self.filepath, check_existing=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load image: {e}")
            return {'CANCELLED'}

        width, height = img.size
        if width == 0 or height == 0:
            self.report({'ERROR'}, "Invalid image resolution")
            return {'CANCELLED'}

        # ===== 크기 계산 =====
        # 모든 객체에 동일하게 적용할 크기 미리 계산
        size_x = width * 0.001  # 1px = 1mm
        size_y = height * 0.001

        # ===== Center_Line 생성 =====
        bpy.ops.mesh.primitive_plane_add(size=2)  # 기본 크기 2
        center = context.active_object
        center.name = "Center_Line"
        center.scale.x = size_x / 2  # 스케일 적용 (size/2 이유: 플레인 기본 크기가 2)
        center.scale.y = size_y / 2
        
        # 환경설정에서 투명도
        addon_prefs = bpy.context.preferences.addons[ADDON_ID].preferences
        opacity = getattr(addon_prefs, "image_opacity", 0.5)

        mat_center = bpy.data.materials.new(name="Center_Line_Mat")
        mat_center.use_nodes = True
        bsdf_center = mat_center.node_tree.nodes.get("Principled BSDF")
        tex_center = mat_center.node_tree.nodes.new("ShaderNodeTexImage")
        tex_center.image = img
        mat_center.node_tree.links.new(bsdf_center.inputs["Base Color"], tex_center.outputs["Color"])
        bsdf_center.inputs["Alpha"].default_value = opacity
        mat_center.blend_method = 'BLEND'
        if hasattr(mat_center, 'shadow_method'):
            mat_center.shadow_method = 'NONE'
        center.data.materials.clear()
        center.data.materials.append(mat_center)

        # ===== Plan_Main 생성 =====
        bpy.ops.mesh.primitive_plane_add(size=2)  # 중요: 1이 아니라 2!
        plan = context.active_object
        plan.name = image_name + "_Main"
        plan.scale.x = size_x / 2  # 동일한 크기 적용
        plan.scale.y = size_y / 2

        mat_main = bpy.data.materials.new(name=image_name + "_Mat_Main")
        mat_main.use_nodes = True
        bsdf_main = mat_main.node_tree.nodes.get("Principled BSDF")
        tex_main = mat_main.node_tree.nodes.new("ShaderNodeTexImage")
        tex_main.image = img
        mat_main.node_tree.links.new(bsdf_main.inputs["Base Color"], tex_main.outputs["Color"])
        bsdf_main.inputs["Alpha"].default_value = 1.0  # 불투명
        mat_main.blend_method = 'BLEND'
        if hasattr(mat_main, 'shadow_method'):
            mat_main.shadow_method = 'NONE'
        plan.data.materials.append(mat_main)

        # ===== 계층 구조 설정 =====
        # 부모-자식 관계 설정 전에 두 객체의 위치와 스케일 확인
        plan.location = center.location.copy()  # 위치 정확히 일치시킴
        plan.location.z = -0.001  # Plan_Main의 z값을 -0.001로 설정하여 Center_Line 아래에 위치
        
        # 부모-자식 관계 설정
        plan.parent = center
        # 부모-자식 관계 설정 후 자식 객체의 로컬 변환을 유지
        plan.matrix_parent_inverse = center.matrix_world.inverted()

        # 컬렉션 정리
        plan_col = self.get_or_create_collection("Plan")
        line_col = self.get_or_create_collection("Line")
        plan_col.objects.link(plan)
        line_col.objects.link(center)

        self.safe_unlink(context, plan)
        self.safe_unlink(context, center)

        context.view_layer.objects.active = center
        center.select_set(True)
        plan.select_set(True)

        return {'FINISHED'}

    def get_or_create_collection(self, name):
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        return col

    def safe_unlink(self, context, obj):
        if obj.name in context.scene.collection.objects:
            context.scene.collection.objects.unlink(obj)