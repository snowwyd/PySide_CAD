import ezdxf
import math
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor
from app.core.line import Line
from app.core.circle import Circle, CircleByThreePoints
from app.core.arc import ArcByThreePoints, ArcByRadiusChord
from app.core.polygon import Polygon
from app.core.rectangle import Rectangle
from app.core.spline import BezierSpline, SegmentSpline


def save_to_dxf(shapes, filename):
    doc = ezdxf.new("R12")
    msp = doc.modelspace()

    thickness_layers = {}
    for shape in shapes:
        if hasattr(shape, "line_thickness") and shape.line_thickness > 0:
            thickness = shape.line_thickness
            if thickness not in thickness_layers:
                layer_name = f"Thickness_{thickness}"
                layer = doc.layers.add(layer_name)
                layer.lineweight = thickness * 100
                thickness_layers[thickness] = layer_name

    ensure_line_types_exist(doc)

    for shape in shapes:
        dxfattribs = get_dxf_attributes(shape)

        if hasattr(shape, "line_thickness") and shape.line_thickness > 0:
            thickness = shape.line_thickness
            dxfattribs["layer"] = thickness_layers.get(thickness, "0")

        if isinstance(shape, Line):
            msp.add_line(
                (shape.start_point.x(), shape.start_point.y()),
                (shape.end_point.x(), shape.end_point.y()),
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, Circle):
            msp.add_circle(
                (shape.center.x(), shape.center.y()),
                shape.radius,
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, CircleByThreePoints):
            center, radius = shape.calculate_circle()
            if center and radius:
                msp.add_circle((center.x(), center.y()), radius, dxfattribs=dxfattribs)

        elif isinstance(shape, ArcByThreePoints):
            center, radius, start_angle, span_angle = shape.calculate_arc()
            if center and radius:
                start_angle_deg = start_angle % 360
                span_angle = (
                    span_angle % 360 if span_angle >= 0 else (span_angle % 360) + 360
                )
                end_angle_deg = (start_angle_deg + span_angle) % 360
                if end_angle_deg < start_angle_deg:
                    end_angle_deg += 360
                msp.add_arc(
                    (center.x(), center.y()),
                    radius,
                    start_angle_deg,
                    end_angle_deg,
                    dxfattribs=dxfattribs,
                )

        elif isinstance(shape, ArcByRadiusChord):
            radius, start_angle, span_angle = shape.calculate_arc()
            start_angle_deg = start_angle % 360
            span_angle = (
                span_angle % 360 if span_angle >= 0 else (span_angle % 360) + 360
            )
            end_angle_deg = (start_angle_deg + span_angle) % 360
            if end_angle_deg < start_angle_deg:
                end_angle_deg += 360
            msp.add_arc(
                (shape.center.x(), shape.center.y()),
                radius,
                start_angle_deg,
                end_angle_deg,
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, Rectangle):
            rect = shape.rect
            points = [
                (rect.topLeft().x(), rect.topLeft().y()),
                (rect.topRight().x(), rect.topRight().y()),
                (rect.bottomRight().x(), rect.bottomRight().y()),
                (rect.bottomLeft().x(), rect.bottomLeft().y()),
            ]
            polyline = msp.add_polyline(points, dxfattribs=dxfattribs)
            polyline.is_closed = True

        elif isinstance(shape, Polygon):
            points = [(point.x(), point.y()) for point in shape.points]
            if points:
                polyline = msp.add_polyline(points, dxfattribs=dxfattribs)
                polyline.is_closed = (
                    True if len(points) > 1 and points[0] == points[-1] else False
                )

        elif isinstance(shape, BezierSpline):
            if len(shape.points) >= 2:
                t_values = [i / 100 for i in range(101)]
                polyline_points = []
                for t in t_values:
                    point = shape.bezier_point(t)
                    polyline_points.append((point.x(), point.y()))
                msp.add_polyline(polyline_points, dxfattribs=dxfattribs)

        elif isinstance(shape, SegmentSpline):
            spline_points = shape.generate_spline_points()
            if spline_points:
                points = [(point.x(), point.y()) for point in spline_points]
                msp.add_polyline(points, dxfattribs=dxfattribs)

    doc.saveas(filename)
    return True


