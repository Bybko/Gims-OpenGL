from random import randint
from math import floor, ceil
import pygame
from pygame.locals import *
from OpenGL.GL import *
from shaders_work import initialize, render_text, _get_rendering_buffer, FONTS, CHARACTERS_TEXTURES


class NumberSurface:
    number: int
    x: int
    y: int
    width: int
    height: int
    scale: float
    font: int
    color: tuple[int, ...]

    def __init__(self, number: int, x: int, y: int, scale: float = 1, font: int = 0) -> None:
        self.number = number
        self.x = x
        self.y = y
        self.scale = scale
        self.font = font
        self.color = (0, 0, 0)
        self.width, self.height = self.__calculate_size()

    def draw(self) -> None:
        render_text(str(self.number), self.x, self.y, self.scale, self.font, self.color)

    def check_overlap(self, other) -> bool:
        return not ((self.y - self.height) > other.y or self.y < (other.y - other.height) or
                    (self.x + self.width) < other.x or self.x > (other.x + other.width))

    def check_click(self, mouse_x: int, mouse_y: int) -> bool:
        return self.x < mouse_x < self.x + self.width and self.y > mouse_y > self.y - self.height

    def __calculate_size(self) -> tuple[int, int]:
        x = self.x
        for ch in str(self.number)[:-1]:
            x += (CHARACTERS_TEXTURES[self.font][ch].advance >> 6) * self.scale
        w, h = CHARACTERS_TEXTURES[self.font][str(self.number)[-1]].textureSize
        w, h = w * self.scale, h * self.scale
        end_character_data = _get_rendering_buffer(x, self.y, w, h)
        end_pos = ceil(end_character_data[20]), floor(end_character_data[21])
        return int(end_pos[0] - self.x), int(self.y - end_pos[1])

    def __repr__(self) -> str:
        return f'Number({self.number}, {self.x} - {self.x + self.width}, {self.y - self.height} - {self.y}, {self.scale})'


def game_end(score: int) -> None:
    print(int(score))
    pygame.quit()
    quit()


def main():
    score = 0
    window = (1920, 1080)
    pygame.init()
    pygame.display.set_mode(window, DOUBLEBUF | OPENGL)

    initialize(window)

    numbers: list[NumberSurface] = []
    for i in range(1, 101):
        is_overlapping = True
        while is_overlapping:
            is_overlapping = False
            scale = randint(5, 30) / 10
            font = randint(0, len(FONTS) - 1)
            number = NumberSurface(i, randint(0, window[0] - int(70 * scale)),
                                   randint(int(40 * scale), window[1]), scale, font)
            for n in numbers:
                if n.check_overlap(number):
                    is_overlapping = True
                    break
        numbers.append(number)

    numbers_removed = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_end(score)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(len(numbers)):
                        if numbers[i].check_click(*pygame.mouse.get_pos()):
                            if numbers[i].number == numbers_removed + 1:
                                del numbers[i]
                                numbers_removed += 1
                                score += 1000
                                if numbers_removed == 100:
                                    game_end(score)
                            else:
                                score -= 200
                            break

        glClearColor(255, 255, 255, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for number in numbers:
            number.draw()
        pygame.display.flip()


if __name__ == '__main__':
    main()
