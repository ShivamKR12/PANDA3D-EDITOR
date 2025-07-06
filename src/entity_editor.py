from panda3d.core import NodePath, Loader
import toml
import os
import importlib.util

import os

import zipfile
import toml
from panda3d.core import NodePath  # Assuming NodePath is from panda3d.core

from panda3d.core import PointLight, Spotlight, DirectionalLight, AmbientLight, Vec4, Vec3

class MapLoader:
    def __init__(self, world):
        self.world = world

    def load_level_folder(self, project_folder):
        """
        Loads the project from a folder (not a .map file).
        Expects the level data in <project_folder>/level/ and settings in <project_folder>/settings/.
        """
        level_dir = os.path.join(project_folder, "level")
        settings_dir = os.path.join(project_folder, "settings")
        if not os.path.exists(level_dir):
            print(f"❌ Level folder not found: {level_dir}")
            return False
        loader_instance = Load(self.world)
        loader_instance.load_project_from_folder_toml(level_dir, self.world.render)
        print("🎮 Scene loaded successfully from folder!")
        # Optionally, load settings here if needed
        return True

# ------------------------------------------------------------------------------
# Load class: Reads TOML files from a folder and reconstructs scene objects.
# (You must adjust these functions so that they correctly match your saved data.)
# ------------------------------------------------------------------------------

