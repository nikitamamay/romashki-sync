from PyQt5 import QtWidgets


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, widget: QtWidgets.QWidget = None, parent=None) -> None:
        super().__init__(parent=parent)
        self.setSizeAdjustPolicy(QtWidgets.QScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setWidgetResizable(True)
        if widget:
            self.setWidget(widget)
