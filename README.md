# Panda3D Editor Documentation

## Warning:
this project is mostly tested on python 3.9 

## Overview
The Panda3D Editor is a scene editor designed to facilitate the creation, visualization, and management of 3D environments for Panda3D-based applications. It provides an intuitive interface for editing scene objects, adjusting properties, and managing assets.
[create_project](https://github.com/user-attachments/assets/506df29a-cb40-4d0f-86f4-4b12e1eeb659)

## Features!

- **Scene Hierarchy Management**: Organize objects within a tree view.
- ![editor_viewport](https://github.com/user-attachments/assets/8007e677-0d7f-4650-bff4-62f37a01e8cf)

- **Transform Gizmos**: Move, rotate, and scale objects interactively.
- **Property Inspector**: Modify object attributes in real-time.
- **Undo/Redo System**: Keep track of changes and revert if needed.
- **Integrated Python Console**: Execute scripts within the editor.
- **Visual Debugging Tools**: Display collision bounds, lights, and physics objects.
- **Networking Tools**: For creating games that will be multiplayer.
- **Animation Tab**: Create animations inside the editor(in future updates it will also load from 3rd party).
- ![animator](https://github.com/user-attachments/assets/21096391-ee7d-4951-9402-171c07f80a2a)

- **Terrain paintning/sclupting**: Create/Paint/Sclupt a terrain mesh. 
- **global registry & monobehavior system**: just like unity we have a mono behavior system!
- **UI Editor**: Create & Edit UI's for your game.
- **Save load system**: of course save your project in .toml for each entity and then it zips all entity tomls to .map, that way you can either share the .map to others or individual entities!
- **Shader Editor**: create shaders live inside the editor and save them to individual files(shader node editor comming soon).
- ![shader_editor](https://github.com/user-attachments/assets/136b4f32-6840-405f-9a69-c77c79304838)

- **Node Editor**: If you are tired of typing you can use the node editor!

## Getting Started
### Installation
Ensure you have Panda3D installed. Then, clone the repository and install dependencies:
```sh
pip install -r requirements.txt
```

### Running the Editor
Run the editor using:
```sh
python main.py
```

## User Interface
### 1. Scene Hierarchy
Displays all objects in the scene. Right-click to add or remove objects.

### 2. Viewport
A 3D view of the scene where users can interact with objects.

### 3. Properties Panel
Modify selected object properties such as position, rotation, and material settings.

### 4. Toolbar
Provides quick access to commonly used tools like translation, rotation, scaling, and snapping.

## Shortcuts
| Shortcut | Action |
|----------|--------|
| W | forward |
| A | left |
| S | backwards |
| D | right |
| e | up |
| q | down |

## Extending the Editor
### Adding Custom Components
Users can extend the editor by adding custom components. Example:
```python
class CustomComponent:
    def __init__(self, node):
        self.node = node
        print("Custom component added to", node)
```

## Roadmap
- Implement a material editor
- Fix terrain editor responsiveness issues
- Improve UI responsiveness and usability
- Organizing the project
- Undo & Redo is comming soon
- Introducing physics and physics debugging

## Contributing
We welcome contributions! Submit issues and pull requests via GitHub.

## License
MIT License. Free to use and modify.