class Load:
    def __init__(self, world):
        self.world = world

    def load_lights_from_toml(self, file_path: str, render: NodePath):
        """
        Load lights from a TOML file and attach them to the render node.
        """
        if not file_path or not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, "r") as file:
            lights_data = toml.load(file)

        for light_name, light_data in lights_data.items():
            light_type = light_data.get("type", "point")
            position = light_data.get("position", {"x": 0, "y": 0, "z": 0})
            color = light_data.get("color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})

            if light_type == "point":
                light = PointLight(light_name)
            elif light_type == "directional":
                light = DirectionalLight(light_name)
            elif light_type == "ambient":
                light = AmbientLight(light_name)
            elif light_type == "spot":
                light = Spotlight(light_name)
                fov = light_data.get("fov", 45.0)
                light.getLens().setFov(fov)
            else:
                print(f"Unsupported light type: {light_type}")
                continue

            light.setColor(Vec4(color["r"], color["g"], color["b"], color["a"]))
            light_node = render.attachNewNode(light)
            light_node.setPos(Vec3(position["x"], position["y"], position["z"]))

            if light_type in ["directional", "spot"]:
                direction = light_data.get("direction", {"x": 0, "y": -1, "z": 0})
                light_node.lookAt(Vec3(direction["x"], direction["y"], direction["z"]))

            render.setLight(light_node)
        print(f"Lights loaded from {file_path}")

    def load_project_from_folder_toml(self, input_folder: str, root_node: NodePath):
        """
        Loads a project (scene) from a folder containing TOML files.
        This example first loads lights, then iterates over all TOML files in the folder
        to reconstruct scene entities.
        """
        if not os.path.exists(input_folder):
            print(f"❌ Input folder {input_folder} does not exist.")
            return []

        # First, load lights if available.
        lights_toml = os.path.join(input_folder, "lights", "lights.toml")
        if os.path.exists(lights_toml):
            self.load_lights_from_toml(lights_toml, root_node)
        
        # Iterate over other TOML files in the folder to load entities.
        entities = []
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml") and file_name != "lights.toml":
                file_path = os.path.join(input_folder, file_name)
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)
                
                # Example: extract transform and load a model if available.
                name = entity_data.get("name", "Unnamed")
                model_path = entity_data.get("entity_model", "")
                transform = entity_data.get("transform", {})
                pos = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rot = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 1, "y": 1, "z": 1})

                # Create a new node for the entity.
                entity_node = root_node.attachNewNode(name)
                if model_path and os.path.exists(model_path):
                    # Load and reparent the model.
                    model = loader.loadModel(os.path.relpath(model_path))
                    model.reparentTo(entity_node)
                    print(f"✅ Loaded model for {name}: {model_path}")
                else:
                    print(f"⚠️ Model path not found for {name}: {model_path}")

                entity_node.setPos(pos["x"], pos["y"], pos["z"])
                entity_node.setHpr(rot["h"], rot["p"], rot["r"])
                entity_node.setScale(scale["x"], scale["y"], scale["z"])
                entities.append(entity_node)
                print(f"✅ Entity '{name}' loaded from {file_name}")

        return entities

    def load_script(self, script_path: str, node: NodePath):
        """
        Dynamically load a script from a Python file and attach it to a node.
        """
        spec = importlib.util.spec_from_file_location("script", script_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)
        if hasattr(script_module, "Script"):
            return script_module.Script(node)
        else:
            raise AttributeError(f"The script at {script_path} does not define a 'Script' class.")
        
    def load_ui_from_folder_toml(self, input_folder: str, root_node: NodePath):
        """
        Load entities from TOML files, reconstruct them in the scene graph, attach models, scripts, and build a list of entities.
        Args:
            input_folder (str): Folder where TOML files are stored.
            root_node (NodePath): The root node to attach loaded entities to.
        Returns:
            list: A list of dictionaries containing all entity data.
        """
        if not os.path.exists(input_folder):
            print(f"Input folder {input_folder} does not exist.")
            return []

        entities = []
        
        with open(input_folder, "r") as file:
            input_folder = file.read().strip()

        # Sanitize the input_folder path
        input_folder = input_folder.replace('\0', '')

        # Debugging: Print the sanitized input_folder path
        print(f"Sanitized input folder path: {input_folder}")

        # Iterate over all TOML files in the input folder
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):
                file_path = os.path.join(os.path.relpath(input_folder), file_name)
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Extract data from the entity
                name = entity_data.get("name", "Unnamed")
                entity_id = entity_data.get("id", None)
                model_path = entity_data.get("entity_model", "")
                entity_type = entity_data.get("type", "")
                widget_type = entity_data.get("widget_type", "")
                action = entity_data.get("action", "")
                properties = entity_data.get("properties", {})
                specials = properties.get("specials", "")
                __UIEditorLabel__ = specials.get("__UIEditorLabel__", "")
                __UIEditorButton__ = specials.get("__UIEditorButton__", "")
                
                if __UIEditorLabel__ != "":
                    text = __UIEditorLabel__.get("text", "")
                
                if __UIEditorButton__ != "":
                    text = __UIEditorButton__.get("text", "")
                    
                coloring = entity_data.get("coloring", {})
                frame_color = coloring.get("frameColor1", {"r": 0.5, "g": 0.5, "b": 0.5})
                color = coloring.get("text_fg1", {"r": 1.0, "g": 1.0, "b": 1.0})
                image = entity_data.get("image", "")
                parent = entity_data.get("parent", "")

                transform = entity_data.get("transform", {})
                isCanvas = entity_data.get("isCanvas", False)
                isLabel = entity_data.get("isLabel", False)
                isButton = entity_data.get("isButton", False)
                isImage = entity_data.get("isImage", False)
                #TODO load UI object to ui editor

                # Set transformation properties
                position = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rotation = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 0.1, "y": 0.1, "z": 0.1})
                parent = properties.get("parent", self.world.render2d)
                script_paths = properties.get("script_paths", "")
                s_property = properties.get("script_properties", "")

                if widget_type == "l":
                    self.widget = self.world.recreate_widget(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "l")
                    
                if widget_type == "b":
                    self.widget = self.world.recreate_button(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "b")
                    
                if widget_type == None:
                    self.widget = NodePath("None")
                    
                # Set properties
                for key, value in properties.items():
                    self.widget.set_python_tag(key, value)
                for s in script_paths:
                    prop = {}

                    for attr, value in s_property.items():
                        prop[attr] = (value)
                        print("iiii:", value)
                    prop.clear()
                # Append entity data to the list
                entities.append({
                    "name": name,
                    "id": entity_id,
                    "transform": transform,
                    "properties": properties,
                    "model": model_path
                })

                self.world.hierarchy_tree1.clear()
                self.world.populate_hierarchy(self.world.hierarchy_tree1, self.world.render2d)
                
                print(f"Entity '{name}' with ID '{entity_id}' loaded.")

        return entities

    def load_ui_from_folder_toml(self, input_folder: str, root_node: NodePath):
        """
        Load entities from TOML files, reconstruct them in the scene graph, attach models, scripts, and build a list of entities.
        Args:
            input_folder (str): Folder where TOML files are stored.
            root_node (NodePath): The root node to attach loaded entities to.
        Returns:
            list: A list of dictionaries containing all entity data.
        """
        if not os.path.exists(input_folder):
            print(f"Input folder {input_folder} does not exist.")
            return []

        entities = []
        
        with open(input_folder, "r") as file:
            input_folder = file.read().strip()

        # Iterate over all TOML files in the input folder
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):
                file_path = os.path.join(os.path.relpath(input_folder), file_name)
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Extract data from the entity
                name = entity_data.get("name", "Unnamed")
                entity_id = entity_data.get("id", None)
                model_path = entity_data.get("entity_model", "")
                entity_type = entity_data.get("type", "")
                widget_type = entity_data.get("widget_type", "")
                action = entity_data.get("action", "")
                properties = entity_data.get("properties", {})
                specials = properties.get("specials", "")
                __UIEditorLabel__ = specials.get("__UIEditorLabel__", "")
                __UIEditorButton__ = specials.get("__UIEditorButton__", "")
                
                if __UIEditorLabel__ != "":
                    text = __UIEditorLabel__.get("text", "")
                
                if __UIEditorButton__ != "":
                    text = __UIEditorButton__.get("text", "")
                    
                coloring = entity_data.get("coloring", {})
                frame_color = coloring.get("frameColor1", {"r": 0.5, "g": 0.5, "b": 0.5})
                color = coloring.get("text_fg1", {"r": 1.0, "g": 1.0, "b": 1.0})
                image = entity_data.get("image", "")
                parent = entity_data.get("parent", "")

                transform = entity_data.get("transform", {})
                isCanvas = entity_data.get("isCanvas", False)
                isLabel = entity_data.get("isLabel", False)
                isButton = entity_data.get("isButton", False)
                isImage = entity_data.get("isImage", False)
                #TODO load UI object to ui editor

                # Set transformation properties
                position = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rotation = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 0.1, "y": 0.1, "z": 0.1})
                parent = properties.get("parent", self.world.render2d)
                script_paths = properties.get("script_paths", "")
                s_property = properties.get("script_properties", "")

                if widget_type == "l":
                    self.widget = self.world.recreate_widget(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "l")
                    
                if widget_type == "b":
                    self.widget = self.world.recreate_button(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "b")
                    
                if widget_type == None:
                    self.widget = NodePath("None")
                    
                # Set properties
                for key, value in properties.items():
                    self.widget.set_python_tag(key, value)
                for s in script_paths:
                    prop = {}

                    for attr, value in s_property.items():
                        prop[attr] = (value)
                        print("iiii:", value)
                    prop.clear()
                # Append entity data to the list
                entities.append({
                    "name": name,
                    "id": entity_id,
                    "transform": transform,
                    "properties": properties,
                    "model": model_path
                })

                self.world.hierarchy_tree1.clear()
                self.world.populate_hierarchy(self.world.hierarchy_tree1, self.world.render2d)
                
                print(f"Entity '{name}' with ID '{entity_id}' loaded.")

        return entities



