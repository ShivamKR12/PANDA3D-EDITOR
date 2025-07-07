from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal

class PropertyGrid(QWidget):
    propertyChanged = pyqtSignal(str, object)  # property name, new value

    def __init__(self, property_descriptors, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.inputs = {}
        self.property_descriptors = property_descriptors
        self._build_grid()

    def _build_grid(self):
        for idx, prop in enumerate(self.property_descriptors):
            label = QLabel(prop['label'])
            box = QLineEdit()
            box.setText(str(prop.get('value', '')))
            box.editingFinished.connect(lambda prop=prop, box=box: self._on_property_changed(prop, box))
            self.inputs[prop['name']] = box
            self.layout.addWidget(label, idx, 0)
            self.layout.addWidget(box, idx, 1)

    def _on_property_changed(self, prop, box):
        text = box.text()
        try:
            value = prop['type'](text)
            box.setStyleSheet("")  # clear error
            self.propertyChanged.emit(prop['name'], value)
        except Exception:
            box.setStyleSheet("border: 1px solid red;")

    def set_values(self, values):
        for name, value in values.items():
            if name in self.inputs:
                self.inputs[name].setText(str(value))

    def get_values(self):
        result = {}
        for prop in self.property_descriptors:
            name = prop['name']
            text = self.inputs[name].text()
            try:
                result[name] = prop['type'](text)
            except Exception:
                result[name] = None
        return result
