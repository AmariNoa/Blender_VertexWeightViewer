bl_info = {
    "name": "Vertex Weight Viewer (Sidebar)",
    "author": "AmariNoa (with ChatGPT)",
    "version": (1, 5),
    "blender": (3, 6, 0),
    "location": "3D View > Sidebar > Vertex Weights",
    "description": "Display weights of selected vertices in the sidebar",
    "category": "3D View"
}

import bpy
import bmesh
from bpy.app.translations import pgettext, register as i18n_register, unregister as i18n_unregister

# 翻訳辞書
translations = {
    "ja_JP": {
        ("*", "Vertex Weights"): "頂点ウェイト",
        ("*", "Clear Weights"): "選択した頂点のウェイトをリセット",
        ("*", "No vertices selected"): "頂点が選択されていません",
        ("*", "No weights assigned"): "ウェイトが割り当てられていません",
        ("*", "Vertex"): "頂点",
        ("*", "Weights cleared"): "ウェイトを削除しました",
    }
}

# ウェイト削除用オペレーター
class VWV_OT_ClearWeights(bpy.types.Operator):
    bl_idname = "vwv.clear_weights"
    bl_label = pgettext("Clear Weights")

    def execute(self, context):
        obj = context.object
        if not obj or obj.type != 'MESH' or obj.mode != 'EDIT':
            return {'CANCELLED'}

        mesh = obj.data

        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            self.report({'ERROR'}, "Failed to switch to Object Mode")
            return {'CANCELLED'}

        selected_indices = [v.index for v in mesh.vertices if v.select]
        groups = obj.vertex_groups

        for index in selected_indices:
            for group in groups:
                group.remove([index])

        try:
            bpy.ops.object.mode_set(mode='EDIT')
        except RuntimeError:
            self.report({'ERROR'}, "Failed to switch back to Edit Mode")
            return {'CANCELLED'}

        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
        self.report({'INFO'}, pgettext("Weights cleared"))
        return {'FINISHED'}

# パネル表示
class VIEW3D_PT_vertex_weights(bpy.types.Panel):
    bl_label = pgettext("Vertex Weights")
    bl_idname = "VIEW3D_PT_vertex_weights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vertex Weights"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        mesh = obj.data

        # 削除ボタン
        layout.operator("vwv.clear_weights", text=pgettext("Clear Weights"), icon='X')

        bm = bmesh.from_edit_mesh(mesh)
        selected_verts = sorted([v for v in bm.verts if v.select], key=lambda v: v.index)

        if not selected_verts:
            layout.label(text=pgettext("No vertices selected"))
            return

        col = layout.column()
        col.use_property_split = True

        groups = obj.vertex_groups

        for v in selected_verts:
            v_index = v.index
            vertex = mesh.vertices[v_index]

            weights = []
            for g in vertex.groups:
                weight = g.weight
                if weight > 0:
                    name = groups[g.group].name
                    weights.append((name, weight))

            box = col.box()
            box.label(text=f"{pgettext('Vertex')} {v_index}")

            if not weights:
                box.label(text=pgettext("No weights assigned"))
            else:
                weights.sort(key=lambda x: x[1], reverse=True)
                for name, weight in weights:
                    box.label(text=f"{weight:.4f} : {name}")

# 登録
def register():
    bpy.utils.register_class(VWV_OT_ClearWeights)
    bpy.utils.register_class(VIEW3D_PT_vertex_weights)
    i18n_register(__name__, translations)

def unregister():
    bpy.utils.unregister_class(VWV_OT_ClearWeights)
    bpy.utils.unregister_class(VIEW3D_PT_vertex_weights)
    i18n_unregister(__name__)
