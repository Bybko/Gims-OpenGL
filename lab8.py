import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *

height = 1
num_slices = 20
bottom_points = []
top_points = []

rotate_x = 0
rotate_y = 0
rotate_z = 0.0

draw_edges = False
draw_points = False
fill_polygons = False
interpolate_colors = True

color_top = [0.0, 0.0, 0.0]
color_bot = [0.0, 0.0, 0.0]
color_model = [(0.0, 0.0, 0.0)]


def figure_model():
    global bottom_points, top_points

    for i in range(num_slices + 1):
        theta = (math.pi * (i - num_slices / 2) / 2) / num_slices

        # за основу взята параметрическая формула гиперболического цилиндра, где а = 1 и b = 1
        # 0.5 и -0.5 это максимум и минимум по высоте
        x_bottom = 1 * math.cosh(theta) - 1.2
        z_bottom = 1 * math.sinh(theta)
        bottom_points.append((x_bottom, -0.5, z_bottom))

        x_top = 1 * math.cosh(theta) - 1.2
        z_top = 1 * math.sinh(theta)
        top_points.append((x_top, 0.5, z_top))


def colors_making():
    global color_model, color_top, color_bot
    color_model = []
    for i in range(num_slices + 1):
        if not fill_polygons:
            color_model.append((0.9, 0.3, 0.0))
        else:
            color_model.append((random.random(), random.random(), random.random()))

    if not fill_polygons:
        color_top = [0.7, 0.5, 0.1]
        color_bot = [0.5, 0.5, 0.1]
    else:
        color_top = [random.random(), random.random(), random.random()]
        color_bot = [random.random(), random.random(), random.random()]


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # очищаем экран на каждом кадре

    glEnable(GL_DEPTH_TEST)  # включает проверку глубины (чтобы ближайший объект закрывал дальний при конфликте в 3д)
    glPushMatrix()  # сохраняет текущую матрицу в стеке матриц

    # вращение по осям
    glRotatef(rotate_x, 1.0, 0.0, 0.0)
    glRotatef(rotate_y, 0.0, 1.0, 0.0)
    glRotatef(rotate_z, 0.0, 0.0, 1.0)

    # в зависимости от режима будет разное закрашивание
    if not interpolate_colors:
        glShadeModel(GL_FLAT)
    else:
        glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING)  # включает освещение
    glEnable(GL_LIGHT0)  # включает первый источник света
    glEnable(GL_COLOR_MATERIAL)  # объект использует текущий цвет как свой материал, для корректного освещения

    light_position = [1, 1, 1, 0.0]  # позиция источника света
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)  # установка позиции источника света
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_position)  # диффузный свет
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_position)  # фоновый свет

    glPointSize(3)

    # включает разные режимы отображения в зависимости от выбора
    if draw_edges:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    elif draw_points:
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # отрисовка фигуры
    glBegin(GL_QUAD_STRIP)
    for i in range(num_slices + 1):
        glColor3f(color_model[i][0], color_model[i][1], color_model[i][2])
        glVertex3fv(bottom_points[i])
        glVertex3fv(top_points[i])
    glEnd()

    # отрисовка верхней крышки
    glBegin(GL_POLYGON)
    glColor3f(color_top[0], color_top[1], color_top[2])
    for point in bottom_points:
        glVertex3fv(point)
    glEnd()

    # отрисовка нижней крышки
    glBegin(GL_POLYGON)
    glColor3f(color_bot[0], color_bot[1], color_bot[2])
    for point in top_points:
        glVertex3fv(point)
    glEnd()

    pygame.display.flip()  # обновляет кадр

    # всё выключается и восстанавливает матрицу из стека (удаляя её из верха, куда мы её запихнули в начале через push)
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_COLOR_MATERIAL)

    glPopMatrix()


def event_handler(key):
    global draw_edges, draw_points, interpolate_colors, fill_polygons
    global rotate_x, rotate_y, rotate_z

    if key == K_1:
        draw_edges = not draw_edges
    elif key == K_2:
        draw_points = not draw_points
    elif key == K_3:
        interpolate_colors = not interpolate_colors
        fill_polygons = not interpolate_colors
        colors_making()
    elif key == K_4:
        if interpolate_colors and not fill_polygons:
            fill_polygons = True
        elif interpolate_colors and fill_polygons:
            fill_polygons = False
        colors_making()
    elif key == K_w:
        rotate_x += 5.0
    elif key == K_s:
        rotate_x -= 5.0
    elif key == K_a:
        rotate_y += 5.0
    elif key == K_d:
        rotate_y -= 5.0
    elif key == K_q:
        rotate_z += 5.0
    elif key == K_e:
        rotate_z -= 5.0
    elif key == K_c:
        rotate_x = rotate_y = rotate_z = 0.0


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    figure_model()
    colors_making()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                event_handler(event.key)
        draw()


if __name__ == "__main__":
    main()