def save_to_dxf_advanced(shapes, filename):
    doc = ezdxf.new("R2000")
    doc.header["$LWDISPLAY"] = 1
    msp = doc.modelspace()

    ensure_line_types_exist(doc)

    for shape in shapes:
        dxfattribs = get_dxf_attributes_advanced(shape)

        if isinstance(shape, Line):
            msp.add_line(
                (shape.start_point.x(), shape.start_point.y()),
                (shape.end_point.x(), shape.end_point.y()),
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, Circle):
            msp.add_circle(
                (shape.center.x(), shape.center.y()),
                shape.radius,
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, CircleByThreePoints):
            center, radius = shape.calculate_circle()
            if center and radius:
                msp.add_circle((center.x(), center.y()), radius, dxfattribs=dxfattribs)

        elif isinstance(shape, ArcByThreePoints):
            center, radius, start_angle, span_angle = shape.calculate_arc()
            if center and radius:
                start_angle_deg = start_angle % 360
                span_angle = (
                    span_angle % 360 if span_angle >= 0 else (span_angle % 360) + 360
                )
                end_angle_deg = (start_angle_deg + span_angle) % 360
                if end_angle_deg < start_angle_deg:
                    end_angle_deg += 360
                msp.add_arc(
                    (center.x(), center.y()),
                    radius,
                    start_angle_deg,
                    end_angle_deg,
                    dxfattribs=dxfattribs,
                )

        elif isinstance(shape, ArcByRadiusChord):
            radius, start_angle, span_angle = shape.calculate_arc()
            start_angle_deg = start_angle % 360
            span_angle = (
                span_angle % 360 if span_angle >= 0 else (span_angle % 360) + 360
            )
            end_angle_deg = (start_angle_deg + span_angle) % 360
            if end_angle_deg < start_angle_deg:
                end_angle_deg += 360
            msp.add_arc(
                (shape.center.x(), shape.center.y()),
                radius,
                start_angle_deg,
                end_angle_deg,
                dxfattribs=dxfattribs,
            )

        elif isinstance(shape, Rectangle):
            rect = shape.rect
            points = [
                (rect.topLeft().x(), rect.topLeft().y()),
                (rect.topRight().x(), rect.topRight().y()),
                (rect.bottomRight().x(), rect.bottomRight().y()),
                (rect.bottomLeft().x(), rect.bottomLeft().y()),
                (rect.topLeft().x(), rect.topLeft().y()),
            ]
            msp.add_lwpolyline(points, dxfattribs=dxfattribs)

        elif isinstance(shape, Polygon):
            points = [(point.x(), point.y()) for point in shape.points]
            if points:
                if len(points) > 1 and points[0] != points[-1]:
                    points.append(points[0])
                msp.add_lwpolyline(points, dxfattribs=dxfattribs)

        elif isinstance(shape, BezierSpline):
            if len(shape.points) >= 2:
                control_points = [(p.x(), p.y(), 0) for p in shape.points]
                msp.add_spline(control_points, dxfattribs=dxfattribs)

        elif isinstance(shape, SegmentSpline):
            spline_points = shape.generate_spline_points()
            if spline_points:
                points = [(point.x(), point.y()) for point in spline_points]
                msp.add_lwpolyline(points, dxfattribs=dxfattribs)

    doc.saveas(filename)
    return True


def ensure_line_types_exist(doc):
    linetypes = doc.linetypes
    if "DASHED" not in linetypes:
        linetypes.add("DASHED", pattern=[10.0, -5.0])
    if "DASHDOT" not in linetypes:
        linetypes.add("DASHDOT", pattern=[10.0, -3.0, 0.0, -3.0])
    if "DASHDOT2" not in linetypes:
        linetypes.add("DASHDOT2", pattern=[10.0, -3.0, 0.0, -3.0, 0.0, -3.0])


