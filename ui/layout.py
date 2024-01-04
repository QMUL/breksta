"""Contains helper functions to create layouts."""
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox


def create_group_box(widget, name: str) -> QGroupBox:
    """Adds a UI element to a Vertical box layout and encapsulates it into a Group Box with a given name.
    Args:
        widget: The UI element added to the layout and the Group Box.
        name (str): The name of the Group Box.
    """
    group_box = QGroupBox(name)
    group_layout = QVBoxLayout()
    group_layout.addWidget(widget)
    group_box.setLayout(group_layout)
    return group_box


def create_horizontal_box(widget, label) -> QHBoxLayout:
    """Adds a UI element to a Horizontal box layout.
    Args:
        widget: The UI element added to the box.
        label: The element's label.
    """
    box_layout = QHBoxLayout()
    box_layout.addWidget(label)
    box_layout.addWidget(widget)
    return box_layout
