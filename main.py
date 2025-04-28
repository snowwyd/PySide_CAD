import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QInputDialog,
    QStatusBar,
    QDockWidget,
    QMessageBox,
    QFileDialog,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QToolBar,
    QTabWidget,
    QToolButton,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QSpinBox,
    QMenu,
    QStyleFactory,
)
from PySide6.QtGui import QAction, QIcon, QPalette, QFont
from PySide6.QtCore import Qt, QSize
from app.ui.canvas import Canvas
from app.ui.object_tree import ConstructionTree
from PySide6.QtGui import QColor
from app.utils.handle_dxf import *
from app.config.config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D-FLEX 2025")
        self.setGeometry(100, 100, 1600, 1000)
        self.showMaximized()
        self.current_file = None
        self.initUI()

    def initUI(self):
        self.canvas = Canvas(self)
        self.toolTabs = self.createToolTabs()
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolTabs)
        layout.addWidget(self.canvas, 1)
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.menuBar().setVisible(False)
        self.createStatusBar()
        self.createConstructionTree()

    def createToolTabs(self):
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)
        tabs.setFixedHeight(TOOLBAR_HEIGHT)

        tabs.addTab(self._createFileTab(), "Файл")
        tabs.addTab(self._createWorkspaceTab(), "Рабочее пространство")
        tabs.addTab(self._createObjectsTab(), "Объекты")
        tabs.addTab(self._createStyleTab(), "Стиль")

        return tabs

    def _createGroup(self, title, widget):
        group = QWidget()
        vlay = QVBoxLayout(group)
        vlay.setSpacing(5)
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        vlay.addWidget(label)
        vlay.addWidget(widget)
        return group

    def _separator(self):
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.NoFrame)
        sep.setFixedWidth(2)
        sep.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        return sep

    def _createFileTab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        create_widget = self._makeButtonGrid(
            [
                ("Новый", self.newFile),
                ("Открыть DXF", self.openDxfFile),
            ]
        )
        save_widget = self._makeButtonGrid(
            [
                ("Сохранить", self.saveFile),
                ("Сохранить как", self.saveFileAs),
            ]
        )
        exit_widget = self._makeButtonGrid(
            [
                ("Выход", self.close),
            ]
        )
        layout.addWidget(self._createGroup("Создание", create_widget))
        layout.addWidget(self._separator())
        layout.addWidget(self._createGroup("Сохранение", save_widget))
        layout.addWidget(self._separator())
        layout.addWidget(self._createGroup("Выход", exit_widget))
        layout.addStretch()
        return widget

    def _createWorkspaceTab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Coordinate system group
        coord_widget = self._makeButtonGrid(
            [
                ("Полярная", lambda: self.setCoordinateSystem("polar")),
                ("Декартова", lambda: self.setCoordinateSystem("cartesian")),
            ]
        )
        layout.addWidget(self._createGroup("Система координат", coord_widget))
        layout.addWidget(self._separator())

        # Grid group with toggle, snap and spinbox for size
        grid_widget = QWidget()
        g_layout = QGridLayout(grid_widget)
        g_layout.setSpacing(5)

        # Toggle grid display
        toggle_btn = QToolButton()
        toggle_btn.setIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "resources",
                    "icons",
                    "показ_сетки.png",
                )
            )
        )
        toggle_btn.setIconSize(QSize(32, 32))
        toggle_btn.setToolTip("Показать/скрыть сетку")
        toggle_btn.clicked.connect(self.toggleGrid)
        g_layout.addWidget(toggle_btn, 0, 0)

        # Snap to grid
        snap_btn = QToolButton()
        snap_btn.setIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "resources",
                    "icons",
                    "привязка_к_сетке.png",
                )
            )
        )
        snap_btn.setIconSize(QSize(32, 32))
        snap_btn.setToolTip("Привязка к сетке")
        snap_btn.setCheckable(True)
        snap_btn.clicked.connect(self.toggleSnapGrid)
        g_layout.addWidget(snap_btn, 0, 1)

        # Grid size input
        spin = QSpinBox()
        spin.setRange(GRID_RANGE[0], GRID_RANGE[1])
        spin.setValue(self.canvas.grid_size)
        spin.setPrefix("Размер сетки: ")
        spin.setSuffix(" mm")
        spin.valueChanged.connect(self._setGridSize)
        g_layout.addWidget(spin, 0, 2)

        layout.addWidget(self._createGroup("Сетка", grid_widget))
        layout.addStretch()
        return widget

    def _createObjectsTab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        base_modes = [
            (label, lambda checked, m=mode: self.setDrawingMode(m))
            for mode, label in DRAWING_MODES.items()
            if not any(mode in grp for grp in GROUPED_DRAWING_MODES.values())
        ]
        layout.addWidget(
            self._createGroup("Основные", self._makeButtonGrid(base_modes))
        )
        layout.addWidget(self._separator())
        for group_name, modes in GROUPED_DRAWING_MODES.items():
            actions = [
                (DRAWING_MODES[m], lambda checked, m=m: self.setDrawingMode(m))
                for m in modes
            ]
            layout.addWidget(
                self._createGroup(group_name, self._makeButtonGrid(actions))
            )
            layout.addWidget(self._separator())
        layout.addStretch()
        return widget

    def _createStyleTab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        # Color selection button with menu
        color_btn = QToolButton()
        color_btn.setIconSize(QSize(32, 32))

        color_btn.setIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "resources",
                    "icons",
                    "выбор_цвета.png",
                )
            )
        )
        color_btn.setToolTip("Выбрать цвет")
        color_menu = QMenu(color_btn)
        for name, rgb in STANDART_COLORS.items():
            icon = QAction(
                QIcon(
                    os.path.join(
                        os.path.dirname(__file__),
                        "resources",
                        "icons",
                        name.lower() + ".png",
                    )
                ),
                name,
                self,
            )
            icon.triggered.connect(lambda checked, n=name: self._setColor(n))
            color_menu.addAction(icon)
        color_btn.setMenu(color_menu)
        color_btn.setPopupMode(QToolButton.InstantPopup)
        # Thickness selection
        thick_btn = QToolButton()
        thick_btn.setIconSize(QSize(32, 32))

        thick_btn.setIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "resources",
                    "icons",
                    "толщина_линии.png",
                )
            )
        )
        thick_btn.setToolTip("Толщина линии")
        thick_menu = QMenu(thick_btn)
        for t in STANDART_THICKNESSES:
            act = QAction(f"{t:.2f} мм", self)
            act.triggered.connect(lambda checked, v=t: self._setThickness(v))
            thick_menu.addAction(act)
        thick_btn.setMenu(thick_menu)
        thick_btn.setPopupMode(QToolButton.InstantPopup)
        # Add to group
        style_widget = QWidget()
        s_layout = QHBoxLayout(style_widget)
        s_layout.setSpacing(5)
        s_layout.addWidget(color_btn)
        s_layout.addWidget(thick_btn)
        layout.addWidget(self._createGroup("Параметры", style_widget))
        layout.addWidget(self._separator())
        type_widget = self._makeButtonGrid(
            [
                (label, lambda checked, lt=lt: self.setLineType(lt))
                for lt, label in LINE_TYPES.items()
            ]
        )
        layout.addWidget(self._createGroup("Тип", type_widget))
        layout.addStretch()
        return widget

    def toggleGrid(self):
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.update()
        grid_state = "включена" if self.canvas.show_grid else "выключена"
        self.statusBar.showMessage(f"Сетка {grid_state}")

    def _makeButtonGrid(self, actions):
        widget = QWidget()
        grid = QGridLayout(widget)
        grid.setSpacing(5)
        for idx, (text, slot) in enumerate(actions):
            btn = QToolButton()
            btn.setIconSize(QSize(32, 32))
            btn.setText("")
            btn.setIcon(
                QIcon(
                    os.path.join(
                        os.path.dirname(__file__),
                        "resources",
                        "icons",
                        text.lower().replace(" ", "_") + ".png",
                    )
                )
            )
            btn.setToolTip(text)
            btn.clicked.connect(slot)
            col = idx
            grid.addWidget(btn, 1, col)
        return widget

    def _setGridSize(self, val):
        self.canvas.grid_size = val
        self.canvas.update()
        self.statusBar.showMessage(f"Размер сетки установлен: {val}")

    def _setColor(self, name):
        rgb = STANDART_COLORS[name]
        color = QColor(*rgb)
        self.canvas.currentColor = color
        self.statusBar.showMessage(f"Цвет: {name}")

    def _setThickness(self, val):
        self.canvas.lineThickness = val
        self.statusBar.showMessage(f"Толщина: {val:.2f} мм")

    def createConstructionTree(self):
        if not self.findChild(QDockWidget, "Дерево построений"):
            self.constructionTree = ConstructionTree(self, self.canvas)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.constructionTree)

    def createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.fileNameLabel = QLabel("Новый файл")
        self.statusBar.addPermanentWidget(self.fileNameLabel)

    def handleManualInput(self):
        self.canvas.handle_manual_input()

    def setCoordinateSystem(self, mode):
        self.canvas.inputCoordinateSystem = mode
        self.statusBar.showMessage(
            f"Система координат переключена на {COORD_SYSTEMS[mode].lower()}"
        )

        if mode == "cartesian":
            QMessageBox.information(
                self,
                "Система координат ввода",
                "Ввод координат будет производиться в Декартовой системе.",
            )
        else:
            QMessageBox.information(
                self,
                "Система координат ввода",
                "Ввод координат будет производиться в Полярной системе.",
            )

    def setDrawingMode(self, mode):
        self.canvas.setDrawingMode(mode)
        self.statusBar.showMessage(f"Режим рисования: {DRAWING_MODES[mode]}")

    def setLineType(self, line_type):
        self.canvas.lineType = line_type
        self.statusBar.showMessage(f"Установлен тип линии: {LINE_TYPES[line_type]}")

    def newFile(self):
        if self.canvas.shapes and self.confirmSaveChanges():
            self.saveFile()

        self.canvas.shapes.clear()
        self.canvas.update()
        self.constructionTree.updateConstructionTree()

        self.current_file = None
        self.fileNameLabel.setText("Новый файл")
        self.statusBar.showMessage("Создан новый файл")

    def openDxfFile(self):
        if self.canvas.shapes and self.confirmSaveChanges():
            self.saveFile()

        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть DXF файл",
            "",
            "DXF Files (*.dxf);;All Files (*)",
            options=options,
        )

        if filename:
            try:
                self.canvas.shapes.clear()

                loaded_shapes = read_from_dxf(filename, self.canvas)

                if loaded_shapes:
                    self.canvas.shapes.extend(loaded_shapes)
                    self.canvas.update()
                    self.constructionTree.updateConstructionTree()

                    self.current_file = filename
                    self.fileNameLabel.setText(
                        f"Файл: {self.getFileNameFromPath(filename)}"
                    )
                    self.statusBar.showMessage(f"Загружен файл: {filename}")
                else:
                    QMessageBox.warning(
                        self, "Ошибка загрузки", "Не удалось загрузить фигуры из файла."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка загрузки",
                    f"Произошла ошибка при загрузке файла:\n{str(e)}",
                )

    def saveFile(self):
        if not self.current_file:
            return self.saveFileAs()

        try:
            success = save_to_dxf_advanced(self.canvas.shapes, self.current_file)
            if success:
                self.statusBar.showMessage(f"Файл сохранен: {self.current_file}")
                return True
            else:
                QMessageBox.warning(
                    self, "Ошибка сохранения", "Не удалось сохранить файл."
                )
                return False
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Произошла ошибка при сохранении файла:\n{str(e)}",
            )
            return False

    def saveFileAs(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как DXF файл", "", "DXF Files (*.dxf)", options=options
        )

        if filename:
            if not filename.lower().endswith(".dxf"):
                filename += ".dxf"

            try:
                success = save_to_dxf_advanced(self.canvas.shapes, filename)
                if success:
                    self.current_file = filename
                    self.fileNameLabel.setText(
                        f"Файл: {self.getFileNameFromPath(filename)}"
                    )
                    self.statusBar.showMessage(f"Файл сохранен: {filename}")
                    return True
                else:
                    QMessageBox.warning(
                        self, "Ошибка сохранения", "Не удалось сохранить файл."
                    )
                    return False
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка сохранения",
                    f"Произошла ошибка при сохранении файла:\n{str(e)}",
                )
                return False

        return False

    def confirmSaveChanges(self):
        reply = QMessageBox.question(
            self,
            "Несохраненные изменения",
            "Сохранить изменения в текущем файле?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )

        if reply == QMessageBox.Save:
            return True
        elif reply == QMessageBox.Discard:
            return False
        else:
            return None

    def toggleSnapGrid(self, checked):
        self.canvas.snap_grid = checked

    def getFileNameFromPath(self, path):
        import os

        return os.path.basename(path)

    def closeEvent(self, event):
        if self.canvas.shapes and self.confirmSaveChanges():
            if self.saveFile():
                event.accept()
            else:
                reply = QMessageBox.question(
                    self,
                    "Ошибка сохранения",
                    "Не удалось сохранить файл. Выйти без сохранения?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
        else:
            event.accept()


def apply_material_theme(app, dark=False):
    # Set Fusion style as base
    app.setStyle(QStyleFactory.create("Fusion"))
    # Set global font

    palette = QPalette()
    primary = QColor(PRIMARY_COLOR)
    on_primary = QColor(ON_PRIMARY_COLOR)
    secondary = QColor("#03DAC6")
    surface = QColor("#FFFFFF")
    background = QColor("#FAFAFA")
    on_surface = QColor("#000000")

    # Assign palette roles
    palette.setColor(QPalette.Window, background)
    palette.setColor(QPalette.WindowText, on_surface)
    palette.setColor(QPalette.Base, surface)
    palette.setColor(QPalette.AlternateBase, background)
    palette.setColor(QPalette.ToolTipBase, on_surface)
    palette.setColor(QPalette.ToolTipText, on_surface)
    palette.setColor(QPalette.Text, on_surface)
    palette.setColor(QPalette.Button, surface)
    palette.setColor(QPalette.ButtonText, on_surface)
    palette.setColor(QPalette.Highlight, primary)
    palette.setColor(QPalette.HighlightedText, on_primary)
    palette.setColor(QPalette.Link, secondary)
    app.setPalette(palette)

    # QSS for additional styling
    app.setStyleSheet(
        f"""
        /* General font */
        * {{ font-family: Consolas; }}
        /* Tooltips */
        QToolTip {{ background-color: {surface.name()}; color: {on_surface.name()}; border: 1px solid {primary.name()}; }}
        /* Tool buttons */
        QToolButton {{ border: none; padding: 6px; border-radius: 4px; qproperty-toolButtonStyle: IconOnly; }}
        QToolButton:hover {{ background-color: {primary.lighter(150).name()}; }}
        QToolButton:pressed, QToolButton:checked {{ background-color: {primary.name()}; color: {on_primary.name()}; }}
        /* Tabs */
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ background: {surface.name()}; color: {on_surface.name()}; padding: 8px 16px; border-radius: 4px; margin: 2px; }}
        QTabBar::tab:selected {{ background: {primary.name()}; color: {on_primary.name()}; }}
        /* Spinboxes */
        QSpinBox {{ padding: 4px; border-radius: 4px; }}
        /* Separator lines */
        QFrame#separator {{ background-color: {surface.name()}; }}
    """
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_material_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