def get_dxf_attributes(shape):
    attributes = {}
    if hasattr(shape, "color"):
        color_index = convert_qcolor_to_aci(shape.color)
        if color_index is not None:
            attributes["color"] = color_index
    if hasattr(shape, "line_type"):
        line_type = shape.line_type
        if line_type == "solid":
            attributes["linetype"] = "CONTINUOUS"
        elif line_type == "dash":
            attributes["linetype"] = "DASHED"
        elif line_type == "dash_dot":
            attributes["linetype"] = "DASHDOT"
        elif line_type == "dash_dot_dot":
            attributes["linetype"] = "DASHDOT2"
    return attributes


def get_dxf_attributes_advanced(shape):
    attributes = {"layer": "0"}
    if hasattr(shape, "color"):
        color_index = convert_qcolor_to_aci(shape.color)
        if color_index is not None:
            attributes["color"] = color_index
    if hasattr(shape, "line_type"):
        line_type = shape.line_type
        if line_type == "solid":
            attributes["linetype"] = "CONTINUOUS"
        elif line_type == "dash":
            attributes["linetype"] = "DASHED"
        elif line_type == "dash_dot":
            attributes["linetype"] = "DASHDOT"
        elif line_type == "dash_dot_dot":
            attributes["linetype"] = "DASHDOT2"
    if hasattr(shape, "line_thickness") and shape.line_thickness > 0:
        thickness_mm = shape.line_thickness
        std_thicknesses = [
            0,
            5,
            9,
            13,
            15,
            18,
            20,
            25,
            30,
            35,
            40,
            50,
            53,
            60,
            70,
            80,
            90,
            100,
            106,
            120,
            140,
            158,
            200,
            211,
        ]
        thickness_100mm = int(thickness_mm * 100)
        closest_std = min(std_thicknesses, key=lambda x: abs(x - thickness_100mm))
        attributes["lineweight"] = closest_std
    return attributes


