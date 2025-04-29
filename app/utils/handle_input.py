import math
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QInputDialog,
)
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from app.core.line import Line
from app.core.circle import Circle, CircleByThreePoints
from app.core.arc import ArcByThreePoints, ArcByRadiusChord
from app.core.polygon import Polygon
from app.core.rectangle import Rectangle

# def handle_manual_input(self):
#     if self.drawingMode == 'arc_radius_chord':
#         if self.centerPoint is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты центра X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты центра R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.centerPoint = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                 "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.centerPoint is not None and self.radius_point is None:
#             radius, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите радиус:", min=0.1)
#             if not ok:
#                 return
#             else:
#                 x = self.centerPoint.x() + radius
#                 y = self.centerPoint.y()
#                 self.radius_point = QPointF(x, y)
#                 return
#         if self.centerPoint is not None and self.radius_point is not None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты конца хорды X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты конца хорды R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 chord_point = QPointF(x, y)
#                 self.current_shape = ArcByRadiusChord(self.centerPoint, self.radius_point, chord_point,
#                                                 self.lineType, self.lineThickness,
#                                                 dash_parameters=self.dash_parameters,
#                                                 dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#                 self.shapes.append(self.current_shape)
#                 self.shapeAdded.emit()
#                 self.current_shape = None
#                 self.centerPoint = None
#                 self.radius_point = None
#                 self.update()
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                 "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return

#     elif self.drawingMode == 'line':
#         if len(self.points) == 0:
#                     prompt_text = "Введите координаты начальной точки X Y через пробел:"
#                     coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#                     if not ok:
#                         return
#                     try:
#                         x_str, y_str = coord_str.strip().split()
#                         x = float(x_str)
#                         y = float(y_str)
#                         self.points.append(QPointF(x, y))
#                     except ValueError:
#                         QMessageBox.warning(self, "Ошибка ввода",
#                             "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                         return
#         if len(self.points) == 1:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты конечной точки X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты конечной точки R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.points.append(QPointF(x, y))
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#             self.current_shape = Line(self.points[0], self.points[1], self.lineType, self.lineThickness,
#                                     dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.points.clear()
#             self.update()

#     elif self.drawingMode == 'circle_center_radius':
#         if self.centerPoint is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты центра X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты центра R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.centerPoint = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.centerPoint is not None:
#             radius, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите радиус:", min=0.1)
#             if not ok:
#                 return
#             self.current_shape = Circle(self.centerPoint, radius, self.lineType, self.lineThickness,
#                                         dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.centerPoint = None
#             self.update()

#     elif self.drawingMode == 'rectangle_sides':
#         if self.start_point is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты начальной вершины X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты начальной вершины R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.start_point = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.start_point is not None:
#             length, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите длину по оси X:", min=0.1)
#             if not ok:
#                 self.start_point = None
#                 return
#             width, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите ширину по оси Y:", min=0.1)
#             if not ok:
#                 self.start_point = None
#                 return
#             # Calculate end_point
#             end_point = QPointF(self.start_point.x() + length, self.start_point.y() + width)
#             rect = QRectF(self.start_point, end_point).normalized()
#             self.current_shape = Rectangle(rect, self.lineType, self.lineThickness,
#                                         dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.start_point = None
#             self.update()

#     elif self.drawingMode == 'rectangle_center':
#         if self.centerPoint is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты центра X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты центра R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.centerPoint = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.centerPoint is not None:
#             dx, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите половину длины по оси X (полудиагональ по X):", min=0.1)
#             if not ok:
#                 self.centerPoint = None
#                 return
#             dy, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите половину длины по оси Y (полудиагональ по Y):", min=0.1)
#             if not ok:
#                 self.centerPoint = None
#                 return
#             topLeft = QPointF(self.centerPoint.x() - dx, self.centerPoint.y() - dy)
#             width = 2 * dx
#             height = 2 * dy
#             rect = QRectF(topLeft, QSizeF(width, height))
#             self.current_shape = Rectangle(rect.normalized(), self.lineType, self.lineThickness,
#                                         dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.centerPoint = None
#             self.update()