class Save:
    def __init__(self, world):
        self.world = world

    def save_lights_to_toml(self, lights, file_path):
        """
        Save all lights in the scene to a TOML file.
        """
        lights_data = {}
        for i, light_node in enumerate(lights):
            light = light_node.node()
            light_data = {
                "type": "",
                "position": {
                    "x": light_node.getX(),
                    "y": light_node.getY(),
                    "z": light_node.getZ(),
                },
                "color": {
                    "r": light.getColor()[0],
                    "g": light.getColor()[1],
                    "b": light.getColor()[2],
                    "a": light.getColor()[3],
                },
            }
            # Determine light type
            from panda3d.core import PointLight, AmbientLight, DirectionalLight, Spotlight
            if isinstance(light, PointLight):
                light_data["type"] = "point"
            elif isinstance(light, AmbientLight):
                light_data["type"] = "ambient"
            elif isinstance(light, DirectionalLight):
                light_data["type"] = "directional"
                light_data["direction"] = {
                    "x": light_node.getQuat().getForward()[0],
                    "y": light_node.getQuat().getForward()[1],
                    "z": light_node.getQuat().getForward()[2],
                }
            elif isinstance(light, Spotlight):
                light_data["type"] = "spot"
                light_data["direction"] = {
                    "x": light_node.getQuat().getForward()[0],
                    "y": light_node.getQuat().getForward()[1],
                    "z": light_node.getQuat().getForward()[2],
                }
                light_data["fov"] = light.getLens().getFov()[0]
            else:
                print(f"Unsupported light type for light_{i+1}")
                continue

            lights_data[f"light_{i+1}"] = light_data

        # Write out the TOML file
        with open(file_path, "w") as file:
            toml.dump(lights_data, file)
        print(f"Lights saved to {file_path}")

    def save_scene_to_toml(self, root_node: NodePath, output_folder: str):
        """
        Traverse the scene graph, extract entity data, and save each entity to its own TOML file.
        Also saves lights into a subfolder.
        """
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        # Save lights first
        lights = [node for node in root_node.find_all_matches('**/+Light')]
        lights_folder = os.path.join(output_folder, "lights")
        os.makedirs(lights_folder, exist_ok=True)
        lights_file = os.path.join(lights_folder, "lights.toml")
        self.save_lights_to_toml(lights, lights_file)

        # Now save entities
        for node in root_node.find_all_matches("**"):
            tags = node.get_python_tag_keys()
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                model_path = node.get_python_tag("model_path")
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()

                # Extract custom properties
                properties = {}
                for key in tags:
                    if key not in ("id", "pos", "hpr", "scale", "scripts"):
                        properties[key] = node.get_python_tag(key)

                entity_data = {
                    "name": node.get_name(),
                    "id": entity_id,
                    "entity_model": model_path,
                    "type": "script",
                    "transform": {
                        "position": {"x": position.x, "y": position.y, "z": position.z},
                        "rotation": {"h": rotation.x, "p": rotation.y, "r": rotation.z},
                        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    },
                    "properties": properties,
                }
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    toml.dump(entity_data, file)
                print(f"Saved {file_name} to {output_folder}")

    def zip_toml_files(self, source_dir, output_zip):
        """
        Zips all .toml files from the source directory (and its subdirectories) into a single ZIP file.
        """
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for foldername, subfolders, filenames in os.walk(source_dir):
                for filename in filenames:
                    if filename.endswith('.toml'):
                        filepath = os.path.join(foldername, filename)
                        # Get relative path for zip archive
                        arcname = os.path.relpath(filepath, source_dir)
                        zipf.write(filepath, arcname=arcname)
        print(f"Zipped TOML files into: {output_zip}")

    def save_scene_to_map(self, toml_folder: str, output_map: str):
        """
        Zips the TOML folder (containing scene and lights data) into a .map file.
        """
        if not os.path.exists(toml_folder):
            print(f"❌ The TOML folder {toml_folder} does not exist.")
            return
        self.zip_toml_files(toml_folder, output_map)
        print(f"Scene saved to map file: {output_map}")
        
    def save_scene_ui_to_toml(self, root_node: NodePath, output_folder: str, file_name: str):
        """
        Traverse the scene graph, extract entity data, and save each entity to a TOML file.

        Args:
            root_node (NodePath): The root of the scene graph to traverse.
            output_folder (str): Folder where TOML files will be saved.
        """
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for node in root_node.find_all_matches("**"):  # Traverse all nodes in the scene graph
            tags = node.get_python_tag_keys()
            print(node)

            # Check if the node has an 'id' tag
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                
                model_path = node.get_python_tag("model_path")
                widget_type = node.get_python_tag("widget_type")

                # Get transform properties
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()

                frame_color = node.get_python_tag("frameColor1")
                color = node.get_python_tag("text_fg1")

                action = node.get_python_tag("action")
                text = node.get_python_tag("text")
                image = node.get_python_tag("image")
                parent = node.get_python_tag("parent")
                isCanvas = node.get_python_tag("isCanvas")
                isLabel = node.get_python_tag("isLabel")
                isButton = node.get_python_tag("isButton")
                isImage = node.get_python_tag("isImage")
                
                # Get custom properties
                properties = {}
                for key in tags:
                    if key not in ("id",
                                   "pos",
                                   "hpr",
                                   "scale",
                                   "scripts",
                                   "text",
                                   "image",
                                   "parent",
                                   "action",
                                   "isCanvas",
                                   "isLabel",
                                   "isButton",
                                   "isImage",
                                   "frameColor1",
                                   "text_fg1",
                                   "frameColor",
                                   "text_fg",
                                   "ui_reference"):  # Exclude transform tags
                        properties[key] = node.get_python_tag(key)
                print(frame_color)
                # Create a dictionary to store entity data
                entity_data = {
                    "name": node.get_name(),
                    "id": entity_id,
                    "widget_type": widget_type,
                    "text1" : text,
                    "type": "script",
                    "action" : action,
                    "image" : image,
                    "parent" : parent,
                    "transform": {
                        "position": {"x": position.x, "y": position.y, "z": position.z},
                        "rotation": {"h": rotation.x, "p": rotation.y, "r": rotation.z},
                        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    },
                    "properties": properties,
                    "isCanvas": isCanvas,
                    "isLabel": isLabel,
                    "isButton": isButton,
                    "isImage": isImage,
                }
                # Conditionally add 'coloring' if widget_type == "l"
                if widget_type == "l":
                    entity_data["coloring"] = {
                        "frameColor1": {"r": frame_color["r"], "g": frame_color["g"], "b": frame_color["b"]},
                        "text_fg1": {"r": color["r"], "g": color["g"], "b": color["b"]},
                    }
                if widget_type == "b":
                    entity_data["coloring"] = {
                        "frameColor1": {"r": frame_color["r"], "g": frame_color["g"], "b": frame_color["b"]},
                        "text_fg1": {"r": color["r"], "g": color["g"], "b": color["b"]},
                    }

                # Convert dictionary to TOML string
                toml_string = toml.dumps(entity_data)
                # Save to a file with the node's name and ID
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    file.write(toml_string)
        def zip_toml_files(source_dir, output_file):
            # Create a .zip file with the .ui extension
            with zipfile.ZipFile(output_file, 'w') as zipf:
                # Iterate through all files in the source directory
                for foldername, subfolders, filenames in os.walk(source_dir):
                    for filename in filenames:
                        # Check if the file has a .toml extension
                        if filename.endswith('.toml'):
                            filepath = os.path.join(foldername, filename)
                            # Write the .toml file to the .zip file
                            zipf.write(filepath, os.path.relpath(filepath, source_dir))
            print(f"Zipped all .toml files into: {output_file}")
        zip_toml_files("./saves/ui", file_name + ".ui")