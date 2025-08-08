import pygame, random
pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption("Reaction Time")
font = pygame.font.SysFont(None, 36)
text = font.render("PRESS ANY KEY TO START", True, (255,255,255))
wait_text = font.render("WAIT...", True, (0,255,0))
running = True; state="start"; start_time=0; avg=0; count=0; r_surf=None
while running:
    t = pygame.time.get_ticks()
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN:
            if state=="start":
                state="wait"; start_time = t+random.randint(1000,3000)
            elif state=="wait_for_reaction":
                state="wait"; reaction=(t-start_time)/1000
                count+=1; avg=(avg*(count-1)+reaction)/count
                r_surf=font.render(f"Time: {reaction:.3f}s", True,(255,255,255))
                state="start"
    if state=="wait" and t>=start_time: state="wait_for_reaction"
    screen.fill((0,0,0))
    center = screen.get_rect().center
    if state=="start": screen.blit(text, text.get_rect(center=center))
    elif state=="wait_for_reaction": screen.blit(wait_text, wait_text.get_rect(center=center))
    if r_surf: screen.blit(r_surf, (center[0]-100,350))
    pygame.display.flip()
pygame.quit()