#     elif self.drawingMode == 'circle_three_points':
#         while len(self.points) < 3:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = f"Введите координаты точки {len(self.points)+1} X Y через пробел:"
#             else:
#                 prompt_text = f"Введите полярные координаты точки {len(self.points)+1} R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok or coord_str.strip() == '':
#                 break
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.points.append(QPointF(x, y))
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if len(self.points) == 3:
#             self.current_shape = CircleByThreePoints(self.points.copy(), self.lineType, self.lineThickness,
#                                                     dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.points.clear()
#             self.update()

#     elif self.drawingMode == 'arc_three_points':
#         while len(self.points) < 3:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = f"Введите координаты точки {len(self.points)+1} X Y через пробел:"
#             else:
#                 prompt_text = f"Введите полярные координаты точки {len(self.points)+1} R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok or coord_str.strip() == '':
#                 break
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.points.append(QPointF(x, y))
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода", "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if len(self.points) == 3:
#             self.current_shape = ArcByThreePoints(self.points.copy(), self.lineType, self.lineThickness,
#                                                 dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.points.clear()
#             self.update()

#         if self.centerPoint is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты центра X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты центра R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.centerPoint = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                     "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.centerPoint is not None and self.radius_point is None:
#             radius, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите радиус:", min=0.1)
#             if not ok:
#                 self.centerPoint = None
#                 return
#             else:
#                 x = self.centerPoint.x() + radius
#                 y = self.centerPoint.y()
#                 self.radius_point = QPointF(x, y)
#         if self.centerPoint is not None and self.radius_point is not None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты конца хорды X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты конца хорды R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok or coord_str.strip() == '':
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 chord_point = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                     "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#             self.current_shape = ArcByRadiusChord(self.centerPoint, self.radius_point, chord_point,
#                                                 self.lineType, self.lineThickness,
#                                                 dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#             self.shapes.append(self.current_shape)
#             self.shapeAdded.emit()
#             self.current_shape = None
#             self.centerPoint = None
#             self.radius_point = None
#             self.update()

#     elif self.drawingMode == 'polygon':
#         while True:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты вершины X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты вершины R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok or coord_str.strip() == '':
#                 break
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.points.append(QPointF(x, y))
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                     "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 continue
#         self.update()

#     elif self.drawingMode in ['polygon_inscribed', 'polygon_circumscribed']:
#         if self.centerPoint is None:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты центра X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты центра R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok:
#                 return
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.centerPoint = QPointF(x, y)
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                     "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 return
#         if self.numSides == 0:
#             numSides, ok = QInputDialog.getInt(self, "Количество сторон", "Введите количество сторон:", 3, 3, 100, 1)
#             if ok:
#                 self.numSides = numSides
#             else:
#                 self.centerPoint = None
#                 return
#         radius, ok = QInputDialog.getDouble(self, "Ввод параметров", "Введите радиус:", min=0.1)
#         if not ok:
#             self.centerPoint = None
#             self.numSides = 0
#             return
#         angle = 0
#         x = self.centerPoint.x() + radius * math.cos(angle)
#         y = self.centerPoint.y() + radius * math.sin(angle)
#         radius_point = QPointF(x, y)
#         polygon_points = self.calculate_regular_polygon(self.centerPoint, radius_point, self.numSides, self.drawingMode)
#         self.current_shape = Polygon(polygon_points, self.lineType, self.lineThickness,
#                                     dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
#                                                 color=self.currentColor)
#         self.shapes.append(self.current_shape)
#         self.shapeAdded.emit()
#         self.current_shape = None
#         self.centerPoint = None
#         self.numSides = 0
#         self.update()

