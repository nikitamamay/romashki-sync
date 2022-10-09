from PyQt5 import QtCore, QtGui, QtWidgets

from gui.misc import FONT_FAMILY_MONOSPACE, icon
from gui.scroll_area import ScrollArea
from file_watcher import File


class ChangeRepresentationWidget(QtWidgets.QCheckBox):
    def __init__(self, file_obj: File, parent = None) -> None:
        super().__init__(parent)

        self.file_obj = file_obj

        self.setFont(QtGui.QFont(FONT_FAMILY_MONOSPACE))
        self.setText(self.file_obj.basename())
        self.setToolTip(self.file_obj.relpath)

        self.menu = QtWidgets.QMenu(self.text())
        self.menu.addAction(icon.daisy(), self.text())
        # self.a_ignored = QtWidgets.QAction("Ignore")
        # self.a_ignored.setCheckable(True)
        # self.a_ignored.triggered.connect(self.toggleIgnored)
        # self.menu.addAction(self.a_ignored)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.menu.move(event.globalPos())
        self.menu.show()

    def setState(self, state: int):
        if state == 1:
            self.setStyleSheet("color: red")
        else:
            raise Exception(f'Unsupported state: {state}')


class ChangeRepresentationListWidget(QtWidgets.QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.reprs: list[ChangeRepresentationWidget] = []

        self.pixmap = None

        self.layout_reprs = QtWidgets.QVBoxLayout()
        self.layout_reprs.setSpacing(2)
        self.layout_reprs.setContentsMargins(2, 2, 2, 2)
        self.layout_reprs.setAlignment(QtCore.Qt.AlignTop)

        self.container_reprs = QtWidgets.QWidget()
        self.container_reprs.setLayout(self.layout_reprs)
        self.container_reprs.paintEvent = lambda event: self.container_paintEvent(self.container_reprs, event)

        self.scroll_area = ScrollArea(self.container_reprs)
        self.scroll_area.setMinimumHeight(40)

        self.checkbox_all = QtWidgets.QCheckBox("Select All")
        self.checkbox_all.setTristate(False)
        self.checkbox_all.clicked.connect(self.set_state_to_all)

        self.layout_ = QtWidgets.QGridLayout()
        self.layout_.setSpacing(2)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.checkbox_all, 1, 0, 1, 1)
        self.layout_.addWidget(self.scroll_area, 2, 0, 1, 1)
        self.setLayout(self.layout_)

    def container_paintEvent(self, container, a0: QtGui.QPaintEvent) -> None:
        if self.pixmap:
            painter = QtGui.QPainter()
            painter.begin(container)
            p_w_min = 32
            margin = min(20, (container.height() - p_w_min) / 2)
            p_w = max(min(128, container.width(), container.height()) - 2 * margin, p_w_min)
            painter.drawPixmap(container.width() - p_w - margin, margin, p_w, p_w, self.pixmap)
            painter.end()
        return super().paintEvent(a0)

    def init_representations(self, files: list[File]) -> None:
        self.clear_representations()
        for f in files:
            self.add_file_repr(f)
        self.check_tristate()

    def clear_representations(self) -> None:
        while len(self.reprs) > 0:
            self.layout_reprs.removeWidget(self.reprs.pop())

    def apply_intersections(self, l: list[File]) -> None:
        for f in l:
            for r in self.reprs:
                if r.file_obj.relpath == f.relpath:
                    r.setState(1)

    def add_file_repr(self, f: File) -> None:
        w = ChangeRepresentationWidget(f)
        self.layout_reprs.addWidget(w)
        self.reprs.append(w)
        w.toggled.connect(self.check_tristate)

    def set_state_to_all(self, state: bool) -> None:
        for r in self.reprs:
            r.setChecked(state)
        self.check_tristate()

    def get_checked_files(self) -> list[File]:
        l: list[File] = []
        for r in self.reprs:
            if r.isChecked():
                l.append(r.file_obj)
        return l

    def check_tristate(self) -> None:
        if len(self.reprs) > 0:
            state = self.reprs[0].isChecked()
            for i in range(1, len(self.reprs)):
                if self.reprs[i].isChecked() != state:
                    self.checkbox_all.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
                    return
            self.checkbox_all.setCheckState([
                QtCore.Qt.CheckState.Unchecked,
                QtCore.Qt.CheckState.Checked
            ][int(state)])
        else:
            self.checkbox_all.setCheckState(QtCore.Qt.CheckState.Unchecked)