def convert_qcolor_to_aci(qcolor):
    if qcolor is None:
        return 256
    r, g, b = qcolor.red(), qcolor.green(), qcolor.blue()
    standard_colors = {
        (0, 0, 0): 0,
        (255, 0, 0): 1,
        (255, 255, 0): 2,
        (0, 255, 0): 3,
        (0, 255, 255): 4,
        (0, 0, 255): 5,
        (255, 0, 255): 6,
        (255, 255, 255): 7,
        (128, 128, 128): 8,
        (192, 192, 192): 9,
    }
    if (r, g, b) in standard_colors:
        return standard_colors[(r, g, b)]
    min_distance = float("inf")
    closest_index = 7
    for (sr, sg, sb), index in standard_colors.items():
        distance = math.sqrt((r - sr) ** 2 + (g - sg) ** 2 + (b - sb) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_index = index
    return closest_index


def convert_aci_to_qcolor(aci):
    basic_aci_to_rgb = {
        0: (0, 0, 0),
        1: (255, 0, 0),
        2: (255, 255, 0),
        3: (0, 255, 0),
        4: (0, 255, 255),
        5: (0, 0, 255),
        6: (255, 0, 255),
        7: (255, 255, 255),
        8: (128, 128, 128),
        9: (192, 192, 192),
    }
    r, g, b = basic_aci_to_rgb.get(aci, (0, 0, 0))
    return QColor(r, g, b)


def read_from_dxf(filename, DrawingArea):
    try:
        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()
        entities = list(msp)

        flatten_z_coordinates(entities)
        normalize_dxf_entities(entities)

        scale_factor = calculate_dynamic_scale_factor(entities, target_size=1000)
        scale_dxf_entities(entities, scale_factor)

        loaded_shapes = []
        for entity in entities:
            shape = convert_dxf_to_shape(entity, DrawingArea)
            if shape:
                loaded_shapes.append(shape)
        return loaded_shapes
    except ezdxf.DXFError as e:
        print(f"DXF Error: {str(e)}")
        return []
    except Exception as e:
        print(f"Error reading DXF file: {str(e)}")
        return []


def calculate_dynamic_scale_factor(entities, target_size):
    """Calculate a scaling factor to fit the design within the target size."""
    min_x = min(
        entity.dxf.start[0] for entity in entities if hasattr(entity.dxf, "start")
    )
    min_y = min(
        entity.dxf.start[1] for entity in entities if hasattr(entity.dxf, "start")
    )
    max_x = max(entity.dxf.end[0] for entity in entities if hasattr(entity.dxf, "end"))
    max_y = max(entity.dxf.end[1] for entity in entities if hasattr(entity.dxf, "end"))

    width = max_x - min_x
    height = max_y - min_y
    max_dimension = max(width, height)

    if max_dimension == 0:
        return 1

    return target_size / max_dimension


def flatten_z_coordinates(entities):
    """Set all Z-coordinates to 0.0."""
    for entity in entities:
        if hasattr(entity.dxf, "start"):
            entity.dxf.start = (entity.dxf.start[0], entity.dxf.start[1], 0.0)
        if hasattr(entity.dxf, "end"):
            entity.dxf.end = (entity.dxf.end[0], entity.dxf.end[1], 0.0)


def normalize_dxf_entities(entities):
    """Center the design around the origin (0, 0)."""
    min_x = min(
        entity.dxf.start[0] for entity in entities if hasattr(entity.dxf, "start")
    )
    min_y = min(
        entity.dxf.start[1] for entity in entities if hasattr(entity.dxf, "start")
    )
    max_x = max(entity.dxf.end[0] for entity in entities if hasattr(entity.dxf, "end"))
    max_y = max(entity.dxf.end[1] for entity in entities if hasattr(entity.dxf, "end"))

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    for entity in entities:
        if hasattr(entity.dxf, "start"):
            entity.dxf.start = (
                entity.dxf.start[0] - center_x,
                entity.dxf.start[1] - center_y,
                entity.dxf.start[2],
            )
        if hasattr(entity.dxf, "end"):
            entity.dxf.end = (
                entity.dxf.end[0] - center_x,
                entity.dxf.end[1] - center_y,
                entity.dxf.end[2],
            )


def scale_dxf_entities(entities, scale_factor):
    """Scale the coordinates by a given factor."""
    for entity in entities:
        if hasattr(entity.dxf, "start"):
            entity.dxf.start = (
                entity.dxf.start[0] * scale_factor,
                entity.dxf.start[1] * scale_factor,
                entity.dxf.start[2],
            )
        if hasattr(entity.dxf, "end"):
            entity.dxf.end = (
                entity.dxf.end[0] * scale_factor,
                entity.dxf.end[1] * scale_factor,
                entity.dxf.end[2],
            )


def convert_dxf_to_shape(entity, DrawingArea):
    shape_attributes = extract_dxf_attributes(entity, DrawingArea)

    if entity.dxftype() == "LINE":
        start_point = QPointF(entity.dxf.start[0], entity.dxf.start[1])
        end_point = QPointF(entity.dxf.end[0], entity.dxf.end[1])
        return Line(
            start_point,
            end_point,
            shape_attributes["line_type"],
            shape_attributes["line_thickness"],
            dash_parameters=DrawingArea.dash_parameters,
            dash_auto_mode=DrawingArea.dash_auto_mode,
            color=shape_attributes["color"],
        )

    elif entity.dxftype() == "CIRCLE":
        center = QPointF(entity.dxf.center[0], entity.dxf.center[1])
        radius = entity.dxf.radius
        return Circle(
            center,
            radius,
            shape_attributes["line_type"],
            shape_attributes["line_thickness"],
            dash_parameters=DrawingArea.dash_parameters,
            dash_auto_mode=DrawingArea.dash_auto_mode,
            color=shape_attributes["color"],
        )

    elif entity.dxftype() == "ARC":
        center = QPointF(entity.dxf.center[0], entity.dxf.center[1])
        radius = entity.dxf.radius
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        radius_point = QPointF(
            center.x() + radius * math.cos(start_rad),
            center.y() + radius * math.sin(start_rad),
        )
        chord_point = QPointF(
            center.x() + radius * math.cos(end_rad),
            center.y() + radius * math.sin(end_rad),
        )
        return ArcByRadiusChord(
            center,
            radius_point,
            chord_point,
            shape_attributes["line_type"],
            shape_attributes["line_thickness"],
            dash_parameters=DrawingArea.dash_parameters,
            dash_auto_mode=DrawingArea.dash_auto_mode,
            color=shape_attributes["color"],
        )

    elif entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
        points = []
        if entity.dxftype() == "LWPOLYLINE":
            points = [QPointF(v[0], v[1]) for v in entity.vertices()]
        else:
            points = [
                QPointF(v.dxf.location[0], v.dxf.location[1]) for v in entity.vertices
            ]
        if len(points) < 2:
            return None
        closed = entity.is_closed if entity.dxftype() == "POLYLINE" else entity.closed
        if closed and len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]
        if len(points) == 4 and is_rectangle(points):
            min_x = min(p.x() for p in points)
            min_y = min(p.y() for p in points)
            max_x = max(p.x() for p in points)
            max_y = max(p.y() for p in points)
            rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
            return Rectangle(
                rect,
                shape_attributes["line_type"],
                shape_attributes["line_thickness"],
                dash_parameters=DrawingArea.dash_parameters,
                dash_auto_mode=DrawingArea.dash_auto_mode,
                color=shape_attributes["color"],
            )
        return Polygon(
            points,
            shape_attributes["line_type"],
            shape_attributes["line_thickness"],
            dash_parameters=DrawingArea.dash_parameters,
            dash_auto_mode=DrawingArea.dash_auto_mode,
            color=shape_attributes["color"],
        )

    elif entity.dxftype() == "SPLINE":
        control_points = [QPointF(p[0], p[1]) for p in entity.control_points]
        return BezierSpline(
            control_points,
            shape_attributes["line_type"],
            shape_attributes["line_thickness"],
            dash_parameters=DrawingArea.dash_parameters,
            dash_auto_mode=DrawingArea.dash_auto_mode,
            color=shape_attributes["color"],
        )
    return None


