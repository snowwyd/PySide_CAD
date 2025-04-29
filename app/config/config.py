COORD_SYSTEMS = {
    "cartesian": "Декартова",
    "polar": "Полярная",
}

LINE_TYPES = {
    "solid": "Сплошная линия",
    "dash": "Штриховая линия",
    "dash_dot": "Штрихпунктирная",
    "dash_dot_dot": "Штрихпунктирная с двумя точками",
}
DRAWING_MODES = {
    "line": "Линия",
    "circle_center_radius": "Окружность по центру и радиусу",
    "circle_three_points": "Окружность по трём точкам",
    "arc_three_points": "Дуга по трём точкам",
    "arc_radius_chord": "Дуга по радиусу и хорде",
    "polygon": "Многоугольник по точкам",
    "polygon_inscribed": "Вписанный многоугольник",
    "polygon_circumscribed": "Описанный многоугольник",
    "rectangle_sides": "Прямоугольник по сторонам",
    "rectangle_center": "Прямоугольник от центра",
    "spline_bezier": "Сплайн Безье",
    "spline_segments": "Сплайн по отрезкам",
}

GROUPED_DRAWING_MODES = {
    "Дуга": ["arc_three_points", "arc_radius_chord"],
    "Окружность": ["circle_center_radius", "circle_three_points"],
    "Прямоугольник": ["rectangle_sides", "rectangle_center"],
    "Многоугольник": ["polygon", "polygon_inscribed", "polygon_circumscribed"],
    "Сплайн": ["spline_bezier", "spline_segments"],
}

GROUP_ORDER = [
    "Линия",
    "Сплайн",
    "Прямоугольник",
    "Многоугольник",
    "Окружность",
    "Дуга",
]

DASH_PARAMETERS = {
    "dash_length": 5,
    "dash_gap": 5,
    "dash_space": 3,
    "dot_length": 1,
    "dot_space": 2,
}

STANDART_COLORS = {
    "Черный": (0, 0, 0),
    "Красный": (255, 0, 0),
    "Желтый": (255, 255, 0),
    "Зеленый": (0, 255, 0),
    "Голубой": (0, 255, 255),
    "Синий": (0, 0, 255),
    "Фиолетовый": (255, 0, 255),
    "Белый": (255, 255, 255),
    "Серый": (128, 128, 128),
    "Светло-серый": (192, 192, 192),
}

STANDART_THICKNESSES = [
    0.01,
    0.05,
    0.09,
    0.13,
    0.15,
    0.18,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.50,
    0.70,
    1.00,
]

GRID_SIZE = 50
GRID_RANGE = [1, 1000]
SNAP_GRID = False

SCALE_STEP = 0.01
SCALE_LIMITS = [0.001, 3000]
CANVAS_LIMIT = 10000
BACKGROUND_IMAGE = "resources/themes/bg.jpg"
TOOLBAR_HEIGHT = 150

PRIMARY_COLOR = "#ffde8c"
ON_PRIMARY_COLOR = "#000000"
