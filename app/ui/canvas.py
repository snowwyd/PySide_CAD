import math
from PySide6.QtWidgets import QWidget, QInputDialog, QMessageBox
from PySide6.QtGui import QPainter, QColor, QPen, QCursor
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, QSizeF, Signal
from app.core.shapes.line import Line
from app.core.shapes.circle import Circle, CircleByThreePoints
from app.utils.handle_input import handle_manual_input
from app.core.shapes.arc import ArcByThreePoints, ArcByRadiusChord
from app.core.shapes.polygon import Polygon
from app.core.shapes.rectangle import Rectangle
from app.core.shapes.spline import BezierSpline, SegmentSpline

class Canvas(QWidget):
    zPressed = Signal()
    shapeAdded = Signal()
    shapeRemoved = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.handle_manual_input = lambda: handle_manual_input(self)
        self.parent = parent
        self.backgroundColor = QColor(255, 255, 255)
        self.currentColor = QColor(0, 0, 0)
        self.shapes = []
        self.current_shape = None
        self.drawingMode = 'line'
        self.lineType = 'solid'
        self.lineThickness = 1.0

        self.points = []
        self.temp_point = None

        self.panning = False
        self.lastPanPoint = QPoint()
        self.offset = QPoint(0, 0)
        self.scale = 1.0
        self.rotation = 0.0
        self.coordinateSystem = 'cartesian'
        self.inputCoordinateSystem = 'cartesian'

        self.numSides = 0
        self.centerPoint = None
        self.start_point = None
        self.radius_point = None

        self.cursor_position = None

        self.show_axes = True

        self.dash_parameters = {
            'dash_length': 5,
            'dash_gap': 5,
            'dash_space': 3,
            'dot_length': 1,
            'dot_space': 2
        }
        self.dash_auto_mode = False
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.highlighted_shape_index = None
        self.show_grid = True
        self.grid_size = 50
    
    def create_pen(self):
        pen = QPen()
        pen.setColor(self.currentColor)
        pen.setWidthF(self.lineThickness)
        pen.setCosmetic(False)
        pen.setCapStyle(Qt.FlatCap)

        if self.lineType == 'solid':
            pen.setStyle(Qt.SolidLine)
        elif self.lineType in ['dash', 'dash_dot', 'dash_dot_dot']:
            pen.setStyle(Qt.CustomDashLine)
            pen.setDashPattern(self._compute_dash_pattern())
        else:
            pen.setStyle(Qt.SolidLine)

        return pen

    def drawGrid(self, painter):
        if not self.show_grid:
            return
            
        viewRect = self.rect()
        
        corners = [
            self.mapToLogicalCoordinates(viewRect.topLeft()),
            self.mapToLogicalCoordinates(viewRect.topRight()),
            self.mapToLogicalCoordinates(viewRect.bottomLeft()),
            self.mapToLogicalCoordinates(viewRect.bottomRight())
        ]
        
        left = min(corner.x() for corner in corners)
        right = max(corner.x() for corner in corners)
        top = max(corner.y() for corner in corners)
        bottom = min(corner.y() for corner in corners)
        
        margin = self.grid_size * 2
        left = math.floor((left - margin) / self.grid_size) * self.grid_size
        right = math.ceil((right + margin) / self.grid_size) * self.grid_size
        top = math.ceil((top + margin) / self.grid_size) * self.grid_size
        bottom = math.floor((bottom - margin) / self.grid_size) * self.grid_size
        
        gridPen = QPen(QColor(200, 200, 200))
        gridPen.setWidthF(0.5 / self.scale)
        painter.setPen(gridPen)
        
        x = left
        while x <= right:
            painter.drawLine(QPointF(x, bottom), QPointF(x, top))
            x += self.grid_size
            
        y = bottom
        while y <= top:
            painter.drawLine(QPointF(left, y), QPointF(right, y))
            y += self.grid_size

    def highlightShape(self, index):
        self.highlighted_shape_index = index
        self.repaint()

    def setDrawingMode(self, mode):
        if self.drawingMode == 'spline_bezier' and self.current_shape:
            if isinstance(self.current_shape, BezierSpline):
                self.current_shape.is_editing = False
                self.current_shape.editing_index = None
                self.current_shape.highlight_index = None
                if len(self.current_shape.points) >= 3 and self.current_shape not in self.shapes:
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
        
        self.points.clear()
        self.current_shape = None
        self.temp_point = None
        self.centerPoint = None
        self.radius_point = None
        self.start_point = None
        self.numSides = 0
        
        self.drawingMode = mode
        self.update()
        
        if hasattr(self, 'parent') and hasattr(self.parent, 'statusBar'):
            self.parent.statusBar.showMessage(f"Режим рисования: {self.get_drawing_mode_text()}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), self.backgroundColor)
        painter.save()

        painter.translate(self.width() / 2 + self.offset.x(), self.height() / 2 + self.offset.y())
        painter.scale(self.scale, self.scale)
        painter.rotate(self.rotation)
        painter.scale(1, -1)

        self.transform = painter.transform()

        self.drawGrid(painter)

        if self.show_axes:
            length = 10000

            penX = QPen(Qt.red)
            penX.setWidthF(0.5)
            painter.setPen(penX)
            painter.drawLine(-length, 0, length, 0)

            penY = QPen(Qt.blue)
            penY.setWidthF(0.5)
            painter.setPen(penY)
            painter.drawLine(0, -length, 0, length)

        for index, shape in enumerate(self.shapes):
            if index == self.highlighted_shape_index:
                painter.save()
                pen = QPen(Qt.red)
                pen.setWidthF(shape.line_thickness + 2)
                painter.setPen(pen)
                shape.draw(painter)
                painter.restore()
            else:
                shape.draw(painter)

        if self.current_shape:
            temp_pen = QPen()
            temp_pen.setWidthF(self.lineThickness)
            temp_pen.setStyle(Qt.DotLine)
            self.current_shape.draw(painter, pen=temp_pen)
        else:
            temp_pen = QPen()
            temp_pen.setWidthF(self.lineThickness)
            temp_pen.setStyle(Qt.DotLine)
            if self.drawingMode == 'line' and self.points:
                temp_line = Line(self.points[0], self.temp_point, self.lineType, self.lineThickness,
                                 dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_line.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'circle_center_radius' and self.centerPoint and self.temp_point:
                radius = math.hypot(self.temp_point.x() - self.centerPoint.x(),
                                    self.temp_point.y() - self.centerPoint.y())
                temp_circle = Circle(self.centerPoint, radius, self.lineType, self.lineThickness,
                                     dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_circle.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'rectangle_sides' and self.start_point and self.temp_point:
                rect = QRectF(self.start_point, self.temp_point).normalized()
                temp_rect = Rectangle(rect, self.lineType, self.lineThickness,
                                      dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_rect.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'rectangle_center' and self.centerPoint and self.temp_point:
                width = abs(self.temp_point.x() - self.centerPoint.x()) * 2
                height = abs(self.temp_point.y() - self.centerPoint.y()) * 2
                topLeft = QPointF(self.centerPoint.x() - width / 2, self.centerPoint.y() - height / 2)
                rect = QRectF(topLeft, QSizeF(width, height))
                temp_rect = Rectangle(rect.normalized(), self.lineType, self.lineThickness,
                                      dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_rect.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'polygon' and self.points:
                points = self.points.copy()
                if self.temp_point:
                    points.append(self.temp_point)
                if len(points) > 1:
                    temp_polygon = Polygon(points, self.lineType, self.lineThickness,
                                           dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                    temp_polygon.draw(painter, pen=temp_pen)

            elif self.drawingMode in ['spline_bezier', 'spline_segments'] and self.points:
                points = self.points.copy()
                if self.temp_point:
                    points.append(self.temp_point)

                if self.drawingMode == 'spline_bezier':
                    temp_spline = BezierSpline(points, self.lineType, self.lineThickness,
                                               dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                else:
                    temp_spline = SegmentSpline(points, self.lineType, self.lineThickness,
                                                dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_spline.draw(painter, pen=temp_pen)

            elif self.drawingMode in ['polygon_inscribed', 'polygon_circumscribed'] and self.centerPoint and self.temp_point:
                radius_point = self.temp_point
                radius = math.hypot(radius_point.x() - self.centerPoint.x(),
                                    radius_point.y() - self.centerPoint.y())
                pen = QPen(Qt.DotLine)
                pen.setWidthF(1)
                painter.setPen(pen)
                rect = QRectF(self.centerPoint.x() - radius, self.centerPoint.y() - radius,
                              2 * radius, 2 * radius)
                painter.drawEllipse(rect)
                if self.numSides > 0:
                    polygon_points = self.calculate_regular_polygon(self.centerPoint, radius_point, self.numSides,
                                                                    self.drawingMode)
                    temp_polygon = Polygon(polygon_points, self.lineType, self.lineThickness,
                                           dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                    temp_polygon.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'circle_three_points' and len(self.points) == 2 and self.temp_point:
                points = self.points + [self.temp_point]
                temp_circle = CircleByThreePoints(points, self.lineType, self.lineThickness,
                                                  dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_circle.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'arc_three_points' and len(self.points) == 2 and self.temp_point:
                points = self.points + [self.temp_point]
                temp_arc = ArcByThreePoints(points, self.lineType, self.lineThickness,
                                            dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_arc.draw(painter, pen=temp_pen)

            elif self.drawingMode == 'arc_radius_chord' and self.centerPoint and self.radius_point and self.temp_point:
                temp_arc = ArcByRadiusChord(self.centerPoint, self.radius_point, self.temp_point,
                                            self.lineType, self.lineThickness,
                                            dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                               color=self.currentColor)
                temp_arc.draw(painter, pen=temp_pen)

        painter.restore()

        painter.save()
        painter.resetTransform()
        painter.setPen(Qt.black)

        if self.cursor_position:
            x = self.cursor_position.x()
            y = self.cursor_position.y()
            if self.inputCoordinateSystem == 'cartesian':
                text = f"X: {x:.2f}, Y: {y:.2f}"
            else:
                r = math.hypot(x, y)
                theta = math.degrees(math.atan2(y, x))
                text = f"R: {r:.2f}, θ: {theta:.2f}°"

            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()

            rect = self.rect()
            x_pos = rect.right() - text_width - 10
            y_pos = rect.bottom() - 10

            painter.drawText(int(x_pos), int(y_pos), text)

        mode_text = f"Режим: {self.get_drawing_mode_text()}, Линия: {self.get_line_type_text()}, Толщина: {self.lineThickness}, Ввод: {self.get_input_coordinate_system_text()}"
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(mode_text)
        x_pos = (self.width() - text_width) / 2
        y_pos = self.height() - 10

        painter.drawText(int(x_pos), int(y_pos), mode_text)
        
        if self.highlighted_shape_index is not None:
            if 0 <= self.highlighted_shape_index < len(self.shapes):
                highlight_text = f"Выбран объект {self.highlighted_shape_index + 1}"
                highlight_text_width = metrics.horizontalAdvance(highlight_text)
                highlight_x_pos = 10 
                highlight_y_pos = 20
                painter.drawText(int(highlight_x_pos), int(highlight_y_pos), highlight_text)

        painter.restore()

    def get_drawing_mode_text(self):
        mode_translation = {
            'line': 'Линия',
            'circle_center_radius': 'Окружность (центр и радиус)',
            'circle_three_points': 'Окружность (3 точки)',
            'arc_three_points': 'Дуга (3 точки)',
            'arc_radius_chord': 'Дуга (радиус и хорда)',
            'polygon': 'Многоугольник',
            'polygon_inscribed': 'Вписанный многоугольник',
            'polygon_circumscribed': 'Описанный многоугольник',
            'rectangle_sides': 'Прямоугольник по сторонам',
            'rectangle_center': 'Прямоугольник от центра',
            'spline_bezier': 'Сплайн Безье',
            'spline_segments': 'Сплайн по отрезкам'
        }
        return mode_translation.get(self.drawingMode, 'Неизвестный')

    def get_line_type_text(self):
        line_type_translation = {
            'solid': 'Сплошная',
            'dash': 'Штриховая',
            'dash_dot': 'Штрих-пунктирная',
            'dash_dot_dot': 'Штрих-пунктирная с двумя точками'
        }
        return line_type_translation.get(self.lineType, 'Неизвестный')

    def get_input_coordinate_system_text(self):
        return 'Декартовый' if self.inputCoordinateSystem == 'cartesian' else 'Полярный'

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            logicalPos = self.mapToLogicalCoordinates(event.pos())
            coord = self.getCoordinate(logicalPos)

            self.temp_point = coord
            self.cursor_position = coord

            if self.drawingMode == 'line':
                if not self.points:
                    self.points = [coord]
                else:
                    self.points.append(coord)
                    if len(self.points) == 2:
                        self.current_shape = Line(self.points[0], self.points[1], 
                                              self.lineType, self.lineThickness,
                                              dash_parameters=self.dash_parameters, 
                                              dash_auto_mode=self.dash_auto_mode,
                                              color=self.currentColor)
                        self.shapes.append(self.current_shape)
                        self.shapeAdded.emit()
                        self.current_shape = None
                        self.points.clear()
                        self.temp_point = None
                        self.update()

            elif self.drawingMode == 'circle_center_radius':
                if self.centerPoint is None:
                    self.centerPoint = coord
                else:
                    radius = math.hypot(coord.x() - self.centerPoint.x(),
                                    coord.y() - self.centerPoint.y())
                    self.current_shape = Circle(self.centerPoint, radius, 
                                            self.lineType, self.lineThickness,
                                            dash_parameters=self.dash_parameters, 
                                            dash_auto_mode=self.dash_auto_mode,
                                            color=self.currentColor)
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.centerPoint = None
                    self.temp_point = None
                    self.update()

            elif self.drawingMode == 'rectangle_sides':
                if not self.current_shape:
                    self.start_point = coord
                    self.current_shape = Rectangle(QRectF(coord, coord), 
                                               self.lineType, self.lineThickness,
                                               dash_parameters=self.dash_parameters, 
                                               dash_auto_mode=self.dash_auto_mode,
                                               color=self.currentColor)
                else:
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.start_point = None
                    self.temp_point = None
                    self.update()

            elif self.drawingMode == 'circle_three_points':
                self.points.append(coord)
                if len(self.points) == 3:
                    self.current_shape = CircleByThreePoints(
                        self.points.copy(), 
                        self.lineType, 
                        self.lineThickness,
                        dash_parameters=self.dash_parameters, 
                        dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor
                    )
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.points.clear()

            elif self.drawingMode == 'arc_three_points':
                self.points.append(coord)
                if len(self.points) == 3:
                    self.current_shape = ArcByThreePoints(
                        self.points.copy(), 
                        self.lineType, 
                        self.lineThickness,
                        dash_parameters=self.dash_parameters, 
                        dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor
                    )
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.points.clear()

            elif self.drawingMode == 'arc_radius_chord':
                if self.centerPoint is None:
                    self.centerPoint = coord
                elif self.radius_point is None:
                    self.radius_point = coord
                else:
                    self.current_shape = ArcByRadiusChord(
                        self.centerPoint, 
                        self.radius_point, 
                        coord,
                        self.lineType, 
                        self.lineThickness,
                        dash_parameters=self.dash_parameters, 
                        dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor
                    )
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.centerPoint = None
                    self.radius_point = None

            elif self.drawingMode == 'polygon':
                self.points.append(coord)
                self.update()

            elif self.drawingMode in ['polygon_inscribed', 'polygon_circumscribed']:
                if self.centerPoint is None:
                    self.centerPoint = coord
                else:
                    if self.numSides == 0:
                        self.numSides, ok = QInputDialog.getInt(self, "Количество сторон", "Введите количество сторон:", 3, 3, 100, 1)
                        if not ok:
                            self.centerPoint = None
                            self.numSides = 0
                            return
                    polygon_points = self.calculate_regular_polygon(self.centerPoint, coord, self.numSides,
                                                                    self.drawingMode)
                    self.current_shape = Polygon(polygon_points, self.lineType, self.lineThickness,
                                                 dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor)
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.centerPoint = None
                    self.numSides = 0
                    self.temp_point = None
                    self.update()

            elif self.drawingMode == 'rectangle_center':
                if self.centerPoint is None:
                    self.centerPoint = coord
                else:
                    width = abs(coord.x() - self.centerPoint.x()) * 2
                    height = abs(coord.y() - self.centerPoint.y()) * 2
                    topLeft = QPointF(self.centerPoint.x() - width / 2, self.centerPoint.y() - height / 2)
                    rect = QRectF(topLeft, QSizeF(width, height))
                    self.current_shape = Rectangle(rect.normalized(), self.lineType, self.lineThickness,
                                                   dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor)
                    self.shapes.append(self.current_shape)
                    self.shapeAdded.emit()
                    self.current_shape = None
                    self.centerPoint = None
                    self.temp_point = None
                    self.update()
            elif self.drawingMode == 'spline_bezier':
                if self.current_shape and isinstance(self.current_shape, BezierSpline):
                    if not hasattr(self.current_shape, 'is_completed'):
                        self.current_shape.is_completed = False
                    
                    if not self.current_shape.is_completed:
                        clicked_point_index = self.current_shape.get_closest_point(coord)
                        if clicked_point_index is not None:
                            self.current_shape.editing_index = clicked_point_index
                            return

                if not self.current_shape or not self.points:
                    self.points = [coord]
                    self.current_shape = BezierSpline(self.points.copy(), self.lineType, self.lineThickness,
                                                dash_parameters=self.dash_parameters, 
                                                dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor)
                    if not hasattr(self.current_shape, 'is_completed'):
                        self.current_shape.is_completed = False
                else:
                    self.points.append(coord)
                    self.current_shape.points = self.points.copy()

            elif self.drawingMode == 'spline_segments':
                self.points.append(coord)
                self.update()

            self.update()

        elif event.button() == Qt.RightButton:
            if self.drawingMode == 'polygon' and len(self.points) >= 3:
                self.current_shape = Polygon(self.points.copy(), self.lineType, self.lineThickness,
                                             dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor)
                self.shapes.append(self.current_shape)
                self.shapeAdded.emit()
                self.current_shape = None
                self.points.clear()
                self.temp_point = None
                self.update()

            elif self.drawingMode == 'spline_bezier' and len(self.points) >= 3:
                if self.current_shape and isinstance(self.current_shape, BezierSpline):
                    self.current_shape.is_completed = True
                    self.current_shape.is_editing = False
                    new_spline = BezierSpline(
                        self.current_shape.points.copy(), 
                        self.lineType, 
                        self.lineThickness,
                        dash_parameters=self.dash_parameters, 
                        dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor
                    )
                    new_spline.is_completed = True
                    new_spline.is_editing = False
                    self.shapes.append(new_spline)
                    self.shapeAdded.emit()
                
                self.current_shape = None
                self.points = []
                self.temp_point = None
                self.update()

            elif self.drawingMode == 'spline_segments' and len(self.points) >= 2:
                self.current_shape = SegmentSpline(self.points.copy(), self.lineType, self.lineThickness,
                                                   dash_parameters=self.dash_parameters, dash_auto_mode=self.dash_auto_mode,
                        color=self.currentColor)
                self.shapes.append(self.current_shape)
                self.shapeAdded.emit()
                self.current_shape = None
                self.points.clear()
                self.temp_point = None
                self.update()
            else:
                self.points.clear()
                self.current_shape = None
                self.temp_point = None
                self.update()
        elif event.button() == Qt.MiddleButton:
            self.panning = True
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.lastPanPoint = event.pos()

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.pos() - self.lastPanPoint
            self.offset += delta
            self.lastPanPoint = event.pos()
            self.update()
        elif self.drawingMode:
            logicalPos = self.mapToLogicalCoordinates(event.pos())
            coord = self.getCoordinate(logicalPos)
            self.temp_point = coord
            self.cursor_position = coord

            if self.drawingMode == 'line' and self.points:
                if len(self.points) == 1:
                    self.current_shape = Line(self.points[0], coord, self.lineType, self.lineThickness,
                                          dash_parameters=self.dash_parameters, 
                                          dash_auto_mode=self.dash_auto_mode,
                                          color=self.currentColor)
            elif self.drawingMode == 'circle_center_radius' and self.centerPoint:
                radius = math.hypot(coord.x() - self.centerPoint.x(), coord.y() - self.centerPoint.y())
                self.current_shape = Circle(self.centerPoint, radius, self.lineType, self.lineThickness,
                                        dash_parameters=self.dash_parameters, 
                                        dash_auto_mode=self.dash_auto_mode,
                                        color=self.currentColor)
            elif self.drawingMode == 'rectangle_sides' and self.start_point:
                rect = QRectF(self.start_point, coord).normalized()
                self.current_shape = Rectangle(rect, self.lineType, self.lineThickness,
                                          dash_parameters=self.dash_parameters, 
                                          dash_auto_mode=self.dash_auto_mode,
                                          color=self.currentColor)

            elif self.drawingMode == 'rectangle_center' and self.centerPoint:
                pass

            elif self.drawingMode == 'spline_bezier':
                if self.current_shape and isinstance(self.current_shape, BezierSpline):
                    if self.current_shape.editing_index is not None:
                        self.current_shape.points[self.current_shape.editing_index] = coord
                        self.points = self.current_shape.points
                    
                    self.current_shape.highlight_index = self.current_shape.get_closest_point(coord)

            elif self.drawingMode in ['polygon', 'spline_segments']:
                pass
            elif self.drawingMode in ['polygon_inscribed', 'polygon_circumscribed'] and self.centerPoint:
                pass
            elif self.drawingMode == 'arc_radius_chord' and self.centerPoint and self.radius_point:
                pass

            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))
        elif event.button() == Qt.LeftButton:
            if self.drawingMode == 'spline_bezier':
                if self.current_shape and isinstance(self.current_shape, BezierSpline):
                    self.current_shape.editing_index = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.scale += delta * 0.1
        if self.scale < 0.1:
            self.scale = 0.1
        self.update()

    def mapToLogicalCoordinates(self, pos):
        if hasattr(self, 'transform'):
            inverse_transform, ok = self.transform.inverted()
            if ok:
                logical_pos = inverse_transform.map(pos)
                return logical_pos
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось инвертировать преобразование.")
                return QPointF()
        else:
            return QPointF(pos)

    def getCoordinate(self, pos):
        if self.coordinateSystem == 'cartesian':
            return pos
        elif self.coordinateSystem == 'polar':
            r = math.hypot(pos.x(), pos.y())
            theta = math.atan2(pos.y(), pos.x())
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            return QPointF(x, y)

    def calculate_regular_polygon(self, center, radius_point, num_sides, mode):
        radius = math.hypot(radius_point.x() - center.x(), radius_point.y() - center.y())
        points = []
        angle_step = 2 * math.pi / num_sides
        start_angle = math.atan2(radius_point.y() - center.y(), radius_point.x() - center.x())
        if mode == 'polygon_inscribed':
            vertex_radius = radius
        elif mode == 'polygon_circumscribed':
            vertex_radius = radius / math.cos(math.pi / num_sides)
        else:
            vertex_radius = radius
        for i in range(num_sides):
            angle = start_angle + i * angle_step
            x = center.x() + vertex_radius * math.cos(angle)
            y = center.y() + vertex_radius * math.sin(angle)
            points.append(QPointF(x, y))
        return points

    def rotate(self, angle):
        self.rotation += angle
        self.update()

    def zoomIn(self):
        self.scale *= 1.1
        self.update()

    def zoomOut(self):
        self.scale /= 1.1
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_G:
            self.show_grid = not self.show_grid
            self.update()

        if event.key() == Qt.Key_Escape:
            self.points.clear()
            self.current_shape = None
            self.temp_point = None
            self.centerPoint = None
            self.radius_point = None
            self.start_point = None
            self.numSides = 0
            if isinstance(self.current_shape, BezierSpline):
                self.current_shape.is_editing = False
                self.current_shape.editing_index = None
                self.current_shape.highlight_index = None
            self.update()
            if hasattr(self, 'parent') and hasattr(self.parent, 'statusBar'):
                self.parent.statusBar.showMessage('Отмена текущего построения')

        if event.key() == Qt.Key_Z:
            if self.shapes:
                self.shapes.pop()
            self.update()
            if hasattr(self, 'parent') and hasattr(self.parent, 'statusBar'):
                self.parent.statusBar.showMessage('Отмена предыдущего построения')
            self.zPressed.emit()

        if event.key() == Qt.Key_V:
            self.handle_manual_input()
        elif event.key() == Qt.Key_Right and event.modifiers() & Qt.ControlModifier:
            self.rotation += 5
            self.update()
            if hasattr(self, 'parent') and hasattr(self.parent, 'statusBar'):
                self.parent.statusBar.showMessage('Поворот по часовой стрелке')
        elif event.key() == Qt.Key_Left and event.modifiers() & Qt.ControlModifier:
            self.rotation -= 5
            self.update()
            if hasattr(self, 'parent') and hasattr(self.parent, 'statusBar'):
                self.parent.statusBar.showMessage('Поворот против часовой стрелки')
        elif event.key() == Qt.Key_M:
            self.show_axes = not self.show_axes
            self.update()
        elif event.key() == Qt.Key_C:
            self.inputCoordinateSystem = 'cartesian'
            QMessageBox.information(self, "Система координат ввода", "Ввод координат будет производиться в Декартовой системе.")
        elif event.key() == Qt.Key_P:
            self.inputCoordinateSystem = 'polar'
            QMessageBox.information(self, "Система координат ввода", "Ввод координат будет производиться в Полярной системе.")
        else:
            super().keyPressEvent(event)
            
    def _compute_dash_pattern(self):
        """Вспомогательный метод для создания шаблона штриховой линии"""
        pattern = []
        if self.lineType == 'dash':
            pattern = [10, 5]
        elif self.lineType == 'dash_dot':
            pattern = [10, 5, 2, 5]
        elif self.lineType == 'dash_dot_dot':
            pattern = [10, 5, 2, 5, 2, 5]
        return pattern
