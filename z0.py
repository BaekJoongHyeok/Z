import pygame
import math
import random
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Z: GHOST SECTOR")
clock = pygame.time.Clock()

RED, WHITE, YELLOW, BLACK, CYAN, GREEN = (180,0,0),(220,220,220),(255,200,0),(0,0,0),(0,255,255),(0,200,0)

def get_font(size, bold=False):
    return pygame.font.SysFont(pygame.font.get_default_font(), size, bold=bold)

font_lg, font_md, font_sm = get_font(120, True), get_font(25, True), get_font(18)

MAP = [
    [1,1,1,1,1,1,1,1],
    [1,2,0,0,0,0,2,1],
    [1,0,0,0,0,0,0,1],
    [1,2,0,0,0,0,2,1],
    [1,1,1,1,1,1,1,1]
]
TILE = 200

# --- Procedural wall textures ---
TEX_SIZE = 64

def generate_wall_texture(wall_type):
    surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    if wall_type == 1:
        surf.fill((60, 50, 45))
        for row in range(0, TEX_SIZE, 8):
            offset = 16 if (row // 8) % 2 else 0
            for col in range(0, TEX_SIZE, 16):
                r = random.randint(-10, 10)
                color = (70+r, 55+r, 48+r)
                pygame.draw.rect(surf, color, (col+offset, row, 15, 7))
                pygame.draw.rect(surf, (40,35,30), (col+offset, row, 15, 7), 1)
        for _ in range(3):
            bx, by = random.randint(0, TEX_SIZE-1), random.randint(0, TEX_SIZE-1)
            pygame.draw.circle(surf, (100, 20, 20), (bx, by), random.randint(2, 5))
    else:
        surf.fill((80, 75, 70))
        for y in range(TEX_SIZE):
            for x in range(TEX_SIZE):
                if random.random() < 0.05:
                    surf.set_at((x, y), (90+random.randint(-10,10), 85+random.randint(-10,10), 78+random.randint(-10,10)))
        for i in range(0, TEX_SIZE, 16):
            pygame.draw.line(surf, (60,55,50), (i, 0), (i, TEX_SIZE), 2)
            pygame.draw.line(surf, (60,55,50), (0, i), (TEX_SIZE, i), 2)
    return surf

wall_textures = {1: generate_wall_texture(1), 2: generate_wall_texture(2)}

class Smoke:
    def __init__(self):
        self.reset(); self.y = random.randint(0, HEIGHT)
    def reset(self):
        self.x, self.y = random.randint(0, WIDTH), HEIGHT + random.randint(10, 100)
        self.size, self.growth, self.alpha = random.randint(15, 30), random.uniform(0.3, 0.6), random.randint(70, 140)
        self.vel_y, self.vel_x = random.uniform(0.8, 2.0), random.uniform(-0.4, 0.4)
    def update(self):
        self.y -= self.vel_y; self.x += self.vel_x; self.size += self.growth; self.alpha -= 0.7
        if self.alpha <= 0: self.reset()
    def draw(self, surf):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (80, 85, 100, int(max(0, self.alpha))), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (self.x - self.size, self.y - self.size))

class Pickup:
    def __init__(self, kind):
        self.kind = kind
        self.reset()
    def reset(self):
        while True:
            self.tx, self.ty = random.randint(1, 6), random.randint(1, 3)
            if MAP[self.ty][self.tx] == 0:
                self.x, self.y = self.tx * TILE + TILE//2, self.ty * TILE + TILE//2
                break

class Ghost:
    def __init__(self):
        self.x = random.randint(400, 1000)
        self.y = random.randint(400, 800)
        self.hp, self.pulse = 2, 0
    def update(self, px, py):
        self.pulse += 0.1
        dx, dy = px - self.x, py - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 35:
            self.x += (dx/dist) * 2.2 + random.uniform(-1, 1)
            self.y += (dy/dist) * 2.2 + random.uniform(-1, 1)
        return dist

