# Lua Animations API Exporter
<p align="center">
<img src="https://i.imgur.com/itf0wob.gif" width="252" height="148"><img src="https://i.imgur.com/Jai4GjB.gif" width="252" height="148">
</p>

An exporter that turns animations in Blender into the format used by [JetBoom's Lua Animations API](https://github.com/JetBoom/animationsapi) for Garry's Mod. This was created because I find Blender much easier to use for animation than the built in editor provided by the API.

The exporter works on any version of Blender that is older than 2.7 (inclusive). When installing in 2.7, you will get a warning that this plugin is designed for a later version, **you can safely ignore this warning**.

The exporter itself can be a bit clunky, since I am not great with Blender's API. I haven't tested every possible edge case so if any problems arise, feel free to open an Issue. It requires that the base animation which the player is using be set to the default bone pose in Blender. For instance, if you want make a gesture animation for when the player is holding a weapon with the dual hold type, then you need to import that animation into Blender and set the rest pose to that. For an example of what I mean, check the example folder provided.

### Notes on reccomended usage
* Only keyframe the bones you actually modify. Otherwise you will have unecessary bones in your exported lua file
* I **highly** reccomend you animate with linear interpolation. To do that, click on the bottom left icon and switch to the "Graph Editor". On the bottom left, select Channel -> Extrapolation Mode -> Linear Extrapolation. While the animations API uses Consine by default, it's not very good. This is a more accurate representation.
* Do not bake animations before exporting. This will create hundreds of unecessary keyframes.
* I would not reccomend animating using Inverse Kinematics unless you know exactly what you're doing. The animations are not baked on export so bones affected by your IK constraints will not have their changes exported. If you do, you'll have to bake the animation yourself and then delete all unecessary keyframes manually. I should be able to automate this in a future update, however.

## Installation
1) Download the python file.
2) Open Blender. Go to File -> User Preferences.
3) Go to Add-ons and click "Install from File..." on the bottom left.
4) Locate the python file and click the "Install from File..." on the top right.
5) Ensure that the checkbox named "Import-Export: Lua Animations API animation" is checked.
6) Press the "Save User Settings" button on the bottom left.

## How to export
1) Select the armature with the animation you want to export
2) Ensure the animation has the name you want.
3) Click File -> Export -> Lua Animations API Animation (.lua)
4) Ensure the settings on the bottom left are to your liking
5) Ensure the file path and file name is to your liking
6) Click "Lua Animations API Export"
7) If no errors occured, a dialog box saying "File Exported Successfully" should appear on your mouse.
