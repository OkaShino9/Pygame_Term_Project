# -*- coding: utf-8 -*-
import pygame
import config as C
import resources as R

def draw_dice(screen, face_value, rect_area):
    DICE_SIZE = 120
    dice_box = pygame.Rect(0, 0, DICE_SIZE + 16, DICE_SIZE + 16)
    dice_box.centerx = rect_area.centerx
    dice_box.y = rect_area.y
    pygame.draw.rect(screen, C.COL_CARD, dice_box, border_radius=14)
    pygame.draw.rect(screen, C.COL_BORDER, dice_box, width=1, border_radius=14)

    if face_value is None:
        t = R.font_sm().render("ยังไม่ทอย", True, C.COL_SUBT)
        screen.blit(t, (dice_box.centerx - t.get_width()//2, dice_box.centery - t.get_height()//2))
        return dice_box

    if R.DICE_IMGS:
        screen.blit(R.DICE_IMGS[face_value-1], (dice_box.x+8, dice_box.y+8))
    else:
        face = pygame.Rect(dice_box.x+8, dice_box.y+8, DICE_SIZE, DICE_SIZE)
        pygame.draw.rect(screen, (255,255,255), face, border_radius=12)
        pygame.draw.rect(screen, C.COL_BORDER, face, width=2, border_radius=12)
        cx, cy = face.center; r = 8
        spots = {
            1: [(cx, cy)],
            2: [(cx-25, cy-25), (cx+25, cy+25)],
            3: [(cx-25, cy-25), (cx, cy), (cx+25, cy+25)],
            4: [(cx-25, cy-25), (cx+25, cy-25), (cx-25, cy+25), (cx+25, cy+25)],
            5: [(cx-25, cy-25), (cx+25, cy-25), (cx, cy), (cx-25, cy+25), (cx+25, cy+25)],
            6: [(cx-25, cy-25), (cx+25, cy-25), (cx-25, cy), (cx+25, cy), (cx-25, cy+25), (cx+25, cy+25)],
        }
        for (px,py) in spots[face_value]:
            pygame.draw.circle(screen, (40,40,40), (px,py), r)
    return dice_box