def render_minimap(surf, px, py, pa, ghosts, pickups):
    mm_size, mm_x, mm_y = 120, WIDTH - 130, 10
    mm_surf = pygame.Surface((mm_size, mm_size), pygame.SRCALPHA)
    mm_surf.fill((0, 0, 0, 160))
    rows, cols = len(MAP), len(MAP[0])
    cw, ch = mm_size / cols, mm_size / rows
    for r in range(rows):
        for c in range(cols):
            if MAP[r][c] > 0:
                color = (100, 80, 70, 200) if MAP[r][c] == 1 else (120, 100, 90, 200)
                pygame.draw.rect(mm_surf, color, (c*cw, r*ch, cw, ch))
            else:
                pygame.draw.rect(mm_surf, (20, 20, 30, 100), (c*cw, r*ch, cw, ch))
    world_w, world_h = cols * TILE, rows * TILE
    ppx = (px / world_w) * mm_size
    ppy = (py / world_h) * mm_size
    pygame.draw.circle(mm_surf, (0, 200, 255), (int(ppx), int(ppy)), 3)
    ex, ey = ppx + math.cos(pa)*8, ppy + math.sin(pa)*8
    pygame.draw.line(mm_surf, (0, 200, 255), (int(ppx), int(ppy)), (int(ex), int(ey)), 2)
    for g in ghosts:
        gx = (g.x / world_w) * mm_size
        gy = (g.y / world_h) * mm_size
        pygame.draw.circle(mm_surf, (255, 80, 80), (int(gx), int(gy)), 2)
    for p in pickups:
        pkx = (p.x / world_w) * mm_size
        pky = (p.y / world_h) * mm_size
        color = CYAN if p.kind == "ammo" else GREEN
        pygame.draw.rect(mm_surf, color, (int(pkx)-2, int(pky)-2, 4, 4))
    pygame.draw.rect(mm_surf, (100, 100, 100), (0, 0, mm_size, mm_size), 1)
    surf.blit(mm_surf, (mm_x, mm_y))

