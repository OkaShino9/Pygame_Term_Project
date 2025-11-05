import pygame
import sys

def curtain_transition(screen, old_surface, new_surface, curtain_image_path, duration=0.6):
    """
    ม่านรูปภาพเลื่อนลงมาปิดหน้าจอ แล้วเลื่อนขึ้นไปเปิดเผยหน้าใหม่
    
    Args:
        screen: pygame display surface
        old_surface: surface ของหน้าจอเก่า
        new_surface: surface ของหน้าจอใหม่
        curtain_image_path: path ของรูปม่าน
        duration: ระยะเวลาแต่ละ phase (ลง + ขึ้น = duration * 2)
    """
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    
    # โหลดรูปม่าน
    try:
        curtain = pygame.image.load(curtain_image_path).convert_alpha()
        curtain = pygame.transform.scale(curtain, (screen_width, screen_height))
    except:
        # ถ้าไม่มีรูป ใช้สีทึบแทน
        curtain = pygame.Surface((screen_width, screen_height))
        curtain.fill((20, 20, 40))
        print(f"[WARN] ไม่พบรูป {curtain_image_path}, ใช้สีทึบแทน")
    
    # ========== Phase 1: ม่านเลื่อนลงมา ==========
    print("[TRANSITION] Phase 1: เลื่อนลงมา...")
    elapsed = 0
    while elapsed < duration:
        dt = clock.tick(60) / 1000.0
        elapsed += dt
        
        progress = elapsed / duration
        progress = progress * progress * (3.0 - 2.0 * progress)  # smoothstep
        
        # ม่านเริ่มที่ y = -screen_height (บนสุด) เลื่อนลงมาที่ y = 0
        curtain_y = -screen_height + int(progress * screen_height)
        
        screen.blit(old_surface, (0, 0))
        screen.blit(curtain, (0, curtain_y))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    # หยุดสักครู่ที่ม่านปิดเต็มหน้าจอ
    screen.blit(old_surface, (0, 0))
    screen.blit(curtain, (0, 0))
    pygame.display.flip()
    pygame.time.wait(1000)  # หยุด 0.1 วินาที
    elapsed = 0
    while elapsed < duration:
        dt = clock.tick(60) / 1000.0
        elapsed += dt
        
        progress = elapsed / duration
        progress = progress * progress * (3.0 - 2.0 * progress)  # smoothstep
        
        # ม่านเริ่มที่ y = 0 เลื่อนขึ้นไปที่ y = screen_height (ล่างสุด)
        curtain_y = int(progress * screen_height)
        
        screen.blit(new_surface, (0, 0))
        screen.blit(curtain, (0, curtain_y))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()