# -*- coding: utf-8 -*-
# pygame.event
# pygame
# pygame.display
# pygame.time
# pygame.draw
# pygame.init
# pygame.quit
# pygame.mouse
# pygame.surface
# pygame.Rect
# pygame.image
# pygame.font
# pygame.transform
# pygame.mixer
# pygame.mixer.music

import pygame
from pygame import Rect, display, draw, event, font, image
from pygame import init as _init
from pygame import mixer, mouse
from pygame import quit as _quit
from pygame import surface, time, transform
from pygame.mixer import music


def init():
    return _init()


def quit():
    return _quit()


def set_display(size, flags=0):
    return display.set_mode(size, flags)


def update_screen():
    return display.flip()


def events():
    return event.get()


def draw_rect(surface_, color, rect, width=0):
    return draw.rect(surface_, color, rect, width=0)


def fill(surface, color):
    surface.fill(color)


__all__ = [
    "pygame",
    "event",
    "display",
    "time",
    "draw",
    "init",
    "quit",
    "mouse",
    "surface",
    "Rect",
    "image",
    "font",
    "transform",
    "mixer",
    "music",
    "set_display",
    "update_screen",
    "events",
    "fill",
    "draw_rect",
]
