import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QInputDialog,
    QStatusBar,
    QDockWidget,
    QMessageBox,
    QFileDialog,
    QLabel,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from app.ui.canvas import Canvas
from app.ui.object_tree import ConstructionTree
from PySide6.QtGui import QColor
from app.utils.handle_dxf import save_to_dxf_advanced, read_from_dxf
from app.config.config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D-FLEX 2025")
        self.setGeometry(100, 100, 1600, 1000)
        self.is_dark_theme = False
        self.current_file = None
        self.initUI()

    def initUI(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        self.createMenus()
        self.createStatusBar()
        self.createConstructionTree()

    def setGridSize(self):
        size, ok = QInputDialog.getInt(
            self,
            "Размер сетки",
            "Введите размер ячейки сетки:",
            value=self.canvas.grid_size,
            minValue=10,
            maxValue=200,
        )
        if ok:
            self.canvas.grid_size = size
            self.canvas.update()
            self.statusBar.showMessage(f"Размер сетки установлен: {size}")

    def createMenus(self):
        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu("Файл")

        newAction = QAction("Новый", self)
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("Создать новый файл")
        newAction.triggered.connect(self.newFile)
        fileMenu.addAction(newAction)

        openDxfAction = QAction("Открыть DXF...", self)
        openDxfAction.setShortcut("Ctrl+O")
        openDxfAction.setStatusTip("Открыть файл DXF")
        openDxfAction.triggered.connect(self.openDxfFile)
        fileMenu.addAction(openDxfAction)

        saveAction = QAction("Сохранить", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Сохранить файл")
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)

        saveAsAction = QAction("Сохранить как...", self)
        saveAsAction.setShortcut("Ctrl+Shift+S")
        saveAsAction.setStatusTip("Сохранить файл как...")
        saveAsAction.triggered.connect(self.saveFileAs)
        fileMenu.addAction(saveAsAction)

        fileMenu.addSeparator()

        exitAction = QAction("Выход", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Выйти из программы")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        gridMenu = mainMenu.addMenu("Сетка")

        gridAction = QAction("Показать/скрыть сетку", self)
        gridAction.setStatusTip("Переключить отображение сетки")
        gridAction.triggered.connect(self.toggleGrid)
        gridMenu.addAction(gridAction)

        gridSizeAction = QAction("Размер сетки", self)
        gridSizeAction.setStatusTip("Изменить размер ячейки сетки")
        gridSizeAction.triggered.connect(self.setGridSize)
        gridMenu.addAction(gridSizeAction)

        self.createDrawingObjectsMenu(mainMenu)
        self.createLineSettingsMenu(mainMenu)
        self.createShapeSettingsMenu(mainMenu)
        self.createCoordinateSystemMenu(mainMenu)

    def toggleGrid(self):
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.update()
        grid_state = "включена" if self.canvas.show_grid else "выключена"
        self.statusBar.showMessage(f"Сетка {grid_state}")

    def createDrawingObjectsMenu(self, menu):
        drawingObjectsMenu = menu.addMenu("Объекты")

        for mode, label in DRAWING_MODES.items():
            if not any(mode in group for group in GROUPED_DRAWING_MODES.values()):
                action = QAction(label, self)
                action.setStatusTip(f"Режим рисования: {label}")
                action.triggered.connect(lambda checked, m=mode: self.setDrawingMode(m))
                drawingObjectsMenu.addAction(action)

        group_order = GROUP_ORDER

        for group_name in group_order:
            if group_name in GROUPED_DRAWING_MODES:
                modes = GROUPED_DRAWING_MODES[group_name]
                groupMenu = drawingObjectsMenu.addMenu(group_name)
                for mode in modes:
                    action = QAction(DRAWING_MODES[mode], self)
                    action.setStatusTip(f"Режим рисования: {DRAWING_MODES[mode]}")
                    action.triggered.connect(
                        lambda checked, m=mode: self.setDrawingMode(m)
                    )
                    groupMenu.addAction(action)

    def createLineSettingsMenu(self, menu):
        lineSettingsMenu = menu.addMenu("Тип линии")
        for line_type, label in LINE_TYPES.items():
            action = QAction(label, self)
            action.setStatusTip(f"Установить {label.lower()}")
            action.triggered.connect(lambda checked, lt=line_type: self.setLineType(lt))
            lineSettingsMenu.addAction(action)

    def createShapeSettingsMenu(self, menu):
        shapeSettingsMenu = menu.addMenu("Настройки объектов")

        colorAction = QAction("Выбрать цвет", self)
        colorAction.setStatusTip("Выбрать цвет для новых построений")
        colorAction.triggered.connect(self.chooseColor)
        shapeSettingsMenu.addAction(colorAction)

        lineThicknessAction = QAction("Толщина линии", self)
        lineThicknessAction.setStatusTip("Изменить толщину линии")
        lineThicknessAction.triggered.connect(self.setLineThickness)
        shapeSettingsMenu.addAction(lineThicknessAction)

    def chooseColor(self):
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QPushButton,
            QHBoxLayout,
            QLabel,
            QGridLayout,
        )
        from PySide6.QtGui import QColor, QIcon, QPixmap
        from PySide6.QtCore import Qt, QSize

        standard_colors = STANDART_COLORS

        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите CAD-совместимый цвет")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        info_label = QLabel("Выберите один из стандартных CAD-совместимых цветов:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        grid = QGridLayout()
        grid.setSpacing(10)

        def create_color_square(color):
            pixmap = QPixmap(32, 32)
            pixmap.fill(color)
            return QIcon(pixmap)

        row, col = 0, 0
        for color_name, rgb in standard_colors.items():
            color = QColor(*rgb)
            button = QPushButton()
            button.setToolTip(color_name)
            button.setIcon(create_color_square(color))
            button.setIconSize(QSize(32, 32))
            button.setMinimumHeight(50)
            button.clicked.connect(
                lambda checked, c=color: self.setSelectedColor(c, dialog)
            )

            color_layout = QVBoxLayout()
            color_layout.addWidget(button)
            color_layout.addWidget(QLabel(color_name, alignment=Qt.AlignCenter))

            grid.addLayout(color_layout, row, col)

            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(grid)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def setSelectedColor(self, color, dialog):
        if color.isValid():
            self.canvas.currentColor = color
            self.statusBar.showMessage(f"Цвет линии изменен на {color.name()}")
            dialog.accept()

    def createCoordinateSystemMenu(self, menu):
        coordinateSystemMenu = menu.addMenu("Система координат")

        polarAction = QAction("Полярная", self)
        polarAction.setStatusTip("Переключиться на Полярную систему координат")
        polarAction.triggered.connect(lambda: self.setCoordinateSystem("polar"))
        coordinateSystemMenu.addAction(polarAction)

        cartesianAction = QAction("Декартова", self)
        cartesianAction.setStatusTip("Переключиться на Декартову систему координат")
        cartesianAction.triggered.connect(lambda: self.setCoordinateSystem("cartesian"))
        coordinateSystemMenu.addAction(cartesianAction)

    def createConstructionTree(self):
        if not self.findChild(QDockWidget, "Дерево построений"):
            self.constructionTree = ConstructionTree(self, self.canvas)
            self.addDockWidget(Qt.RightDockWidgetArea, self.constructionTree)

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

    def setLineThickness(self):
        standard_thicknesses = STANDART_THICKNESSES

        current_thickness = self.canvas.lineThickness
        closest_thickness = min(
            standard_thicknesses, key=lambda x: abs(x - current_thickness)
        )
        current_index = standard_thicknesses.index(closest_thickness)

        thickness_labels = []
        for t in standard_thicknesses:
            if t <= 0.09:
                category = "Очень тонкая"
            elif t <= 0.25:
                category = "Тонкая"
            elif t <= 0.50:
                category = "Средняя"
            elif t <= 0.70:
                category = "Толстая"
            else:
                category = "Очень толстая"
            thickness_labels.append(f"{t:.2f} мм ({category})")

        thickness, ok = QInputDialog.getItem(
            self,
            "Толщина линии",
            "Выберите стандартную толщину линии по ISO:",
            thickness_labels,
            current_index,
            False,
        )

        if ok:
            selected_thickness = float(thickness.split()[0])
            self.canvas.lineThickness = selected_thickness
            self.statusBar.showMessage(
                f"Толщина линии установлена: {selected_thickness} мм"
            )

    def rotateLeft(self):
        self.canvas.rotate(10)
        self.statusBar.showMessage("Поворот против часовой стрелки")

    def rotateRight(self):
        self.canvas.rotate(-10)
        self.statusBar.showMessage("Поворот по часовой стрелке")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
