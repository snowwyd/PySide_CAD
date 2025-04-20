from PySide6.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem, QMenu, 
                           QInputDialog, QMessageBox, QVBoxLayout, 
                           QWidget, QLabel, QPushButton, QHBoxLayout)
from PySide6.QtGui import QAction, QColor, QBrush
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from PySide6.QtGui import QFont  
from app.core.line import Line
from app.core.circle import Circle, CircleByThreePoints
from app.core.arc import ArcByThreePoints, ArcByRadiusChord
from app.core.polygon import Polygon
from app.core.rectangle import Rectangle
from app.core.spline import BezierSpline, SegmentSpline
from PySide6.QtWidgets import QTreeWidgetItemIterator

# TODO: имплементировать свою реализацию

class ConstructionTree(QDockWidget):
    def __init__(self, parent, canvas):
        super().__init__("Объекты построения", parent)
        self.parent = parent
        self.canvas = canvas
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        title_label = QLabel("Объекты построения")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        self.buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_widget)
        
        collapse_btn = QPushButton("Свернуть все")
        expand_btn = QPushButton("Развернуть все")
        collapse_btn.clicked.connect(lambda: self.treeWidget.collapseAll())
        expand_btn.clicked.connect(lambda: self.treeWidget.expandAll())
        
        buttons_layout.addWidget(expand_btn)
        buttons_layout.addWidget(collapse_btn)
        
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setFont(QFont("Arial", 10))
        
        self.main_layout.addWidget(header_widget)
        self.main_layout.addWidget(self.buttons_widget)
        self.main_layout.addWidget(self.treeWidget)
        
        self.setWidget(self.main_widget)
        
        self.canvas.shapeAdded.connect(self.updateConstructionTree)
        self.canvas.shapeRemoved.connect(self.updateConstructionTree)
        self.canvas.zPressed.connect(self.updateConstructionTree)
        self.treeWidget.itemClicked.connect(self.onTreeItemClicked)
        self.treeWidget.itemDoubleClicked.connect(self.onTreeItemDoubleClicked)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.onTreeContextMenu)
        
        is_dark_theme = parent.is_dark_theme if hasattr(parent, 'is_dark_theme') else False
        self.updateThemeStyles(is_dark_theme)
        
        self.updateConstructionTree()

    def updateThemeStyles(self, is_dark_theme):
        if is_dark_theme:
            self.setStyleSheet("""
                QTreeWidget {
                    background-color: #1e1e1e;
                    alternate-background-color: #252525;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                }
                QTreeWidget::item {
                    color: #ffffff;
                    padding: 4px;
                    border-bottom: 1px solid #3d3d3d;
                }
                QTreeWidget::item:selected {
                    background-color: #2979ff;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QTreeWidget {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    background-color: white;
                    alternate-background-color: #f8f8f8;
                }
                QTreeWidget::item {
                    padding: 4px;
                    border-bottom: 1px solid #eeeeee;
                }
                QTreeWidget::item:selected {
                    background: #e3f2fd;
                    color: #1976d2;
                }
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
            """)

    def saveExpandState(self):
        expanded_states = {}
        
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            expanded_states[item.text(0)] = item.isExpanded()
            iterator += 1
        return expanded_states

    def restoreExpandState(self, expanded_states):
        if not expanded_states:
            return
            
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item.text(0) in expanded_states:
                item.setExpanded(expanded_states[item.text(0)])
            else:
                item.setExpanded(False)
            iterator += 1

    def updateConstructionTree(self):
        expanded_states = self.saveExpandState()

        self.treeWidget.clear()
        
        shape_names = {
            'Line': 'Линия',
            'Circle': 'Окружность',
            'Rectangle': 'Прямоугольник',
            'Polygon': 'Многоугольник',
            'CircleByThreePoints': 'Окружность по трем точкам',
            'ArcByThreePoints': 'Дуга по трем точкам',
            'ArcByRadiusChord': 'Дуга по радиусу и хорде',
            'BezierSpline': 'Кривая Безье',
            'SegmentSpline': 'Сегментная кривая'
        }

        shape_colors = {
            'Line': '#2196F3',
            'Circle': '#4CAF50',
            'Rectangle': '#FFC107',
            'Polygon': '#9C27B0',
            'CircleByThreePoints': '#4CAF50',
            'ArcByThreePoints': '#FF5722',
            'ArcByRadiusChord': '#FF5722',
            'BezierSpline': '#E91E63',
            'SegmentSpline': '#E91E63'
        }
        
        line_type_names = {
            'solid': 'Сплошная',
            'dash': 'Штриховая',
            'dash_dot': 'Штрих-пунктирная',
            'dash_dot_dot': 'Штрих-пунктирная с двумя точками'
        }
        
        is_dark_theme = self.parent.is_dark_theme if hasattr(self.parent, 'is_dark_theme') else False
        
        for index, shape in enumerate(self.canvas.shapes):
            shape_type = type(shape).__name__
            shape_name = shape_names.get(shape_type, shape_type)
            item_text = f"{index + 1}: {shape_name}"
            
            tree_item = QTreeWidgetItem([item_text])
            tree_item.setData(0, Qt.UserRole, {'index': index})
            
            color = QColor(shape_colors.get(shape_type, '#757575'))
            
            if is_dark_theme:
                tree_item.setForeground(0, QColor('#ffffff'))
            else:
                tree_item.setForeground(0, color)
                
            font = QFont("Arial", 10, QFont.Bold)
            tree_item.setFont(0, font)
            
            if index == self.canvas.highlighted_shape_index:
                self.treeWidget.setCurrentItem(tree_item)
            
            self.treeWidget.addTopLevelItem(tree_item)

            def create_child_item(parent, text, index=None, property_name=None, is_editable=True):
                item = QTreeWidgetItem([text])
                if is_editable and index is not None:
                    item.setData(0, Qt.UserRole, {'index': index, 'property': property_name})
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                parent.addChild(item)
                item.setFont(0, QFont("Arial", 9))
                if is_dark_theme:
                    item.setForeground(0, QColor('#ffffff'))
                return item
            
            if hasattr(shape, 'line_type'):
                line_type_text = line_type_names.get(shape.line_type, shape.line_type)
                create_child_item(tree_item,
                    f"Тип линии: {line_type_text}",
                    index, 'line_type')
            
            if hasattr(shape, 'line_thickness'):
                create_child_item(tree_item,
                    f"Толщина линии: {shape.line_thickness:.2f}",
                    index, 'line_thickness')
            
            if hasattr(shape, 'color') and shape.color:
                color_item = create_child_item(tree_item,
                    f"Цвет: {shape.color.name()}",
                    index, 'color')
                
                color_brush = QBrush(shape.color)
                color_item.setBackground(0, color_brush)
                
                if shape.color.red() + shape.color.green() + shape.color.blue() < 380:
                    color_item.setForeground(0, QColor(255, 255, 255))

            if isinstance(shape, Line):
                create_child_item(tree_item, 
                    f"Начало: ({shape.start_point.x():.2f}, {shape.start_point.y():.2f})",
                    index, 'start_point')
                create_child_item(tree_item,
                    f"Конец: ({shape.end_point.x():.2f}, {shape.end_point.y():.2f})",
                    index, 'end_point')
                create_child_item(tree_item,
                    f"Длина: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, Circle):
                create_child_item(tree_item,
                    f"Центр: ({shape.center.x():.2f}, {shape.center.y():.2f})",
                    index, 'center')
                create_child_item(tree_item,
                    f"Радиус: {shape.radius:.2f}",
                    index, 'radius')
                create_child_item(tree_item,
                    f"Длина окружности: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, Rectangle):
                rect = shape.rect
                topLeft = rect.topLeft()
                create_child_item(tree_item,
                    f"Верхний левый угол: ({topLeft.x():.2f}, {topLeft.y():.2f})",
                    index, 'top_left')
                create_child_item(tree_item,
                    f"Ширина: {rect.width():.2f}",
                    index, 'width')
                create_child_item(tree_item,
                    f"Высота: {rect.height():.2f}",
                    index, 'height')
                create_child_item(tree_item,
                    f"Периметр: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, Polygon):
                for i, p in enumerate(shape.points):
                    create_child_item(tree_item,
                        f"Вершина {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                        index, f'point_{i}')
                create_child_item(tree_item,
                    f"Периметр: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, CircleByThreePoints):
                for i, p in enumerate(shape.points):
                    create_child_item(tree_item,
                        f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                        index, f'point_{i}')
                create_child_item(tree_item,
                    f"Длина окружности: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, ArcByThreePoints):
                for i, p in enumerate(shape.points):
                    create_child_item(tree_item,
                        f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                        index, f'point_{i}')
                create_child_item(tree_item,
                    f"Длина дуги: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, ArcByRadiusChord):
                create_child_item(tree_item,
                    f"Центр: ({shape.center.x():.2f}, {shape.center.y():.2f})",
                    index, 'center')
                create_child_item(tree_item,
                    f"Точка радиуса: ({shape.radius_point.x():.2f}, {shape.radius_point.y():.2f})",
                    index, 'radius_point')
                create_child_item(tree_item,
                    f"Точка хорды: ({shape.chord_point.x():.2f}, {shape.chord_point.y():.2f})",
                    index, 'chord_point')
                create_child_item(tree_item,
                    f"Длина дуги: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, BezierSpline):
                for i, p in enumerate(shape.points):
                    create_child_item(tree_item,
                        f"Контрольная точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                        index, f'control_point_{i}')
                create_child_item(tree_item,
                    f"Длина сплайна: {shape.get_total_length():.2f}",
                    is_editable=False)

            elif isinstance(shape, SegmentSpline):
                for i, p in enumerate(shape.points):
                    create_child_item(tree_item,
                        f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                        index, f'point_{i}')
                create_child_item(tree_item,
                    f"Длина сплайна: {shape.get_total_length():.2f}",
                    is_editable=False)

            else:
                create_child_item(tree_item, "Нет дополнительной информации", is_editable=False)

        if len(self.canvas.shapes) == 1 and not expanded_states:
            self.treeWidget.expandAll()
        else:
            self.restoreExpandState(expanded_states)

    def onTreeItemClicked(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                self.canvas.highlighted_shape_index = index
                self.canvas.repaint()
                
                shape = self.canvas.shapes[index]
                shape_type = type(shape).__name__
                shape_names = {
                    'Line': 'Линия',
                    'Circle': 'Окружность',
                    'Rectangle': 'Прямоугольник',
                    'Polygon': 'Многоугольник',
                    'CircleByThreePoints': 'Окружность по трем точкам',
                    'ArcByThreePoints': 'Дуга по трем точкам',
                    'ArcByRadiusChord': 'Дуга по радиусу и хорде',
                    'BezierSpline': 'Кривая Безье',
                    'SegmentSpline': 'Сегментная кривая'
                }
                shape_name = shape_names.get(shape_type, shape_type)
                message = f"Выбран объект: {index + 1}: {shape_name}"
                if hasattr(self.parent, 'statusBar'):
                    self.parent.statusBar.showMessage(message)

    def onTreeItemDoubleClicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data is not None:
            index = data.get('index')
            property_name = data.get('property')
            if index is not None and property_name is not None:
                if 0 <= index < len(self.canvas.shapes):
                    shape = self.canvas.shapes[index]
                    self.editShapeProperty(shape, property_name)
                    self.canvas.update()
                    self.updateConstructionTree()

    def onTreeContextMenu(self, position):
        item = self.treeWidget.itemAt(position)
        if item:
            data = item.data(0, Qt.UserRole)
            if data is not None and 'index' in data and 'property' not in data:
                menu = QMenu()
                edit_action = QAction('Редактировать', self)
                edit_action.triggered.connect(lambda checked=False, i=item: self.editShape(i))
                delete_action = QAction('Удалить', self)
                delete_action.triggered.connect(lambda checked=False, i=item: self.deleteShape(i))
                rotate_action = QAction('Повернуть', self)
                rotate_action.triggered.connect(lambda checked=False, i=item: self.rotateShape(i))
                
                color_action = QAction('Изменить цвет', self)
                color_action.triggered.connect(lambda checked=False, i=item: self.changeShapeColor(i))
                thickness_action = QAction('Изменить толщину', self)
                thickness_action.triggered.connect(lambda checked=False, i=item: self.changeShapeThickness(i))
                
                menu.addAction(edit_action)
                menu.addAction(delete_action)
                menu.addAction(rotate_action)
                menu.addSeparator()
                menu.addAction(color_action)
                menu.addAction(thickness_action)
                menu.exec(self.treeWidget.viewport().mapToGlobal(position))

    def changeShapeColor(self, item):
        """Изменяет цвет выбранной фигуры"""
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]
                
                if hasattr(self.parent, 'chooseColor'):
                    previous_color = self.parent.canvas.currentColor
                    
                    if hasattr(shape, 'color') and shape.color:
                        self.parent.canvas.currentColor = shape.color
                    
                    self.parent.chooseColor()
                    
                    if hasattr(shape, 'color'):
                        shape.color = self.parent.canvas.currentColor
                    
                    self.parent.canvas.currentColor = previous_color
                    
                    self.canvas.update()
                    self.updateConstructionTree()

    def changeShapeThickness(self, item):
        """Изменяет толщину линии выбранной фигуры"""
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]
                
                if hasattr(shape, 'line_thickness'):
                    thickness, ok = QInputDialog.getDouble(
                        self, 
                        "Толщина линии", 
                        "Введите толщину линии:", 
                        shape.line_thickness, 
                        0.1, 10.0, 1
                    )
                    
                    if ok:
                        shape.line_thickness = thickness
                        self.canvas.update()
                        self.updateConstructionTree()

    def rotateShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]
                
                angle, ok = QInputDialog.getDouble(
                    self, 
                    "Поворот фигуры",
                    "Введите угол поворота в градусах\n(положительный - против часовой стрелки):",
                    0,
                    -360,
                    360,
                    1
                )
                if not ok:
                    return
                    
                if hasattr(shape, 'center'):
                    center = shape.center
                elif hasattr(shape, 'points') and shape.points:
                    x_sum = sum(p.x() for p in shape.points)
                    y_sum = sum(p.y() for p in shape.points)
                    center = QPointF(x_sum / len(shape.points), y_sum / len(shape.points))
                elif hasattr(shape, 'start_point') and hasattr(shape, 'end_point'):
                    center = QPointF(
                        (shape.start_point.x() + shape.end_point.x()) / 2,
                        (shape.start_point.y() + shape.end_point.y()) / 2
                    )
                elif hasattr(shape, 'rect'):
                    center = shape.rect.center()
                else:
                    return
                    
                shape.rotate_around_point(angle, center)
                self.canvas.update()
                self.updateConstructionTree()

    def editShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]
                self.editGeneralShapeProperties(shape)
                # TODO: wtf?
                if isinstance(shape, Line):
                    self.editLineShape(shape)
                elif isinstance(shape, Circle):
                    self.editCircleShape(shape)
                elif isinstance(shape, Rectangle):
                    self.editRectangleShape(shape)
                elif isinstance(shape, Polygon):
                    self.editPolygonShape(shape)
                elif isinstance(shape, CircleByThreePoints):
                    self.editCircleByThreePointsShape(shape)
                elif isinstance(shape, ArcByThreePoints):
                    self.editArcByThreePointsShape(shape)
                elif isinstance(shape, ArcByRadiusChord):
                    self.editArcByRadiusChordShape(shape)
                elif isinstance(shape, BezierSpline):
                    self.editBezierSplineShape(shape)
                elif isinstance(shape, SegmentSpline):
                    self.editSegmentSplineShape(shape)
                else:
                    QMessageBox.information(self, "Редактировать", "Редактирование этого типа фигур не поддерживается.")
                self.canvas.update()
                self.updateConstructionTree()

    def deleteShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and 'index' in data:
            index = data['index']
            if 0 <= index < len(self.canvas.shapes):
                item_text = item.text(0)
                del self.canvas.shapes[index]
                self.canvas.highlighted_shape_index = None
                self.canvas.shapeRemoved.emit()
                self.canvas.update()
                self.parent.statusBar.showMessage(f"Удален объект: {item_text}")

    def editGeneralShapeProperties(self, shape):
        line_types = ['Сплошная', 'Штриховая', 'Штрих-пунктирная', 'Штрих-пунктирная с двумя точками']
        line_type_keys = ['solid', 'dash', 'dash_dot', 'dash_dot_dot']
        current_line_type_index = line_type_keys.index(shape.line_type)
        line_type, ok = QInputDialog.getItem(self, "Тип линии", "Выберите тип линии:", line_types, current_line_type_index, False)
        if ok and line_type:
            shape.line_type = line_type_keys[line_types.index(line_type)]

        thickness, ok = QInputDialog.getDouble(self, "Толщина линии", "Введите толщину линии:", shape.line_thickness, 0.1, 10.0)
        if ok:
            shape.line_thickness = thickness

    def editShapeProperty(self, shape, property_name):
        if property_name == 'line_type':
            line_types = ['Сплошная', 'Штриховая', 'Штрих-пунктирная', 'Штрих-пунктирная с двумя точками']
            line_type_keys = ['solid', 'dash', 'dash_dot', 'dash_dot_dot']
            current_line_type_index = line_type_keys.index(shape.line_type)
            line_type, ok = QInputDialog.getItem(self, "Тип линии", "Выберите тип линии:", line_types, current_line_type_index, False)
            if ok and line_type:
                shape.line_type = line_type_keys[line_types.index(line_type)]
        
        elif property_name == 'line_thickness':
            thickness, ok = QInputDialog.getDouble(self, "Толщина линии", "Введите толщину линии:", shape.line_thickness, 0.1, 10.0)
            if ok:
                shape.line_thickness = thickness
        
        elif property_name == 'color':
            if hasattr(self.parent, 'chooseColor'):
                previous_color = self.parent.canvas.currentColor
                
                if hasattr(shape, 'color') and shape.color:
                    self.parent.canvas.currentColor = shape.color
                
                self.parent.chooseColor()
                
                if hasattr(shape, 'color'):
                    shape.color = self.parent.canvas.currentColor
                
                self.parent.canvas.currentColor = previous_color
        
        # TODO: wtf?
        elif isinstance(shape, Line):
            self.editLineShapeProperty(shape, property_name)
        elif isinstance(shape, Circle):
            self.editCircleShapeProperty(shape, property_name)
        elif isinstance(shape, Rectangle):
            self.editRectangleShapeProperty(shape, property_name)
        elif isinstance(shape, Polygon):
            self.editPolygonShapeProperty(shape, property_name)
        elif isinstance(shape, CircleByThreePoints):
            self.editCircleByThreePointsShapeProperty(shape, property_name)
        elif isinstance(shape, ArcByThreePoints):
            self.editArcByThreePointsShapeProperty(shape, property_name)
        elif isinstance(shape, ArcByRadiusChord):
            self.editArcByRadiusChordShapeProperty(shape, property_name)
        elif isinstance(shape, BezierSpline):
            self.editBezierSplineShapeProperty(shape, property_name)
        elif isinstance(shape, SegmentSpline):
            self.editSegmentSplineShapeProperty(shape, property_name)
        else:
            QMessageBox.information(self, "Редактировать", "Редактирование этого типа фигур не поддерживается.")

    def editLineShapeProperty(self, shape, property_name):
        if property_name == 'start_point':
            x, ok1 = QInputDialog.getDouble(self, "Редактировать начало линии", "Начало X:", value=shape.start_point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, "Редактировать начало линии", "Начало Y:", value=shape.start_point.y())
            if not ok2:
                return
            shape.start_point = QPointF(x, y)
        elif property_name == 'end_point':
            x, ok1 = QInputDialog.getDouble(self, "Редактировать конец линии", "Конец X:", value=shape.end_point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, "Редактировать конец линии", "Конец Y:", value=shape.end_point.y())
            if not ok2:
                return
            shape.end_point = QPointF(x, y)

    def editCircleShapeProperty(self, shape, property_name):
        if property_name == 'center':
            x, ok1 = QInputDialog.getDouble(self, "Редактировать центр окружности", "Центр X:", value=shape.center.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, "Редактировать центр окружности", "Центр Y:", value=shape.center.y())
            if not ok2:
                return
            shape.center = QPointF(x, y)
        elif property_name == 'radius':
            radius, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите радиус:", 1.0, 0.1, 1000.0, 1)
            if not ok:
                return
            shape.radius = radius

    def editRectangleShapeProperty(self, shape, property_name):
        rect = shape.rect
        if property_name == 'top_left':
            x, ok1 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Верхний левый X:", value=rect.topLeft().x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Верхний левый Y:", value=rect.topLeft().y())
            if not ok2:
                return
            rect.moveTopLeft(QPointF(x, y))
            shape.rect = rect
        elif property_name == 'width':
            width, ok = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Ширина:", value=rect.width())
            if not ok:
                return
            rect.setWidth(width)
            shape.rect = rect
        elif property_name == 'height':
            height, ok = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Высота:", value=rect.height())
            if not ok:
                return
            rect.setHeight(height)
            shape.rect = rect

    def editPolygonShapeProperty(self, shape, property_name):
        if property_name.startswith('point_'):
            try:
                point_index = int(property_name.split('_')[1])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self, f"Редактировать вершину {point_index + 1}", "X:", value=point.x())
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self, f"Редактировать вершину {point_index + 1}", "Y:", value=point.y())
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editCircleByThreePointsShapeProperty(self, shape, property_name):
        if property_name.startswith('point_'):
            try:
                point_index = int(property_name.split('_')[1])
            except ValueError:
                return
            if 0 <= point_index < 3:
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "X:", value=point.x())
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "Y:", value=point.y())
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editArcByThreePointsShapeProperty(self, shape, property_name):
        if property_name.startswith('point_'):
            try:
                point_index = int(property_name.split('_')[1])
            except ValueError:
                return
            if 0 <= point_index < 3:
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "X:", value=point.x())
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "Y:", value=point.y())
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editArcByRadiusChordShapeProperty(self, shape, property_name):
        if property_name == 'center':
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать центр дуги", "Центр X:", value=shape.center.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать центр дуги", "Центр Y:", value=shape.center.y())
            if not ok2:
                return
            shape.center = QPointF(x, y)
        elif property_name == 'radius_point':
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать точку радиуса", "X:", value=shape.radius_point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать точку радиуса", "Y:", value=shape.radius_point.y())
            if not ok2:
                return
            shape.radius_point = QPointF(x, y)
        elif property_name == 'chord_point':
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать точку хорды", "X:", value=shape.chord_point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать точку хорды", "Y:", value=shape.chord_point.y())
            if not ok2:
                return
            shape.chord_point = QPointF(x, y)

    def editBezierSplineShapeProperty(self, shape, property_name):
        if property_name.startswith('control_point_'):
            try:
                point_index = int(property_name.split('_')[2])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self, f"Редактировать Контрольную Точку {point_index + 1}", "X:", value=point.x())
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self, f"Редактировать Контрольную Точку {point_index + 1}", "Y:", value=point.y())
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editSegmentSplineShapeProperty(self, shape, property_name):
        if property_name.startswith('point_'):
            try:
                point_index = int(property_name.split('_')[1])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "X:", value=point.x())
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self, f"Редактировать Точку {point_index + 1}", "Y:", value=point.y())
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editLineShape(self, shape):
        start_x, ok1 = QInputDialog.getDouble(self, "Редактировать линию", "Начало X:", value=shape.start_point.x())
        if not ok1:
            return
        start_y, ok2 = QInputDialog.getDouble(self, "Редактировать линию", "Начало Y:", value=shape.start_point.y())
        if not ok2:
            return
        end_x, ok3 = QInputDialog.getDouble(self, "Редактировать линию", "Конец X:", value=shape.end_point.x())
        if not ok3:
            return
        end_y, ok4 = QInputDialog.getDouble(self, "Редактировать линию", "Конец Y:", value=shape.end_point.y())
        if not ok4:
            return
        shape.start_point = QPointF(start_x, start_y)
        shape.end_point = QPointF(end_x, end_y)

    def editCircleShape(self, shape):
        center_x, ok1 = QInputDialog.getDouble(self, "Редактировать окружность", "Центр X:", value=shape.center.x())
        if not ok1:
            return
        center_y, ok2 = QInputDialog.getDouble(self, "Редактировать окружность", "Центр Y:", value=shape.center.y())
        if not ok2:
            return
        radius, ok3 = QInputDialog.getDouble(self, "Редактировать окружность", "Радиус:", value=shape.radius, minValue=0.1)
        if not ok3:
            return
        shape.center = QPointF(center_x, center_y)
        shape.radius = radius

    def editRectangleShape(self, shape):
        rect = shape.rect
        top_left_x, ok1 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Верхний левый X:", value=rect.topLeft().x())
        if not ok1:
            return
        top_left_y, ok2 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Верхний левый Y:", value=rect.topLeft().y())
        if not ok2:
            return
        width, ok3 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Ширина:", value=rect.width())
        if not ok3:
            return
        height, ok4 = QInputDialog.getDouble(self, "Редактировать прямоугольник", "Высота:", value=rect.height())
        if not ok4:
            return
        shape.rect = QRectF(QPointF(top_left_x, top_left_y), QSizeF(width, height))

    def editPolygonShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            coord_str = f"{point.x():.2f} {point.y():.2f}"
            coord_input, ok = QInputDialog.getText(self, "Редактировать многоугольник", f"Вершина {i+1} (X Y):", text=coord_str)
            if not ok:
                return
            try:
                x_str, y_str = coord_input.strip().split()
                x = float(x_str)
                y = float(y_str)
                shape.points[i] = QPointF(x, y)
            except ValueError:
                QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод. Пожалуйста, введите два числа, разделенных пробелом.")
                return

    def editCircleByThreePointsShape(self, shape):
        for i in range(3):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(self, f"Редактировать Точку {i + 1}", "X:", value=point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, f"Редактировать Точку {i + 1}", "Y:", value=point.y())
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editArcByThreePointsShape(self, shape):
        for i in range(3):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(self, f"Редактировать Точку {i + 1}", "X:", value=point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(self, f"Редактировать Точку {i + 1}", "Y:", value=point.y())
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editArcByRadiusChordShape(self, shape):
        self.editArcByRadiusChordShapeProperty(shape, 'center')
        self.editArcByRadiusChordShapeProperty(shape, 'radius_point')
        self.editArcByRadiusChordShapeProperty(shape, 'chord_point')

    def editBezierSplineShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Контрольную Точку {i + 1}", "X:", value=point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Контрольную Точку {i + 1}", "Y:", value=point.y())
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editSegmentSplineShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "X:", value=point.x())
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "Y:", value=point.y())
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)