#     elif self.drawingMode == 'spline_bezier' or self.drawingMode == 'spline_segments':
#         while True:
#             if self.inputCoordinateSystem == 'cartesian':
#                 prompt_text = "Введите координаты точки X Y через пробел:"
#             else:
#                 prompt_text = "Введите полярные координаты точки R θ через пробел (θ в градусах):"
#             coord_str, ok = QInputDialog.getText(self, "Ввод координат", prompt_text)
#             if not ok or coord_str.strip() == '':
#                 break
#             try:
#                 x_str, y_str = coord_str.strip().split()
#                 if self.inputCoordinateSystem == 'cartesian':
#                     x = float(x_str)
#                     y = float(y_str)
#                 else:
#                     r = float(x_str)
#                     theta_degrees = float(y_str)
#                     theta_radians = math.radians(theta_degrees)
#                     x = r * math.cos(theta_radians)
#                     y = r * math.sin(theta_radians)
#                 self.points.append(QPointF(x, y))
#             except ValueError:
#                 QMessageBox.warning(self, "Ошибка ввода",
#                                     "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.")
#                 continue
#         self.update()


def handle_manual_input(parent_window, canvas):
    if (
        hasattr(parent_window, "line_input_dock")
        and parent_window.line_input_dock is not None
    ):
        parent_window.line_input_dock.close()
    parent_window.line_input_dock = QDockWidget("Ручной ввод", parent_window)
    parent_window.line_input_dock.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
    )
    parent_window.addDockWidget(Qt.LeftDockWidgetArea, parent_window.line_input_dock)
    # Создаем виджет и поля для ввода
    dock_widget = QWidget()
    layout = QVBoxLayout()
    if canvas.drawingMode == "line":
        # Поля для координат
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            # Метки для отображения координатной системы
            parent_window.coord_system_label = QLabel("Система координат: Декартова")

            # Создаем форму для ввода координат
            form_layout.addRow("X начальной точки:", parent_window.input_1)
            form_layout.addRow("Y начальной точки:", parent_window.input_2)
            form_layout.addRow("X конечной точки:", parent_window.input_3)
            form_layout.addRow("Y конечной точки:", parent_window.input_4)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R начальной точки:", parent_window.input_1)
            form_layout.addRow("θ начальной точки (в градусах):", parent_window.input_2)
            form_layout.addRow("R от начальной точки:", parent_window.input_3)
            form_layout.addRow(
                "θ от начальной точки (в градусах):", parent_window.input_4
            )

        # Кнопка подтверждения
        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_line_input(parent_window, canvas)
        )

    elif (
        canvas.drawingMode == "spline_bezier" or canvas.drawingMode == "spline_segments"
    ):
        # Ввод точек до тех пор, пока пользователь не отменит или не оставит поле пустым
        while True:
            if canvas.inputCoordinateSystem == "cartesian":
                prompt_text = "Введите координаты точки X Y через пробел:"
            else:
                prompt_text = (
                    "Введите полярные координаты точки R θ через пробел (θ в градусах):"
                )
            coord_str, ok = QInputDialog.getText(canvas, "Ввод координат", prompt_text)
            if not ok or coord_str.strip() == "":
                break
            try:
                x_str, y_str = coord_str.strip().split()
                if canvas.inputCoordinateSystem == "cartesian":
                    x = float(x_str)
                    y = float(y_str)
                else:
                    r = float(x_str)
                    theta_degrees = float(y_str)
                    theta_radians = math.radians(theta_degrees)
                    x = r * math.cos(theta_radians)
                    y = r * math.sin(theta_radians)
                canvas.points.append(QPointF(x, y))
            except ValueError:
                QMessageBox.warning(
                    canvas,
                    "Ошибка ввода",
                    "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.",
                )
                continue
        canvas.update()

    elif canvas.drawingMode == "rectangle_sides":
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            parent_window.coord_system_label = QLabel("Система координат: Декартова")
            form_layout.addRow("X начальной точки:", parent_window.input_1)
            form_layout.addRow("Y начальной точки:", parent_window.input_2)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R начальной точки:", parent_window.input_1)
            form_layout.addRow("θ начальной точки (в градусах):", parent_window.input_2)
        form_layout.addRow("Длина по оси X:", parent_window.input_3)
        form_layout.addRow("Длина по оси Y:", parent_window.input_4)

        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_rect_sides_input(parent_window, canvas)
        )

    elif canvas.drawingMode == "rectangle_center":
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            parent_window.coord_system_label = QLabel("Система координат: Декартова")
            form_layout.addRow("X центра:", parent_window.input_1)
            form_layout.addRow("Y центра:", parent_window.input_2)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R центра:", parent_window.input_1)
            form_layout.addRow("θ центра (в градусах):", parent_window.input_2)
        form_layout.addRow(
            "Расстояние от центра до правой стороны:", parent_window.input_3
        )
        form_layout.addRow(
            "Расстояние от центра до верхней стороны:", parent_window.input_4
        )

        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_rect_center_input(parent_window, canvas)
        )

    elif canvas.drawingMode == "polygon":
        while True:
            if canvas.inputCoordinateSystem == "cartesian":
                prompt_text = "Введите координаты вершины X Y через пробел:"
            else:
                prompt_text = "Введите полярные координаты вершины R θ через пробел (θ в градусах):"
            coord_str, ok = QInputDialog.getText(canvas, "Ввод координат", prompt_text)
            if not ok or coord_str.strip() == "":
                break
            try:
                x_str, y_str = coord_str.strip().split()
                if canvas.inputCoordinateSystem == "cartesian":
                    x = float(x_str)
                    y = float(y_str)
                else:
                    r = float(x_str)
                    theta_degrees = float(y_str)
                    theta_radians = math.radians(theta_degrees)
                    x = r * math.cos(theta_radians)
                    y = r * math.sin(theta_radians)
                canvas.points.append(QPointF(x, y))
            except ValueError:
                QMessageBox.warning(
                    canvas,
                    "Ошибка ввода",
                    "Некорректный ввод координат. Пожалуйста, введите два числа, разделенных пробелом.",
                )
                continue
        canvas.update()

    elif canvas.drawingMode in ["polygon_inscribed", "polygon_circumscribed"]:
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            parent_window.coord_system_label = QLabel("Система координат: Декартова")
            form_layout.addRow("X центра:", parent_window.input_1)
            form_layout.addRow("Y центра:", parent_window.input_2)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R центра:", parent_window.input_1)
            form_layout.addRow("θ центра (в градусах):", parent_window.input_2)
        form_layout.addRow("Радиус окружности:", parent_window.input_3)
        form_layout.addRow("Количество сторон:", parent_window.input_4)

        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_polygon_input(parent_window, canvas)
        )

    elif canvas.drawingMode == "circle_center_radius":
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            parent_window.coord_system_label = QLabel("Система координат: Декартова")
            form_layout.addRow("X центра:", parent_window.input_1)
            form_layout.addRow("Y центра:", parent_window.input_2)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R центра:", parent_window.input_1)
            form_layout.addRow("θ центра (в градусах):", parent_window.input_2)
        form_layout.addRow("Радиус окружности:", parent_window.input_3)

        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_circle_center_input(parent_window, canvas)
        )

    elif canvas.drawingMode in ["circle_three_points", "arc_three_points"]:
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        parent_window.input_5 = QLineEdit()
        parent_window.input_6 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            # Метки для отображения координатной системы
            parent_window.coord_system_label = QLabel("Система координат: Декартова")

            # Создаем форму для ввода координат
            form_layout.addRow("X первой точки:", parent_window.input_1)
            form_layout.addRow("Y первой точки:", parent_window.input_2)
            form_layout.addRow("X второй точки:", parent_window.input_3)
            form_layout.addRow("Y второй точки:", parent_window.input_4)
            form_layout.addRow("X третьей точки:", parent_window.input_5)
            form_layout.addRow("Y третьей точки:", parent_window.input_6)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R первой точки:", parent_window.input_1)
            form_layout.addRow("θ первой точки (в градусах):", parent_window.input_2)
            form_layout.addRow("R второй точки:", parent_window.input_3)
            form_layout.addRow("θ второй точки (в градусах):", parent_window.input_4)
            form_layout.addRow("R третьей точки:", parent_window.input_5)
            form_layout.addRow("θ третьей точки (в градусах):", parent_window.input_6)

        # Кнопка подтверждения
        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_three_points_input(parent_window, canvas)
        )

    elif canvas.drawingMode == "arc_radius_chord":
        parent_window.input_1 = QLineEdit()
        parent_window.input_2 = QLineEdit()
        parent_window.input_3 = QLineEdit()
        parent_window.input_4 = QLineEdit()
        parent_window.input_5 = QLineEdit()
        form_layout = QFormLayout()
        if canvas.inputCoordinateSystem == "cartesian":
            # Метки для отображения координатной системы
            parent_window.coord_system_label = QLabel("Система координат: Декартова")

            # Создаем форму для ввода координат
            form_layout.addRow("X центра:", parent_window.input_1)
            form_layout.addRow("Y центра:", parent_window.input_2)
            form_layout.addRow("Радиус дуги:", parent_window.input_3)
            form_layout.addRow("X конца хорды (ориентир):", parent_window.input_4)
            form_layout.addRow("Y конца хорды (ориентир):", parent_window.input_5)
        else:
            parent_window.coord_system_label = QLabel("Система координат: Полярная")
            form_layout.addRow("R первой точки:", parent_window.input_1)
            form_layout.addRow("θ первой точки (в градусах):", parent_window.input_2)
            form_layout.addRow("Радиус дуги:", parent_window.input_3)
            form_layout.addRow("R конца хорды (ориентир):", parent_window.input_4)
            form_layout.addRow(
                "θ конца хорды (в градусах, ориентир):", parent_window.input_5
            )

        # Кнопка подтверждения
        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(
            lambda: process_arc_chord_input(parent_window, canvas)
        )

        # Собираем все элементы

    if canvas.drawingMode not in ["polygon", "spline_bezier", "spline_segments"]:
        layout.addWidget(parent_window.coord_system_label)
        layout.addLayout(form_layout)
        layout.addWidget(confirm_button)

        dock_widget.setLayout(layout)
        parent_window.line_input_dock.setWidget(dock_widget)

        parent_window.line_input_dock.show()


