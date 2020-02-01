bl_info = {
    "name": "Lua Animations API animation",
    "description": "Exports an animation for Jetboom's Lua Animations API.",
    "author": "Buu342",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "File > Export > LUAANIMATIONAPI",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

import bpy, os
import struct 
from bpy import context
import mathutils
import math

# Check if the given bone has a keyframe
def isKeyframe(ob, frame, data_path, array_index=-1):
    if ob is not None and ob.animation_data is not None and ob.animation_data.action is not None:
        for fcu in ob.animation_data.action.fcurves:
            if fcu.data_path == data_path:
                if array_index == -1 or fcu.array_index == array_index:
                    return frame in (p.co.x for p in fcu.keyframe_points)
    return False


# Check if a keyframe exists in a specific frame
def existsKeyframe(frame):
    obj = bpy.context.object
    action = obj.animation_data.action

    for fcurve in action.fcurves:
        if frame in (p.co.x for p in fcurve.keyframe_points):
            return True
    return False


# Remove newlines and tabs from a file
def compactFile(file):
    lines = []
    replacements = {'\n':'', '\t':''}
    
    with open(file) as infile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            lines.append(line)
    infile.close()
    
    with open(file, 'w') as outfile:
        for line in lines:
            outfile.write(line)
    outfile.close()
    
    
# No armature error
def popupSuccess(self, context):
    self.layout.label("File exported successfully!")
    
# No armature popup
def popupNoArmature(self, context):
    self.layout.label("You need to select an armature with keyframes!")

# Write the data to a file
def writeObject(self, context):
    object = bpy.context.object
    scene = bpy.context.scene
    startFrame = scene.frame_start
    endFrame = scene.frame_end
    currentFrame = scene.frame_current
    lastFrame = 0
    frameRate = scene.render.fps
    try:
        animName = object.animation_data.action.name
    except:
        bpy.context.window_manager.popup_menu(popupNoArmature, title="Error", icon='ERROR')
        return {'CANCELLED'}

    with open(self.filepath, 'w') as file:
        file.write("RegisterLuaAnimation('%s', {\n\tFrameData = {\n" % animName)
        
        # First get a list of all bones that get animated
        boneList = []
        for f in range(endFrame-startFrame+1):
            scene.frame_set(f)
            for pbone in object.pose.bones:
                if not pbone.name in boneList:
                    if isKeyframe(object, f, pbone.path_from_id("location")):
                        boneList.append(pbone.name)
                    
        # If requested, write the first frame as blank
        if self.setting_firstframeblank:
            file.write("\t\t{\n\t\t\tBoneInfo = {\n")
            for b in boneList:
                file.write("\t\t\t\t['%s'] = {\n\t\t\t\t},\n" % b)
            file.write("\t\t\t},\n\t\t\tFrameRate = 100\n\t\t},\n")
            
        # Now, cycle trough all the animated frames and add the bone transformations
        for f in range(endFrame-startFrame+1):
            if f==0 and (not self.setting_firstframe or self.setting_firstframeblank):
                continue
            scene.frame_set(f)
            wroteLine = False
                
            for pbone in object.pose.bones:
                if not pbone.name in boneList:
                    continue
                if existsKeyframe(f):
                    if not wroteLine:
                        file.write("\t\t{\n\t\t\tBoneInfo = {\n")
                        wroteLine = True
                    else:
                        file.write(",\n")
                    loc, rot, sca = pbone.matrix_basis.decompose()
                    rot = pbone.matrix_basis.to_euler()
                    file.write("\t\t\t\t['%s'] = {\n" % pbone.name)
                    if (loc.z != 0):
                        file.write("\t\t\t\t\tMU = %s,\n" % round(loc.z, 2))
                    if (rot.z != 0):
                        file.write("\t\t\t\t\tRU = %s,\n" % round(math.degrees(rot.z)))
                    if (loc.y != 0):
                        file.write("\t\t\t\t\tMR = %s,\n" % round(loc.y, 2))
                    if (rot.y != 0):
                        file.write("\t\t\t\t\tRR = %s\n" % round(math.degrees(rot.y)))
                    if (loc.x != 0):
                        file.write("\t\t\t\t\tMF = %s,\n" % round(loc.x, 2))
                    if (rot.x != 0):
                        file.write("\t\t\t\t\tRF = %s,\n" % round(math.degrees(rot.x)))
                    file.write("\t\t\t\t}")

            # Write the frameRate
            if wroteLine:
                finalFPS = "100"
                if f-lastFrame != 0:
                    finalFPS = str(round(frameRate/(f-lastFrame), 2))
                file.write("\n\t\t\t},\n\t\t\tFrameRate = %s\n\t\t},\n" % finalFPS)
                lastFrame = f
                    
        # Finish by setting the mode
        file.write("\t},\n\tType = %s\n})" % self.setting_mode)

    # Close the file
    file.close()
    
    # If we enabled compact mode, compact the file
    if (self.setting_compact):
        compactFile(self.filepath)
        
    # Reset the frame position and return that we finished
    scene.frame_set(currentFrame)
    bpy.context.window_manager.popup_menu(popupSuccess, title="Success", icon='INFO')
    return {'FINISHED'}


# Our export function
class ObjectExport(bpy.types.Operator):
    """Exports an animation for Jetboom's Lua Animations API"""
    bl_idname = "object.export_luaanimationsapi"
    bl_label = "Lua Animations API Export" # The text on the export button
    bl_options = {'REGISTER', 'UNDO'}
    
    # Filepath variables
    filepath = bpy.props.StringProperty(subtype='FILE_PATH')    
    filename_ext = ".lua"
    filter_glob      = bpy.props.StringProperty(default="*.lua", options={'HIDDEN'}, maxlen=255)
    
    # Settings
    setting_mode     = bpy.props.EnumProperty(
        name="Animation type",
        items=(('TYPE_GESTURE',  "Gesture", "Gestures are keyframed animations that use the current position and angles of the bones. They play once and then stop automatically."),
               ('TYPE_POSTURE',  "Posture", "Postures are static animations that use the current position and angles of the bones. They stay that way until manually stopped."),
               ('TYPE_STANCE',   "Stance",  "Stances are keyframed animations that use the current position and angles of the bones. They play forever until manually stopped."),
               ('TYPE_SEQUENCE', "Seqence", "Sequences are keyframed animations that use the origin and angles of the entity. They play forever until manually stopped.")
               ),
        description="Select the animation type",
        default='TYPE_GESTURE',
        )
    setting_firstframe      = bpy.props.BoolProperty(name="Include first frame?", description="Include the first frame of animation?", default=True)
    setting_firstframeblank = bpy.props.BoolProperty(name="Blank first frame?", description="Adds a frame of all the untouched bones with no transformations to the first frame.", default=False)
    setting_compact         = bpy.props.BoolProperty(name="Compact?", description="Removes all formatting from the exported file (no tabs or new lines).", default=False)
    
    # Code to run when the export button is pressed
    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)            
        writeObject(self, context)
        return {'FINISHED'}

    # Code to run when the export option is selected
    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.path.display_name_from_filepath(bpy.data.filepath), self.filename_ext)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Add trigger into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ObjectExport.bl_idname, text="Lua Animations API Animation (.lua)")
    

# Class registerer
def register():
    bpy.utils.register_class(ObjectExport)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

# Class unregisterer
def unregister():
    bpy.utils.unregister_class(ObjectExport)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

# Main function
if __name__ == "__main__":
    register()