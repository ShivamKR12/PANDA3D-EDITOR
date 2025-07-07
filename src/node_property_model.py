from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel

class NodePropertyModel(QObject):
    property_changed = pyqtSignal(str, float)

    def __init__(self, node):
        super().__init__()
        self.node = node

    def set_property(self, prop_name, value):
        # Validate and set property
        if prop_name.startswith("position."):
            idx = "xyz".index(prop_name[-1])
            pos = list(self.node.getPos())
            pos[idx] = value
            self.node.setPos(*pos)
        elif prop_name.startswith("rotation."):
            idx = "xyz".index(prop_name[-1])
            hpr = list(self.node.getHpr())
            hpr[idx] = value
            self.node.setHpr(*hpr)
        elif prop_name.startswith("scale."):
            idx = "xyz".index(prop_name[-1])
            scale = list(self.node.getScale())
            scale[idx] = value
            self.node.setScale(*scale)
        self.property_changed.emit(prop_name, value)

    def get_property(self, prop_name):
        if prop_name.startswith("position."):
            idx = "xyz".index(prop_name[-1])
            return self.node.getPos()[idx]
        elif prop_name.startswith("rotation."):
            idx = "xyz".index(prop_name[-1])
            return self.node.getHpr()[idx]
        elif prop_name.startswith("scale."):
            idx = "xyz".index(prop_name[-1])
            return self.node.getScale()[idx]
        return None

class NodePropertyEditor(QWidget):
    def __init__(self, node_model):
        super().__init__()
        self.node_model = node_model
        self.input_boxes = {}
        layout = QGridLayout(self)
        props = [
            ("position", "Position"),
            ("rotation", "Rotation"),
            ("scale", "Scale")
        ]
        for i, (prefix, label) in enumerate(props):
            layout.addWidget(QLabel(label + " x y z:"), i*2, 0, 1, 3)
            for j, axis in enumerate("xyz"):
                prop_name = f"{prefix}.{axis}"
                box = QLineEdit(self)
                box.setText(str(self.node_model.get_property(prop_name)))
                box.editingFinished.connect(lambda pn=prop_name, b=box: self.on_input_changed(pn, b))
                self.input_boxes[prop_name] = box
                layout.addWidget(box, i*2+1, j)
        self.node_model.property_changed.connect(self.update_ui)

    def on_input_changed(self, prop_name, box):
        try:
            value = float(box.text())
            self.node_model.set_property(prop_name, value)
            box.setStyleSheet("")
        except ValueError:
            box.setStyleSheet("background: #ffcccc;")  # Red background for error

    def update_ui(self, prop_name, value):
        if prop_name in self.input_boxes:
            self.input_boxes[prop_name].setText(str(value))
