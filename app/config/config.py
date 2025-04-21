COORD_SYSTEMS = {'cartesian': 'Декартова', 'polar': 'Полярная'}
LINE_TYPES = {'solid': 'Сплошная линия', 'dash': 'Штриховая линия', 'dash_dot': 'Штрих-пунктирная', 'dash_dot_dot': 'Штрих-пунктирная с двумя точками'}
DRAWING_MODES = {
    'line': 'Линия',
    'circle_center_radius': 'По центру и радиусу',
    'circle_three_points': 'По трём точкам',
    'arc_three_points': 'По трём точкам',
    'arc_radius_chord': 'По радиусу и хорде',
    'polygon': 'По точкам',
    'polygon_inscribed': 'Вписанный',
    'polygon_circumscribed': 'Описанный',
    'rectangle_sides': 'По сторонам',
    'rectangle_center': 'От центра',
    'spline_bezier': 'Безье',
    'spline_segments': 'По отрезкам'
}

GROUPED_DRAWING_MODES = {
    "Дуга": ['arc_three_points', 'arc_radius_chord'],
    "Окружность": ['circle_center_radius', 'circle_three_points'],
    "Прямоугольник": ['rectangle_sides', 'rectangle_center'],
    "Многоугольник": ['polygon', 'polygon_inscribed', 'polygon_circumscribed'],
    "Сплайн": ['spline_bezier', 'spline_segments']
}