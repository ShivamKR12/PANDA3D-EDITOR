from PyQt5.QtWidgets import QWidget, QVBoxLayout
from property_grid import PropertyGrid

class PropertyGridDemo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        # Example property descriptors for a transform
        properties = [
            {'label': 'Position X', 'name': 'position.x', 'type': float, 'value': 0.0},
            {'label': 'Position Y', 'name': 'position.y', 'type': float, 'value': 0.0},
            {'label': 'Position Z', 'name': 'position.z', 'type': float, 'value': 0.0},
            {'label': 'Rotation X', 'name': 'rotation.x', 'type': float, 'value': 0.0},
            {'label': 'Rotation Y', 'name': 'rotation.y', 'type': float, 'value': 0.0},
            {'label': 'Rotation Z', 'name': 'rotation.z', 'type': float, 'value': 0.0},
            {'label': 'Scale X', 'name': 'scale.x', 'type': float, 'value': 1.0},
            {'label': 'Scale Y', 'name': 'scale.y', 'type': float, 'value': 1.0},
            {'label': 'Scale Z', 'name': 'scale.z', 'type': float, 'value': 1.0},
        ]
        self.grid = PropertyGrid(properties)
        layout.addWidget(self.grid)
        self.grid.propertyChanged.connect(self.on_property_changed)

    def on_property_changed(self, name, value):
        print(f"Property changed: {name} = {value}")
