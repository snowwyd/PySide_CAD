from PySide6.QtWidgets import (
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QInputDialog,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtGui import QAction, QColor, QBrush, QIcon, QLinearGradient, QPalette
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from PySide6.QtGui import QFont
from app.objects.line import Line
from app.objects.circle import Circle, CircleByThreePoints
from app.objects.arc import ArcByThreePoints, ArcByRadiusChord
from app.objects.polygon import Polygon
from app.objects.rectangle import Rectangle
from app.objects.spline import BezierSpline, SegmentSpline
from PySide6.QtWidgets import QTreeWidgetItemIterator
from app.config.config import *


class ConstructionTree(QDockWidget):
    def __init__(self, parent, canvas):
        super().__init__(parent)
        self.parent = parent
        self.canvas = canvas
        self.setAllowedAreas(Qt.LeftDockWidgetArea)

        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Редактирование объектов")
        title_label.setFont(QFont("Consolas", 12))
        header_layout.addWidget(title_label)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setFont(QFont("Arial", 10))

        self.main_layout.addWidget(header_widget)
        # self.main_layout.addWidget(self.buttons_widget)
        self.main_layout.addWidget(self.treeWidget)

        self.setWidget(self.main_widget)

        self.canvas.shapeAdded.connect(self.updateConstructionTree)
        self.canvas.shapeRemoved.connect(self.updateConstructionTree)
        self.canvas.zPressed.connect(self.updateConstructionTree)
        self.treeWidget.itemClicked.connect(self.onTreeItemClicked)
        self.treeWidget.itemDoubleClicked.connect(self.onTreeItemDoubleClicked)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.onTreeContextMenu)

        self.updateThemeStyles()

        self.updateConstructionTree()

    def saveExpandState(self):
        expanded_states = {}
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            # Сохраняем состояние только для групп
            if item.childCount() > 0:
                expanded_states[item.text(0)] = item.isExpanded()
            iterator += 1
        return expanded_states

    def restoreExpandState(self, expanded_states):
        if not expanded_states:
            return
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item.text(0) in expanded_states and item.childCount() > 0:
                item.setExpanded(expanded_states[item.text(0)])
            iterator += 1

    def updateThemeStyles(self):
        palette = QPalette()
        primary = QColor(PRIMARY_COLOR)
        on_primary = QColor(ON_PRIMARY_COLOR)
        secondary = QColor("#03DAC6")
        surface = QColor("#FFFFFF")
        background = QColor("#FAFAFA")
        on_surface = QColor("#000000")
        self.setStyleSheet(
            f"""
            QTreeWidget {{
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid white;
            }}
            QTreeWidget::item:selected {{
                background: #e3f2fd;
                color: #1976d2;
            }}
            QPushButton {{
                background-color: {primary.name()};
                color: {on_primary.name()};
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #1976d2;
            }}
            QTreeWidget::item:has-children {{
                background-color: white;
                border-left: 4px solid {primary.name()};
                margin: 2px;
            }}
        """
        )

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
            "Line": "Линия",
            "Circle": "Окружность (центр и радиус)",
            "Rectangle": "Прямоугольник",
            "Polygon": "Многоугольник",
            "CircleByThreePoints": "Окружность (3 точки)",
            "ArcByThreePoints": "Дуга (3 точки)",
            "ArcByRadiusChord": "Дуга (радиус и хорда)",
            "BezierSpline": "Сплайн Безье",
            "SegmentSpline": "Сплайн по отрезкам",
        }

        shape_icons = {
            "Line": "resources/icons/дерево_линия.png",
            "Circle": "resources/icons/окружность_по_центру_и_радиусу.png",
            "Rectangle": "resources/icons/дерево_прямоугольник.png",
            "Polygon": "resources/icons/дерево_многоугольник.png",
            "CircleByThreePoints": "resources/icons/окружность_по_трём_точкам.png",
            "ArcByThreePoints": "resources/icons/дуга_по_трём_точкам.png",
            "ArcByRadiusChord": "resources/icons/дуга_по_радиусу_и_хорде.png",
            "BezierSpline": "resources/icons/сплайн_безье.png",
            "SegmentSpline": "resources/icons/сплайн_по_отрезкам.png",
        }

        line_type_names = {
            "solid": "Сплошная",
            "dash": "Штриховая",
            "dash_dot": "Штрих-пунктирная",
            "dash_dot_dot": "Штрих-пунктирная с двумя точками",
        }

        is_dark_theme = (
            self.parent.is_dark_theme
            if hasattr(self.parent, "is_dark_theme")
            else False
        )

        # Группировка объектов по типам
        grouped_shapes = {}
        for idx, shape in enumerate(self.canvas.shapes):
            shape_type = type(shape).__name__
            if shape_type not in grouped_shapes:
                grouped_shapes[shape_type] = []
            grouped_shapes[shape_type].append((idx, shape))

        # Создание групп
        for group_type in grouped_shapes:
            group_item = QTreeWidgetItem([shape_names.get(group_type, group_type)])
            group_item.setIcon(
                0, QIcon(shape_icons.get(group_type, "icons/default.png"))
            )
            group_item.setBackground(
                0, QBrush(QColor("#2E2E2E") if is_dark_theme else "#E0E0E0")
            )
            group_item.setForeground(
                0, QColor("#FFFFFF") if is_dark_theme else QColor("#000000")
            )
            group_item.setFont(0, QFont("Consolas", 10, QFont.Bold))
            self.treeWidget.addTopLevelItem(group_item)

            # Добавление объектов в группы
            for index, shape in grouped_shapes[group_type]:
                shape_type = type(shape).__name__
                item_text = f"{shape_names.get(shape_type, shape_type)} {index + 1}"
                tree_item = QTreeWidgetItem([item_text])

                # Настройка иконки
                # icon = QIcon(shape_icons.get(shape_type, "icons/default.png"))
                # tree_item.setIcon(0, icon)

                # Градиентный фон для элемента
                gradient = QLinearGradient(0, 0, 100, 0)
                base_color = QColor(PRIMARY_COLOR)
                gradient.setColorAt(0.0, base_color.lighter(150))
                gradient.setColorAt(1.0, base_color)
                tree_item.setBackground(0, QBrush(gradient))

                # Сохраняем данные об объекте
                tree_item.setData(0, Qt.UserRole, {"index": index})

                # Добавление в группу
                group_item.addChild(tree_item)

                # Создание дочерних элементов (аналогично оригинальному коду)
                def create_child_item(
                    parent, text, index=None, property_name=None, is_editable=True
                ):
                    item = QTreeWidgetItem([text])
                    if is_editable and index is not None:
                        item.setData(
                            0, Qt.UserRole, {"index": index, "property": property_name}
                        )
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                    parent.addChild(item)
                    item.setFont(0, QFont("Consolas", 9))
                    if is_dark_theme:
                        item.setForeground(0, QColor("#ffffff"))
                    return item

                if hasattr(shape, "line_type"):
                    line_type_text = line_type_names.get(
                        shape.line_type, shape.line_type
                    )
                    create_child_item(
                        tree_item, f"Тип линии: {line_type_text}", index, "line_type"
                    )

                if hasattr(shape, "line_thickness"):
                    create_child_item(
                        tree_item,
                        f"Толщина линии: {shape.line_thickness:.2f}",
                        index,
                        "line_thickness",
                    )

                # Здесь добавляются специфичные для типа фигуры параметры
                # (оставшаяся часть кода создания дочерних элементов из оригинального метода)

                if isinstance(shape, Line):
                    create_child_item(
                        tree_item,
                        f"Начало: ({shape.start_point.x():.2f}, {shape.start_point.y():.2f})",
                        index,
                        "start_point",
                    )
                    create_child_item(
                        tree_item,
                        f"Конец: ({shape.end_point.x():.2f}, {shape.end_point.y():.2f})",
                        index,
                        "end_point",
                    )
                    create_child_item(
                        tree_item,
                        f"Длина: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, Circle):
                    create_child_item(
                        tree_item,
                        f"Центр: ({shape.center.x():.2f}, {shape.center.y():.2f})",
                        index,
                        "center",
                    )
                    create_child_item(
                        tree_item, f"Радиус: {shape.radius:.2f}", index, "radius"
                    )
                    create_child_item(
                        tree_item,
                        f"Длина окружности: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, Rectangle):
                    rect = shape.rect
                    topLeft = rect.topLeft()
                    create_child_item(
                        tree_item,
                        f"Верхний левый угол: ({topLeft.x():.2f}, {topLeft.y():.2f})",
                        index,
                        "top_left",
                    )
                    create_child_item(
                        tree_item, f"Ширина: {rect.width():.2f}", index, "width"
                    )
                    create_child_item(
                        tree_item, f"Высота: {rect.height():.2f}", index, "height"
                    )
                    create_child_item(
                        tree_item,
                        f"Периметр: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, Polygon):
                    for i, p in enumerate(shape.points):
                        create_child_item(
                            tree_item,
                            f"Вершина {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                            index,
                            f"point_{i}",
                        )
                    create_child_item(
                        tree_item,
                        f"Периметр: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, CircleByThreePoints):
                    for i, p in enumerate(shape.points):
                        create_child_item(
                            tree_item,
                            f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                            index,
                            f"point_{i}",
                        )
                    create_child_item(
                        tree_item,
                        f"Длина окружности: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, ArcByThreePoints):
                    for i, p in enumerate(shape.points):
                        create_child_item(
                            tree_item,
                            f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                            index,
                            f"point_{i}",
                        )
                    create_child_item(
                        tree_item,
                        f"Длина дуги: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, ArcByRadiusChord):
                    create_child_item(
                        tree_item,
                        f"Центр: ({shape.center.x():.2f}, {shape.center.y():.2f})",
                        index,
                        "center",
                    )
                    create_child_item(
                        tree_item,
                        f"Точка радиуса: ({shape.radius_point.x():.2f}, {shape.radius_point.y():.2f})",
                        index,
                        "radius_point",
                    )
                    create_child_item(
                        tree_item,
                        f"Точка хорды: ({shape.chord_point.x():.2f}, {shape.chord_point.y():.2f})",
                        index,
                        "chord_point",
                    )
                    create_child_item(
                        tree_item,
                        f"Длина дуги: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, BezierSpline):
                    for i, p in enumerate(shape.points):
                        create_child_item(
                            tree_item,
                            f"Контрольная точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                            index,
                            f"control_point_{i}",
                        )
                    create_child_item(
                        tree_item,
                        f"Длина сплайна: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                elif isinstance(shape, SegmentSpline):
                    for i, p in enumerate(shape.points):
                        create_child_item(
                            tree_item,
                            f"Точка {i + 1}: ({p.x():.2f}, {p.y():.2f})",
                            index,
                            f"point_{i}",
                        )
                    create_child_item(
                        tree_item,
                        f"Длина сплайна: {shape.get_total_length():.2f}",
                        is_editable=False,
                    )

                else:
                    create_child_item(
                        tree_item, "Нет дополнительной информации", is_editable=False
                    )

        # Восстановление состояния развернутости
        self.restoreExpandState(expanded_states)

        # Подсветка текущего элемента
        if self.canvas.highlighted_shape_index is not None:
            iterator = QTreeWidgetItemIterator(self.treeWidget)
            while iterator.value():
                item = iterator.value()
                data = item.data(0, Qt.UserRole)
                if data and data.get("index") == self.canvas.highlighted_shape_index:
                    self.treeWidget.setCurrentItem(item)
                    break
                iterator += 1

    def onTreeItemClicked(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and "index" in data:
            index = data["index"]
            if 0 <= index < len(self.canvas.shapes):
                self.canvas.highlighted_shape_index = index
                self.canvas.repaint()

    def onTreeItemDoubleClicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data is not None:
            index = data.get("index")
            property_name = data.get("property")
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
            if data is not None and "index" in data and "property" not in data:
                menu = QMenu()
                edit_action = QAction("Редактировать", self)
                edit_action.triggered.connect(
                    lambda checked=False, i=item: self.editShape(i)
                )
                delete_action = QAction("Удалить", self)
                delete_action.triggered.connect(
                    lambda checked=False, i=item: self.deleteShape(i)
                )
                rotate_action = QAction("Повернуть", self)
                rotate_action.triggered.connect(
                    lambda checked=False, i=item: self.rotateShape(i)
                )

                thickness_action = QAction("Изменить толщину", self)
                thickness_action.triggered.connect(
                    lambda checked=False, i=item: self.changeShapeThickness(i)
                )

                menu.addAction(edit_action)
                menu.addAction(delete_action)
                menu.addAction(rotate_action)
                menu.addSeparator()
                menu.addAction(thickness_action)
                menu.exec(self.treeWidget.viewport().mapToGlobal(position))

    def changeShapeThickness(self, item):
        """Изменяет толщину линии выбранной фигуры"""
        data = item.data(0, Qt.UserRole)
        if data is not None and "index" in data:
            index = data["index"]
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]

                if hasattr(shape, "line_thickness"):
                    thickness, ok = QInputDialog.getDouble(
                        self,
                        "Толщина линии",
                        "Введите толщину линии:",
                        shape.line_thickness,
                        0.1,
                        10.0,
                        1,
                    )

                    if ok:
                        shape.line_thickness = thickness
                        self.canvas.update()
                        self.updateConstructionTree()

    def rotateShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and "index" in data:
            index = data["index"]
            if 0 <= index < len(self.canvas.shapes):
                shape = self.canvas.shapes[index]

                angle, ok = QInputDialog.getDouble(
                    self,
                    "Поворот фигуры",
                    "Введите угол поворота в градусах\n(положительный - против часовой стрелки):",
                    0,
                    -360,
                    360,
                    1,
                )
                if not ok:
                    return

                if hasattr(shape, "center"):
                    center = shape.center
                elif hasattr(shape, "points") and shape.points:
                    x_sum = sum(p.x() for p in shape.points)
                    y_sum = sum(p.y() for p in shape.points)
                    center = QPointF(
                        x_sum / len(shape.points), y_sum / len(shape.points)
                    )
                elif hasattr(shape, "start_point") and hasattr(shape, "end_point"):
                    center = QPointF(
                        (shape.start_point.x() + shape.end_point.x()) / 2,
                        (shape.start_point.y() + shape.end_point.y()) / 2,
                    )
                elif hasattr(shape, "rect"):
                    center = shape.rect.center()
                else:
                    return

                shape.rotate_around_point(angle, center)
                self.canvas.update()
                self.updateConstructionTree()

    def editShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and "index" in data:
            index = data["index"]
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
                    QMessageBox.information(
                        self,
                        "Редактировать",
                        "Редактирование этого типа фигур не поддерживается.",
                    )
                self.canvas.update()
                self.updateConstructionTree()

    def deleteShape(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and "index" in data:
            index = data["index"]
            if 0 <= index < len(self.canvas.shapes):
                item_text = item.text(0)
                del self.canvas.shapes[index]
                self.canvas.highlighted_shape_index = None
                self.canvas.shapeRemoved.emit()
                self.canvas.update()
                self.parent.statusBar.showMessage(f"Удален объект: {item_text}")

    def editGeneralShapeProperties(self, shape):
        line_types = [
            "Сплошная",
            "Штриховая",
            "Штрих-пунктирная",
            "Штрих-пунктирная с двумя точками",
        ]
        line_type_keys = ["solid", "dash", "dash_dot", "dash_dot_dot"]
        current_line_type_index = line_type_keys.index(shape.line_type)
        line_type, ok = QInputDialog.getItem(
            self,
            "Тип линии",
            "Выберите тип линии:",
            line_types,
            current_line_type_index,
            False,
        )
        if ok and line_type:
            shape.line_type = line_type_keys[line_types.index(line_type)]

        thickness, ok = QInputDialog.getDouble(
            self,
            "Толщина линии",
            "Введите толщину линии:",
            shape.line_thickness,
            0.1,
            10.0,
        )
        if ok:
            shape.line_thickness = thickness

    def editShapeProperty(self, shape, property_name):
        if property_name == "line_type":
            line_types = [
                "Сплошная",
                "Штриховая",
                "Штрих-пунктирная",
                "Штрих-пунктирная с двумя точками",
            ]
            line_type_keys = ["solid", "dash", "dash_dot", "dash_dot_dot"]
            current_line_type_index = line_type_keys.index(shape.line_type)
            line_type, ok = QInputDialog.getItem(
                self,
                "Тип линии",
                "Выберите тип линии:",
                line_types,
                current_line_type_index,
                False,
            )
            if ok and line_type:
                shape.line_type = line_type_keys[line_types.index(line_type)]

        elif property_name == "line_thickness":
            thickness, ok = QInputDialog.getDouble(
                self,
                "Толщина линии",
                "Введите толщину линии:",
                shape.line_thickness,
                0.1,
                10.0,
            )
            if ok:
                shape.line_thickness = thickness

        elif property_name == "color":
            if hasattr(self.parent, "chooseColor"):
                previous_color = self.parent.canvas.currentColor

                if hasattr(shape, "color") and shape.color:
                    self.parent.canvas.currentColor = shape.color

                self.parent.chooseColor()

                if hasattr(shape, "color"):
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
            QMessageBox.information(
                self,
                "Редактировать",
                "Редактирование этого типа фигур не поддерживается.",
            )

    def editLineShapeProperty(self, shape, property_name):
        if property_name == "start_point":
            x, ok1 = QInputDialog.getDouble(
                self,
                "Редактировать начало линии",
                "Начало X:",
                value=shape.start_point.x(),
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self,
                "Редактировать начало линии",
                "Начало Y:",
                value=shape.start_point.y(),
            )
            if not ok2:
                return
            shape.start_point = QPointF(x, y)
        elif property_name == "end_point":
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать конец линии", "Конец X:", value=shape.end_point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать конец линии", "Конец Y:", value=shape.end_point.y()
            )
            if not ok2:
                return
            shape.end_point = QPointF(x, y)

    def editCircleShapeProperty(self, shape, property_name):
        if property_name == "center":
            x, ok1 = QInputDialog.getDouble(
                self,
                "Редактировать центр окружности",
                "Центр X:",
                value=shape.center.x(),
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self,
                "Редактировать центр окружности",
                "Центр Y:",
                value=shape.center.y(),
            )
            if not ok2:
                return
            shape.center = QPointF(x, y)
        elif property_name == "radius":
            radius, ok = QInputDialog.getDouble(
                self, "Ввод параметров", "Введите радиус:", 1.0, 0.1, 1000.0, 1
            )
            if not ok:
                return
            shape.radius = radius

    def editRectangleShapeProperty(self, shape, property_name):
        rect = shape.rect
        if property_name == "top_left":
            x, ok1 = QInputDialog.getDouble(
                self,
                "Редактировать прямоугольник",
                "Верхний левый X:",
                value=rect.topLeft().x(),
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self,
                "Редактировать прямоугольник",
                "Верхний левый Y:",
                value=rect.topLeft().y(),
            )
            if not ok2:
                return
            rect.moveTopLeft(QPointF(x, y))
            shape.rect = rect
        elif property_name == "width":
            width, ok = QInputDialog.getDouble(
                self, "Редактировать прямоугольник", "Ширина:", value=rect.width()
            )
            if not ok:
                return
            rect.setWidth(width)
            shape.rect = rect
        elif property_name == "height":
            height, ok = QInputDialog.getDouble(
                self, "Редактировать прямоугольник", "Высота:", value=rect.height()
            )
            if not ok:
                return
            rect.setHeight(height)
            shape.rect = rect

    def editPolygonShapeProperty(self, shape, property_name):
        if property_name.startswith("point_"):
            try:
                point_index = int(property_name.split("_")[1])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self,
                    f"Редактировать вершину {point_index + 1}",
                    "X:",
                    value=point.x(),
                )
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self,
                    f"Редактировать вершину {point_index + 1}",
                    "Y:",
                    value=point.y(),
                )
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editCircleByThreePointsShapeProperty(self, shape, property_name):
        if property_name.startswith("point_"):
            try:
                point_index = int(property_name.split("_")[1])
            except ValueError:
                return
            if 0 <= point_index < 3:
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "X:",
                    value=point.x(),
                )
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "Y:",
                    value=point.y(),
                )
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editArcByThreePointsShapeProperty(self, shape, property_name):
        if property_name.startswith("point_"):
            try:
                point_index = int(property_name.split("_")[1])
            except ValueError:
                return
            if 0 <= point_index < 3:
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "X:",
                    value=point.x(),
                )
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "Y:",
                    value=point.y(),
                )
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editArcByRadiusChordShapeProperty(self, shape, property_name):
        if property_name == "center":
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать центр дуги", "Центр X:", value=shape.center.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать центр дуги", "Центр Y:", value=shape.center.y()
            )
            if not ok2:
                return
            shape.center = QPointF(x, y)
        elif property_name == "radius_point":
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать точку радиуса", "X:", value=shape.radius_point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать точку радиуса", "Y:", value=shape.radius_point.y()
            )
            if not ok2:
                return
            shape.radius_point = QPointF(x, y)
        elif property_name == "chord_point":
            x, ok1 = QInputDialog.getDouble(
                self, "Редактировать точку хорды", "X:", value=shape.chord_point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, "Редактировать точку хорды", "Y:", value=shape.chord_point.y()
            )
            if not ok2:
                return
            shape.chord_point = QPointF(x, y)

    def editBezierSplineShapeProperty(self, shape, property_name):
        if property_name.startswith("control_point_"):
            try:
                point_index = int(property_name.split("_")[2])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Контрольную Точку {point_index + 1}",
                    "X:",
                    value=point.x(),
                )
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Контрольную Точку {point_index + 1}",
                    "Y:",
                    value=point.y(),
                )
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editSegmentSplineShapeProperty(self, shape, property_name):
        if property_name.startswith("point_"):
            try:
                point_index = int(property_name.split("_")[1])
            except ValueError:
                return
            if 0 <= point_index < len(shape.points):
                point = shape.points[point_index]
                x, ok1 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "X:",
                    value=point.x(),
                )
                if not ok1:
                    return
                y, ok2 = QInputDialog.getDouble(
                    self,
                    f"Редактировать Точку {point_index + 1}",
                    "Y:",
                    value=point.y(),
                )
                if not ok2:
                    return
                shape.points[point_index] = QPointF(x, y)

    def editLineShape(self, shape):
        start_x, ok1 = QInputDialog.getDouble(
            self, "Редактировать линию", "Начало X:", value=shape.start_point.x()
        )
        if not ok1:
            return
        start_y, ok2 = QInputDialog.getDouble(
            self, "Редактировать линию", "Начало Y:", value=shape.start_point.y()
        )
        if not ok2:
            return
        end_x, ok3 = QInputDialog.getDouble(
            self, "Редактировать линию", "Конец X:", value=shape.end_point.x()
        )
        if not ok3:
            return
        end_y, ok4 = QInputDialog.getDouble(
            self, "Редактировать линию", "Конец Y:", value=shape.end_point.y()
        )
        if not ok4:
            return
        shape.start_point = QPointF(start_x, start_y)
        shape.end_point = QPointF(end_x, end_y)

    def editCircleShape(self, shape):
        center_x, ok1 = QInputDialog.getDouble(
            self, "Редактировать окружность", "Центр X:", value=shape.center.x()
        )
        if not ok1:
            return
        center_y, ok2 = QInputDialog.getDouble(
            self, "Редактировать окружность", "Центр Y:", value=shape.center.y()
        )
        if not ok2:
            return
        radius, ok3 = QInputDialog.getDouble(
            self,
            "Редактировать окружность",
            "Радиус:",
            value=shape.radius,
            minValue=0.1,
        )
        if not ok3:
            return
        shape.center = QPointF(center_x, center_y)
        shape.radius = radius

    def editRectangleShape(self, shape):
        rect = shape.rect
        top_left_x, ok1 = QInputDialog.getDouble(
            self,
            "Редактировать прямоугольник",
            "Верхний левый X:",
            value=rect.topLeft().x(),
        )
        if not ok1:
            return
        top_left_y, ok2 = QInputDialog.getDouble(
            self,
            "Редактировать прямоугольник",
            "Верхний левый Y:",
            value=rect.topLeft().y(),
        )
        if not ok2:
            return
        width, ok3 = QInputDialog.getDouble(
            self, "Редактировать прямоугольник", "Ширина:", value=rect.width()
        )
        if not ok3:
            return
        height, ok4 = QInputDialog.getDouble(
            self, "Редактировать прямоугольник", "Высота:", value=rect.height()
        )
        if not ok4:
            return
        shape.rect = QRectF(QPointF(top_left_x, top_left_y), QSizeF(width, height))

    def editPolygonShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            coord_str = f"{point.x():.2f} {point.y():.2f}"
            coord_input, ok = QInputDialog.getText(
                self,
                "Редактировать многоугольник",
                f"Вершина {i+1} (X Y):",
                text=coord_str,
            )
            if not ok:
                return
            try:
                x_str, y_str = coord_input.strip().split()
                x = float(x_str)
                y = float(y_str)
                shape.points[i] = QPointF(x, y)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Ошибка ввода",
                    "Некорректный ввод. Пожалуйста, введите два числа, разделенных пробелом.",
                )
                return

    def editCircleByThreePointsShape(self, shape):
        for i in range(3):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "X:", value=point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "Y:", value=point.y()
            )
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editArcByThreePointsShape(self, shape):
        for i in range(3):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "X:", value=point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "Y:", value=point.y()
            )
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editArcByRadiusChordShape(self, shape):
        self.editArcByRadiusChordShapeProperty(shape, "center")
        self.editArcByRadiusChordShapeProperty(shape, "radius_point")
        self.editArcByRadiusChordShapeProperty(shape, "chord_point")

    def editBezierSplineShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Контрольную Точку {i + 1}", "X:", value=point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Контрольную Точку {i + 1}", "Y:", value=point.y()
            )
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)

    def editSegmentSplineShape(self, shape):
        for i in range(len(shape.points)):
            point = shape.points[i]
            x, ok1 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "X:", value=point.x()
            )
            if not ok1:
                return
            y, ok2 = QInputDialog.getDouble(
                self, f"Редактировать Точку {i + 1}", "Y:", value=point.y()
            )
            if not ok2:
                return
            shape.points[i] = QPointF(x, y)