def play():
    px, py, pa, ph = 400.0, 300.0, 0.0, 0.0
    hp, ammo, stamina = 100.0, 20, 100.0
    ghosts = [Ghost() for _ in range(3)]
    pickups = [Pickup("ammo"), Pickup("health")]
    recoil, muzzle, hurt = 0, 0, 0
    spawn_btn = pygame.Rect(WIDTH//2 - 75, 20, 150, 40)

    while True:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        tab_held = keys[K_TAB]

        for e in pygame.event.get():
            if e.type == QUIT: return "quit"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if tab_held and spawn_btn.collidepoint(e.pos):
                    ghosts.append(Ghost())
                elif not tab_held and ammo > 0:
                    ammo -= 1; recoil = 25; muzzle = 5
                    for g in ghosts:
                        angle = math.atan2(g.y - py, g.x - px) - pa
                        while angle < -math.pi: angle += 2*math.pi
                        while angle > math.pi: angle -= 2*math.pi
                        if abs(angle) < 0.2: g.hp -= 1

        is_sprinting = keys[K_LSHIFT] and stamina > 0 and (keys[K_w] or keys[K_s])
        speed = 7.0 if is_sprinting else 4.0
        if is_sprinting: stamina -= 1.0
        elif stamina < 100: stamina += 0.5

        if not tab_held:
            pygame.mouse.set_visible(False); pygame.event.set_grab(True)
            pa += pygame.mouse.get_rel()[0] * 0.003
            dx, dy = 0, 0
            if keys[K_w]: dx += math.cos(pa)*speed; dy += math.sin(pa)*speed
            if keys[K_s]: dx -= math.cos(pa)*speed; dy -= math.sin(pa)*speed
            if keys[K_a]: dx += math.sin(pa)*speed; dy -= math.cos(pa)*speed
            if keys[K_d]: dx -= math.sin(pa)*speed; dy += math.cos(pa)*speed

            if MAP[int(py)//TILE][int(px+dx)//TILE] == 0: px += dx
            elif keys[K_SPACE] and ph < 100: ph += 5
            if MAP[int(py+dy)//TILE][int(px)//TILE] == 0: py += dy
            elif keys[K_SPACE] and ph < 100: ph += 5
            if not keys[K_SPACE] and ph > 0: ph -= 10
            ph = max(0, ph)
        else:
            pygame.mouse.set_visible(True); pygame.event.set_grab(False); pygame.mouse.get_rel()

        for g in ghosts: g.update(px, py)
        for p in pickups:
            if math.sqrt((px-p.x)**2 + (py-p.y)**2) < 50:
                if p.kind == "ammo": ammo += 10
                else: hp = min(100, hp + 30)
                p.reset()

        # --- Render ---
        screen.fill((5, 2, 15))
        # Sky gradient
        for y in range(HEIGHT//2):
            t = y / (HEIGHT//2)
            r = int(5 + t * 10)
            g_c = int(2 + t * 8)
            b = int(15 + t * 20)
            pygame.draw.line(screen, (r, g_c, b), (0, y), (WIDTH, y))
        # Ground
        pygame.draw.rect(screen, (15, 15, 15), (0, HEIGHT//2 + ph, WIDTH, HEIGHT//2))

        z_buf = [2000] * WIDTH
        for x in range(0, WIDTH, 4):
            ray_a = (pa - 0.6) + (x/WIDTH)*1.2
            cos_a, sin_a = math.cos(ray_a), math.sin(ray_a)
            for d in range(10, 1200, 8):
                rx, ry = px + cos_a*d, py + sin_a*d
                tx, ty = int(rx)//TILE, int(ry)//TILE
                if 0 <= ty < len(MAP) and 0 <= tx < len(MAP[0]) and MAP[ty][tx] > 0:
                    wall_type = MAP[ty][tx]
                    h = int(40000/(d+1))
                    # Texture sampling
                    hit_x = rx % TILE
                    hit_y = ry % TILE
                    tex_x = int((hit_x / TILE) * TEX_SIZE) % TEX_SIZE
                    if abs(hit_x) < 2 or abs(hit_x - TILE) < 2:
                        tex_x = int((hit_y / TILE) * TEX_SIZE) % TEX_SIZE
                    # Distance shading
                    shade = max(0.1, 1.0 - d / 1200)
                    fog_r = int(5 * (1 - shade))
                    fog_g = int(2 * (1 - shade))
                    fog_b = int(15 * (1 - shade))
                    tex = wall_textures[wall_type]
                    wall_top = HEIGHT//2 - h//2 + ph
                    for sy in range(max(0, wall_top), min(HEIGHT, wall_top + h)):
                        tex_y = int(((sy - wall_top) / h) * TEX_SIZE) % TEX_SIZE
                        tc = tex.get_at((tex_x, tex_y))
                        cr = int(tc[0] * shade) + fog_r
                        cg = int(tc[1] * shade) + fog_g
                        cb = int(tc[2] * shade) + fog_b
                        for px_off in range(4):
                            if x + px_off < WIDTH:
                                screen.set_at((x + px_off, sy), (min(255,cr), min(255,cg), min(255,cb)))
                    for i in range(4):
                        if x+i < WIDTH: z_buf[x+i] = d
                    break

        # Draw ghosts/pickups
        for obj in ghosts + pickups:
            dist = math.sqrt((px-obj.x)**2 + (py-obj.y)**2)
            angle = math.atan2(obj.y - py, obj.x - px) - pa
            while angle < -math.pi: angle += 2*math.pi
            while angle > math.pi: angle -= 2*math.pi
            if abs(angle) < 1.0 and dist > 10:
                sx = int((0.5 * (angle/0.6) + 0.5) * WIDTH)
                size = int(18000/(dist+1))
                if 0 <= sx < WIDTH and dist < z_buf[sx]:
                    y_pos = HEIGHT//2 + ph
                    if isinstance(obj, Ghost):
                        if dist < 45: hp -= 0.5; hurt = 5
                        p_val = abs(math.sin(obj.pulse)) * 50
                        glow = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                        for r in range(size, 0, -2):
                            alpha = int(80 * (r / size))
                            pygame.draw.circle(glow, (100, 180, 255, alpha), (size, size), r)
                        screen.blit(glow, (sx - size, y_pos - size))
                        pygame.draw.ellipse(screen, (int(150+p_val), 200, 255), (sx-size//2, y_pos-size//2, size, size))
                    else:
                        color = CYAN if obj.kind == "ammo" else GREEN
                        pygame.draw.rect(screen, color, (sx-size//4, y_pos+size//4, size//2, size//2))

        ghosts = [g for g in ghosts if g.hp > 0]
        if len(ghosts) < 3: ghosts.append(Ghost())

        # Gun
        gun_y = HEIGHT - 160 + recoil + ph
        pygame.draw.rect(screen, (30, 30, 30), (WIDTH//2-20, gun_y, 40, 160))
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH//2-18, gun_y+2, 36, 156))
        if muzzle > 0:
            flash = pygame.Surface((80, 80), pygame.SRCALPHA)
            for r in range(40, 0, -3):
                alpha = int(200 * (r / 40))
                pygame.draw.circle(flash, (255, 200, 50, alpha), (40, 40), r)
            screen.blit(flash, (WIDTH//2 - 40, gun_y - 50))
            muzzle -= 1
        recoil = max(0, recoil - 3)

        # HUD
        pygame.draw.rect(screen, (40, 40, 40), (18, HEIGHT-42, 204, 19))
        pygame.draw.rect(screen, RED, (20, HEIGHT-40, int(hp*2), 15))
        pygame.draw.rect(screen, (40, 40, 40), (18, HEIGHT-62, 204, 14))
        pygame.draw.rect(screen, YELLOW, (20, HEIGHT-60, int(stamina*2), 10))
        screen.blit(font_sm.render(f"HP: {int(hp)}", True, WHITE), (25, HEIGHT-40))
        screen.blit(font_sm.render(f"AMMO: {ammo}", True, WHITE), (WIDTH-120, HEIGHT-40))

        # Minimap
        render_minimap(screen, px, py, pa, ghosts, pickups)

        # Spawn button (always visible)
        spawn_color = (150, 0, 0) if tab_held else (80, 0, 0)
        pygame.draw.rect(screen, spawn_color, spawn_btn)
        pygame.draw.rect(screen, (200, 0, 0), spawn_btn, 1)
        screen.blit(font_sm.render("TAB+CLICK: SPAWN", True, WHITE), (spawn_btn.x+5, spawn_btn.y+10))

        if hurt > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((255, 0, 0, 60))
            screen.blit(s, (0, 0))
            hurt -= 1

        pygame.display.flip()
        if hp <= 0 or keys[K_ESCAPE]: return "menu"

def main_menu():
    smokes = [Smoke() for _ in range(30)]
    pygame.mouse.set_visible(True); pygame.event.set_grab(False)
    while True:
        screen.fill(BLACK)
        for s in smokes: s.update(); s.draw(screen)
        screen.blit(font_lg.render("Z", True, RED), (WIDTH//2-40, 100))
        sub = font_sm.render("GHOST SECTOR", True, (150, 150, 150))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 230))
        b_start = pygame.Rect(WIDTH//2-100, 300, 200, 50)
        pygame.draw.rect(screen, (150, 0, 0), b_start)
        pygame.draw.rect(screen, (200, 0, 0), b_start, 2)
        screen.blit(font_md.render("START", True, WHITE), (b_start.x+55, b_start.y+10))
        ctrl = font_sm.render("WASD Move | Mouse Aim | Click Shoot | SHIFT Sprint", True, (100,100,100))
        screen.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, 380))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == QUIT: return "quit"
            if e.type == MOUSEBUTTONDOWN and b_start.collidepoint(e.pos): return "play"

state = "menu"
while state != "quit":
    state = main_menu() if state == "menu" else play()
pygame.quit()
