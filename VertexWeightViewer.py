bl_info = {
    "name": "Vertex Weight Viewer (Sidebar)",
    "author": "AmariNoa (with ChatGPT)",
    "version": (1, 4),
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
        ("*", "No vertices selected"): "頂点が選択されていません",
        ("*", "No weights assigned"): "ウェイトが割り当てられていません",
        ("*", "Vertex"): "頂点",
    }
}

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

def register():
    bpy.utils.register_class(VIEW3D_PT_vertex_weights)
    i18n_register(__name__, translations)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_vertex_weights)
    i18n_unregister(__name__)