def is_rectangle(points, tolerance=1e-6):
    if len(points) != 4:
        return False
    for i in range(4):
        p1 = points[i]
        p2 = points[(i + 1) % 4]
        p3 = points[(i + 2) % 4]
        v1 = (p2.x() - p1.x(), p2.y() - p1.y())
        v2 = (p3.x() - p2.x(), p3.y() - p2.y())
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        if abs(dot_product) > tolerance:
            return False
    return True


def extract_dxf_attributes(entity, DrawingArea):
    attributes = {
        "line_type": "solid",
        "line_thickness": DrawingArea.lineThickness,
        "color": DrawingArea.currentColor,
    }
    if hasattr(entity.dxf, "lineweight") and entity.dxf.lineweight > 0:
        attributes["line_thickness"] = entity.dxf.lineweight / 100.0
    elif hasattr(entity.dxf, "thickness") and entity.dxf.thickness > 0:
        attributes["line_thickness"] = entity.dxf.thickness
    if hasattr(entity.dxf, "color") and entity.dxf.color != 256:
        attributes["color"] = convert_aci_to_qcolor(entity.dxf.color)
    if hasattr(entity.dxf, "linetype"):
        linetype = entity.dxf.linetype
        if linetype == "CONTINUOUS":
            attributes["line_type"] = "solid"
        elif linetype == "DASHED":
            attributes["line_type"] = "dash"
        elif linetype == "DASHDOT":
            attributes["line_type"] = "dash_dot"
        elif linetype in ["DASHDOT2", "DIVIDE"]:
            attributes["line_type"] = "dash_dot_dot"
    return attributes
