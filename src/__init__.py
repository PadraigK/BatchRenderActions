import bpy
import os
from bpy.props import StringProperty, EnumProperty

# Globals to store state between renders
actions_to_render: list[bpy.types.Action] = []
current_action_index = 0
object_to_render = None  

def get_output_path(action_name, base_name, base_path):
    # Compose the directory for this action
    action_dir = os.path.join(base_path, action_name)
    os.makedirs(action_dir, exist_ok=True)
    # Return the full path (Blender will append frame numbers and extension)
    return os.path.join(action_dir, base_name)

def render_next_action():
    global current_action_index, actions_to_render, object_to_render 

    if current_action_index >= len(actions_to_render):
        print("All actions rendered.")
        if render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(render_complete_handler)
        return None  # <-- Needed for bpy.app.timers.register

    action = actions_to_render[current_action_index]
    obj = object_to_render
    scene = bpy.context.scene

    print(f"Rendering action {current_action_index+1}/{len(actions_to_render)}: {action.name}")

    # Set action on the active object
    if obj.animation_data is None:
        obj.animation_data_create()
    obj.animation_data.action = action

    # Set scene frame range
    f_start, f_end = int(action.frame_range[0]), int(action.frame_range[1])
    scene.frame_start = f_start
    scene.frame_end = f_end

    # Set output path
    props = scene.render_action_props
    base_path = bpy.path.abspath(props.output_directory or "//")
    output_path = get_output_path(action.name, props.filename_template, base_path)
    scene.render.filepath = output_path

    # Trigger render
    bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
    return None 

def render_complete_handler(scene):
    global current_action_index
    current_action_index += 1
    bpy.app.timers.register(render_next_action, first_interval=0.5)

def action_enum_items(self, context):
    items = []
    for act in bpy.data.actions:
        if not act.library:
            items.append((act.name, act.name, ""))
    if not items:
        items.append(('NONE', 'No Actions Found', ''))
    return items

class RenderActionProperties(bpy.types.PropertyGroup):
    filename_template: StringProperty(
        name="Filename Template",
        description="Template for frame filenames (use #### for frame numbers)",
        default="frame_####"
    )
    output_directory: StringProperty(
        name="Output Directory",
        description="Base directory for rendered animations",
        subtype='DIR_PATH',
        default="//"
    )
    action_to_render: EnumProperty(
        name="Action",
        description="Select an action to render",
        items=action_enum_items
    )

class RENDER_PT_ActionRenderPanel(bpy.types.Panel):
    bl_label = "Render Actions"
    bl_idname = "RENDER_PT_action_render_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Render Actions'

    def draw(self, context):
        layout = self.layout
        props = context.scene.render_action_props
        obj = context.object

        # First two fields
        layout.prop(props, "filename_template")
        layout.prop(props, "output_directory")

        # Divider/spacer
        layout.separator()

        # Action dropdown
        layout.prop(props, "action_to_render")

        # Render single button
        row = layout.row()
        row.enabled = obj is not None and obj in context.selected_objects and props.action_to_render != 'NONE'
        row.operator("render.single_action")

        # Another divider/spacer
        layout.separator()

        # Render all button
        row = layout.row()
        row.enabled = obj is not None and obj in context.selected_objects
        row.operator("render.batch_actions")

class RENDER_OT_BatchRenderActions(bpy.types.Operator):
    bl_idname = "render.batch_actions"
    bl_label = "Render All Actions"
    bl_description = "Render each action as a full animation using INVOKE_DEFAULT"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global actions_to_render, current_action_index, object_to_render

        obj = context.object
        if not obj or not obj.animation_data:
            self.report({'ERROR'}, "No object with animation data selected.")
            return {'CANCELLED'}

        actions_to_render = [a for a in bpy.data.actions if not a.library]
        current_action_index = 0
        object_to_render = obj

        if not actions_to_render:
            self.report({'ERROR'}, "No actions found to render.")
            return {'CANCELLED'}

        if render_complete_handler not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(render_complete_handler)

        render_next_action()
        return {'FINISHED'}

class RENDER_OT_SingleActionRender(bpy.types.Operator):
    bl_idname = "render.single_action"
    bl_label = "Render Selected Action"
    bl_description = "Render only the selected action as an animation"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        props = context.scene.render_action_props
        if not obj or not obj.animation_data:
            self.report({'ERROR'}, "No object with animation data selected.")
            return {'CANCELLED'}

        action_name = props.action_to_render
        action = bpy.data.actions.get(action_name)
        if not action or action_name == 'NONE':
            self.report({'ERROR'}, "Selected action not found.")
            return {'CANCELLED'}

        # Set action on the active object
        if obj.animation_data is None:
            obj.animation_data_create()
        obj.animation_data.action = action

        # Set scene frame range
        scene = context.scene
        f_start, f_end = int(action.frame_range[0]), int(action.frame_range[1])
        scene.frame_start = f_start
        scene.frame_end = f_end

        # Set output path
        base_path = bpy.path.abspath(props.output_directory or "//")
        output_path = get_output_path(action.name, props.filename_template, base_path)
        scene.render.filepath = output_path

        # Trigger render (no callback needed)
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        return {'FINISHED'}

classes = (
    RenderActionProperties,
    RENDER_PT_ActionRenderPanel,
    RENDER_OT_BatchRenderActions,
    RENDER_OT_SingleActionRender,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.render_action_props = bpy.props.PointerProperty(type=RenderActionProperties)

def unregister():
    if render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(render_complete_handler)
    del bpy.types.Scene.render_action_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