def process_line_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
            canvas.points.append(QPointF(x, y))
            x = float(parent_window.input_3.text())
            y = float(parent_window.input_4.text())
            canvas.points.append(QPointF(x, y))
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            canvas.points.append(QPointF(x, y))
            r = float(parent_window.input_3.text())
            theta_radians = math.radians(float(parent_window.input_4.text()))
            x = x + r * math.cos(theta_radians)
            y = y + r * math.sin(theta_radians)
            canvas.points.append(QPointF(x, y))

        canvas.current_shape = Line(
            canvas.points[0], canvas.points[1], canvas.lineType, canvas.lineThickness
        )
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.points.clear()
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_rect_sides_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
        canvas.start_point = QPointF(x, y)
        length = float(parent_window.input_3.text())
        width = float(parent_window.input_4.text())
        end_point = QPointF(
            canvas.start_point.x() + length, canvas.start_point.y() + width
        )
        rect = QRectF(canvas.start_point, end_point).normalized()
        canvas.current_shape = Rectangle(rect, canvas.lineType, canvas.lineThickness)
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.start_point = None
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_rect_center_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
        canvas.centerPoint = QPointF(x, y)
        dx = float(parent_window.input_3.text())
        dy = float(parent_window.input_4.text())
        topLeft = QPointF(canvas.centerPoint.x() - dx, canvas.centerPoint.y() - dy)
        rect = QRectF(topLeft, QSizeF(dx * 2, dy * 2)).normalized()
        canvas.current_shape = Rectangle(rect, canvas.lineType, canvas.lineThickness)
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.centerPoint = None
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_polygon_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
        canvas.centerPoint = QPointF(x, y)
        radius = float(parent_window.input_3.text())
        sides = int(parent_window.input_4.text())
        x = canvas.centerPoint.x() + radius
        y = canvas.centerPoint.y() + radius
        radius_point = QPointF(x, y)
        polygon_points = canvas.calculate_regular_polygon(
            canvas.centerPoint, radius_point, sides, canvas.drawingMode
        )
        canvas.current_shape = Polygon(
            polygon_points, canvas.lineType, canvas.lineThickness
        )

        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.centerPoint = None
        canvas.numSides = 0
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_circle_center_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
        canvas.centerPoint = QPointF(x, y)
        radius = float(parent_window.input_3.text())
        canvas.current_shape = Circle(
            canvas.centerPoint, radius, canvas.lineType, canvas.lineThickness
        )
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.centerPoint = None
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_three_points_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
            or not parent_window.input_5.text()
            or not parent_window.input_6.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
            canvas.points.append(QPointF(x, y))
            x = float(parent_window.input_3.text())
            y = float(parent_window.input_4.text())
            canvas.points.append(QPointF(x, y))
            x = float(parent_window.input_5.text())
            y = float(parent_window.input_6.text())
            canvas.points.append(QPointF(x, y))
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            canvas.points.append(QPointF(x, y))
            r = float(parent_window.input_3.text())
            theta_radians = math.radians(float(parent_window.input_4.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            canvas.points.append(QPointF(x, y))
            r = float(parent_window.input_5.text())
            theta_radians = math.radians(float(parent_window.input_6.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            canvas.points.append(QPointF(x, y))
        if canvas.drawingMode == "circle_three_points":
            canvas.current_shape = CircleByThreePoints(
                canvas.points.copy(), canvas.lineType, canvas.lineThickness
            )
        else:
            canvas.current_shape = ArcByThreePoints(
                canvas.points.copy(), canvas.lineType, canvas.lineThickness
            )
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.points.clear()
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )


def process_arc_chord_input(parent_window, canvas):
    try:
        if (
            not parent_window.input_1.text()
            or not parent_window.input_2.text()
            or not parent_window.input_3.text()
            or not parent_window.input_4.text()
            or not parent_window.input_5.text()
        ):
            QMessageBox.warning(
                parent_window, "Ошибка ввода", "Пожалуйста, заполните все поля."
            )
            return
        if canvas.inputCoordinateSystem == "cartesian":
            x = float(parent_window.input_1.text())
            y = float(parent_window.input_2.text())
            canvas.centerPoint = QPointF(x, y)
            x = float(parent_window.input_4.text())
            y = float(parent_window.input_5.text())
            chord_point = QPointF(x, y)
        else:
            r = float(parent_window.input_1.text())
            theta_radians = math.radians(float(parent_window.input_2.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            canvas.centerPoint = QPointF(x, y)
            r = float(parent_window.input_4.text())
            theta_radians = math.radians(float(parent_window.input_5.text()))
            x = r * math.cos(theta_radians)
            y = r * math.sin(theta_radians)
            chord_point = QPointF(x, y)
        canvas.radius_point = None
        radius = float(parent_window.input_3.text())
        x = canvas.centerPoint.x() + radius
        y = canvas.centerPoint.y()
        canvas.radius_point = QPointF(x, y)
        canvas.current_shape = ArcByRadiusChord(
            canvas.centerPoint,
            canvas.radius_point,
            chord_point,
            canvas.lineType,
            canvas.lineThickness,
        )
        canvas.shapes.append(canvas.current_shape)
        canvas.current_shape = None
        canvas.centerPoint = None
        canvas.radius_point = None
        canvas.update()
        parent_window.line_input_dock.hide()
    except ValueError:
        QMessageBox.warning(
            parent_window,
            "Ошибка ввода",
            "Некорректный ввод координат. Пожалуйста, введите числа.",
        )
