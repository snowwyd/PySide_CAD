from PySide6.QtWidgets import (QInputDialog, QMessageBox, QFileDialog)
from app.utils.handle_dxf import save_to_dxf_advanced, read_from_dxf
from app.config.config import *


class ActionManager():
    
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
            options=options
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
                    self.fileNameLabel.setText(f"Файл: {self.getFileNameFromPath(filename)}")
                    self.statusBar.showMessage(f"Загружен файл: {filename}")
                else:
                    QMessageBox.warning(self, "Ошибка загрузки", "Не удалось загрузить фигуры из файла.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка загрузки", f"Произошла ошибка при загрузке файла:\n{str(e)}")
    
    def saveFile(self):
        if not self.current_file:
            return self.saveFileAs()
        
        try:
            success = save_to_dxf_advanced(self.canvas.shapes, self.current_file)  # Используем advanced версию
            if success:
                self.statusBar.showMessage(f"Файл сохранен: {self.current_file}")
                return True
            else:
                QMessageBox.warning(self, "Ошибка сохранения", "Не удалось сохранить файл.")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении файла:\n{str(e)}")
            return False
    
    def saveFileAs(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить как DXF файл", 
            "", 
            "DXF Files (*.dxf)", 
            options=options
        )
        
        if filename:
            if not filename.lower().endswith('.dxf'):
                filename += '.dxf'
                
            try:
                success = save_to_dxf_advanced(self.canvas.shapes, filename)
                if success:
                    self.current_file = filename
                    self.fileNameLabel.setText(f"Файл: {self.getFileNameFromPath(filename)}")
                    self.statusBar.showMessage(f"Файл сохранен: {filename}")
                    return True
                else:
                    QMessageBox.warning(self, "Ошибка сохранения", "Не удалось сохранить файл.")
                    return False
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении файла:\n{str(e)}")
                return False
        
        return False

    def toggleGrid(self):
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.update()
        grid_state = "включена" if self.canvas.show_grid else "выключена"
        self.statusBar.showMessage(f"Сетка {grid_state}")

    def setGridSize(self):
        size, ok = QInputDialog.getInt(
            self, 
            "Размер сетки",
            "Введите размер ячейки сетки:",
            value=self.canvas.grid_size,
            minValue=10,
            maxValue=200
        )
        if ok:
            self.canvas.grid_size = size
            self.canvas.update()
            self.statusBar.showMessage(f"Размер сетки установлен: {size}")

    def chooseColor(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QGridLayout
        from PySide6.QtGui import QColor, QIcon, QPixmap
        from PySide6.QtCore import Qt, QSize
        
        standard_colors = {
            "Черный": (0, 0, 0),
            "Красный": (255, 0, 0),
            "Желтый": (255, 255, 0),
            "Зеленый": (0, 255, 0),
            "Голубой": (0, 255, 255),
            "Синий": (0, 0, 255),
            "Фиолетовый": (255, 0, 255),
            "Белый": (255, 255, 255),
            "Серый": (128, 128, 128),
            "Светло-серый": (192, 192, 192)
        }
        
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
            button.clicked.connect(lambda checked, c=color: self.setSelectedColor(c, dialog))
            
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

    def handleManualInput(self):
        self.canvas.handle_manual_input()

    def setCoordinateSystem(self, mode):
        self.canvas.inputCoordinateSystem = mode
        self.statusBar.showMessage(f"Система координат переключена на {COORD_SYSTEMS[mode].lower()}")

        if mode == 'cartesian':
            QMessageBox.information(self, "Система координат ввода", "Ввод координат будет производиться в Декартовой системе.")
        else:
            QMessageBox.information(self, "Система координат ввода", "Ввод координат будет производиться в Полярной системе.")

    def setDrawingMode(self, mode):
        self.canvas.setDrawingMode(mode)
        self.statusBar.showMessage(f"Режим рисования: {DRAWING_MODES[mode]}")

    def setLineType(self, line_type):
        self.canvas.lineType = line_type
        self.statusBar.showMessage(f"Установлен тип линии: {LINE_TYPES[line_type]}")

    def setLineThickness(self):
        """
        Показывает диалог выбора стандартной толщины линии согласно ISO
        """
        standard_thicknesses = [
            0.00, 0.05, 0.09,
            0.13, 0.15, 0.18, 0.20, 0.25,
            0.30, 0.35, 0.40, 0.50,
            0.70,
            1.00
        ]
        
        current_thickness = self.canvas.lineThickness
        closest_thickness = min(standard_thicknesses, key=lambda x: abs(x - current_thickness))
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
            False
        )
        
        if ok:
            selected_thickness = float(thickness.split()[0])
            self.canvas.lineThickness = selected_thickness
            self.statusBar.showMessage(f"Толщина линии установлена: {selected_thickness} мм")

    def confirmSaveChanges(self):
        """Ask the user whether to save changes to the current file"""
        reply = QMessageBox.question(
            self, 
            "Несохраненные изменения", 
            "Сохранить изменения в текущем файле?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            return True
        elif reply == QMessageBox.Discard:
            return False
        else:
            return None
    