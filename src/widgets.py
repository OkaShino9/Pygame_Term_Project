# -*- coding: utf-8 -*-
import pygame
from ui import draw_input_box

class TextField:
    def __init__(self, rect, font, placeholder="", maxlen=16):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.maxlen = maxlen
        self.font = font

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                ch = event.unicode
                if ch and len(self.text) < self.maxlen:
                    self.text += ch

    def draw(self, screen):
        draw_input_box(screen, self.rect, self.text, self.font, active=self.active, placeholder=self.placeholder)
