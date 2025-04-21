import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QInputDialog, QStatusBar,QDockWidget, QMessageBox, QFileDialog, QLabel)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from app.ui.canvas import Canvas
from app.ui.object_tree import ConstructionTree
from app.utils.handle_dxf import save_to_dxf_advanced, read_from_dxf
from app.core.actions.action_manager import ActionManager

from app.config.config import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D-FLEX 2025")
        self.setGeometry(100, 100, 1600, 1000)
        self.current_file = None
        self.actionManager = ActionManager

        self.initUI()

    def initUI(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        self.createMenus()
        self.createStatusBar()
        self.createConstructionTree()

    def createMenus(self):
        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('Файл')
        
        newAction = QAction('Новый', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('Создать новый файл')
        newAction.triggered.connect(self.actionManager.newFile)
        fileMenu.addAction(newAction)
        
        openDxfAction = QAction('Открыть DXF...', self)
        openDxfAction.setShortcut('Ctrl+O')
        openDxfAction.setStatusTip('Открыть файл DXF')
        openDxfAction.triggered.connect(self.actionManager.openDxfFile)
        fileMenu.addAction(openDxfAction)
        
        saveAction = QAction('Сохранить', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Сохранить файл')
        saveAction.triggered.connect(self.actionManager.saveFile)
        fileMenu.addAction(saveAction)
        
        saveAsAction = QAction('Сохранить как...', self)
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.setStatusTip('Сохранить файл как...')
        saveAsAction.triggered.connect(self.actionManager.saveFileAs)
        fileMenu.addAction(saveAsAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из программы')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        gridMenu = mainMenu.addMenu('Сетка')

        gridAction = QAction('Показать/скрыть сетку', self)
        gridAction.setStatusTip("Переключить отображение сетки")
        gridAction.triggered.connect(self.actionManager.toggleGrid)
        gridMenu.addAction(gridAction)

        gridSizeAction = QAction('Размер сетки', self)
        gridSizeAction.setStatusTip("Изменить размер ячейки сетки")
        gridSizeAction.triggered.connect(self.actionManager.setGridSize)
        gridMenu.addAction(gridSizeAction)
        
        self.createDrawingObjectsMenu(mainMenu)
        self.createLineSettingsMenu(mainMenu)
        self.createShapeSettingsMenu(mainMenu)
        self.createCoordinateSystemMenu(mainMenu)
    
    def createDrawingObjectsMenu(self, menu):
        drawingObjectsMenu = menu.addMenu('Объекты')

        for mode, label in DRAWING_MODES.items():
            if not any(mode in group for group in GROUPED_DRAWING_MODES.values()):
                action = QAction(label, self)
                action.setStatusTip(f"Режим рисования: {label}")
                action.triggered.connect(lambda checked, m=mode: self.actionManager.setDrawingMode(m))
                drawingObjectsMenu.addAction(action)

        group_order = ['Линия', 'Сплайн', 'Прямоугольник', 'Многоугольник', 'Окружность', 'Дуга']
        
        for group_name in group_order:
            if group_name in GROUPED_DRAWING_MODES:
                modes = GROUPED_DRAWING_MODES[group_name]
                groupMenu = drawingObjectsMenu.addMenu(group_name)
                for mode in modes:
                    action = QAction(DRAWING_MODES[mode], self)
                    action.setStatusTip(f"Режим рисования: {DRAWING_MODES[mode]}")
                    action.triggered.connect(lambda checked, m=mode: self.actionManager.setDrawingMode(m))
                    groupMenu.addAction(action)

    def createLineSettingsMenu(self, menu):
        lineSettingsMenu = menu.addMenu('Тип линии')
        for line_type, label in LINE_TYPES.items():
            action = QAction(label, self)
            action.setStatusTip(f"Установить {label.lower()}")
            action.triggered.connect(lambda checked, lt=line_type: self.actionManager.setLineType(lt))
            lineSettingsMenu.addAction(action)

    def createShapeSettingsMenu(self, menu):
        shapeSettingsMenu = menu.addMenu('Настройки объектов')
        
        colorAction = QAction('Выбрать цвет', self)
        colorAction.setStatusTip("Выбрать цвет для новых построений")
        colorAction.triggered.connect(self.actionManager.chooseColor)
        shapeSettingsMenu.addAction(colorAction)
        
        lineThicknessAction = QAction('Толщина линии', self)
        lineThicknessAction.setStatusTip("Изменить толщину линии")
        lineThicknessAction.triggered.connect(self.actionManager.setLineThickness)
        shapeSettingsMenu.addAction(lineThicknessAction)
    
    def setSelectedColor(self, color, dialog):
        if color.isValid():
            self.canvas.currentColor = color
            self.statusBar.showMessage(f"Цвет линии изменен на {color.name()}")
            dialog.accept()

    def createCoordinateSystemMenu(self, menu):
        coordinateSystemMenu = menu.addMenu('Система координат')

        polarAction = QAction('Полярная', self)
        polarAction.setStatusTip("Переключиться на Полярную систему координат")
        polarAction.triggered.connect(lambda: self.actionManager.setCoordinateSystem('polar'))
        coordinateSystemMenu.addAction(polarAction)
        
        cartesianAction = QAction('Декартова', self)
        cartesianAction.setStatusTip("Переключиться на Декартову систему координат")
        cartesianAction.triggered.connect(lambda: self.actionManager.setCoordinateSystem('cartesian'))
        coordinateSystemMenu.addAction(cartesianAction)

    def createConstructionTree(self):
        if not self.findChild(QDockWidget, "Дерево построений"):
            self.constructionTree = ConstructionTree(self, self.canvas)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.constructionTree)

    def createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.fileNameLabel = QLabel("Новый файл")
        self.statusBar.addPermanentWidget(self.fileNameLabel)

    def rotateLeft(self):
        self.canvas.rotate(10)
        self.statusBar.showMessage("Поворот против часовой стрелки")

    def rotateRight(self):
        self.canvas.rotate(-10)
        self.statusBar.showMessage("Поворот по часовой стрелке")

    def getFileNameFromPath(self, path):
        """Extract just the file name from a path"""
        import os
        return os.path.basename(path)
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.canvas.shapes and self.actionManager.confirmSaveChanges(self):
            if self.actionManager.saveFile(self):
                event.accept()
            else:
                reply = QMessageBox.question(
                    self, 
                    "Ошибка сохранения", 
                    "Не удалось сохранить файл. Выйти без сохранения?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
