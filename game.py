"""Sector 7 - Demon Contra Main Game."""
import pygame, sys, math, random
from constants import *
from entities import *
import sprites as spr

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Fonts - use Tahoma for Thai language support
_THAI_FONTS = ["Tahoma", "Leelawadee UI", "Leelawadee", "Microsoft Sans Serif", "Segoe UI"]
def _make_font(size, bold=False):
    for name in _THAI_FONTS:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except:
            pass
    return pygame.font.Font(None, size)
font_lg = _make_font(36, bold=True)
font_md = _make_font(22, bold=True)
font_sm = _make_font(16)

# Load sprites
player_img = spr.create_player()
hound_img = spr.create_hellhound()
gazer_img = spr.create_gazer()
baron_img = spr.create_baron()
bullet_img = spr.create_bullet()
pistol_img = spr.create_pistol_bullet()
fb_frames = spr.create_fireball()
sw_img = spr.create_shockwave_frame()
heli_img = spr.create_helicopter()
item_imgs = {
    "ammo": spr.create_ammo_box(), "health": spr.create_health_kit(),
    "boots": spr.create_winged_boots(), "shield": spr.create_shield_item(),
    "spread_gun": spr.create_spread_gun()
}
building_imgs = [spr.create_ruined_building(60+i*20, 80+i*30) for i in range(4)]
fire_frames = spr.create_fire_particle()

# Level 1 data
GROUND_SEGS = [(0,1200),(1250,800),(2100,900),(3050,500),(3600,1000),(4700,1300)]
PLATFORMS = [
    (350,430,100),(550,370,90),(800,410,80),(1050,360,110),
    (1350,400,80),(1500,330,100),(1800,380,90),(2150,420,80),
    (2400,350,110),(2700,400,80),(2950,340,100),(3200,400,90),
    (3650,420,80),(3900,360,110),(4200,400,80),(4500,380,100),
    (4800,430,90),(5100,370,100),(5400,410,80),
]
BG_BUILDINGS = [(i*180+50, random.randint(0,3)) for i in range(35)]
BG_FIRES = [(random.randint(100,5800), GROUND_Y-random.randint(5,15)) for _ in range(20)]

def make_enemies(is_night):
    m = NIGHT_HP_MULT if is_night else 1.0
    enemies = []
    hound_xs = [500,750,1000,1500,1900,2500,2800,3300,3700,4100,4400]
    for x in hound_xs:
        h = HellHound(x, m)
        if is_night: h.apply_night_buff()
        enemies.append(("hound", h))
    gazer_data = [(2200,350),(2650,320),(3100,300),(3500,340),(3900,310),(4300,330)]
    for gx,gy in gazer_data:
        g = Gazer(gx, gy, m)
        if is_night: g.apply_night_buff()
        enemies.append(("gazer", g))
    return enemies

def make_items():
    return [
        Item(400,400,"ammo"), Item(900,380,"ammo"), Item(1400,490,"health"),
        Item(1600,300,"boots"), Item(2300,480,"ammo"), Item(2900,310,"health"),
        Item(3400,480,"ammo"), Item(4000,340,"shield"), Item(4500,480,"ammo"),
        Item(4850,400,"health"),
    ]

def draw_sky(surf, progress, night_pct):
    day_top = (180,100,40); day_bot = (220,140,60)
    night_top = (30,5,10); night_bot = (80,15,20)
    t = night_pct
    top = tuple(int(day_top[i]*(1-t)+night_top[i]*t) for i in range(3))
    bot = tuple(int(day_bot[i]*(1-t)+night_bot[i]*t) for i in range(3))
    for y in range(GROUND_Y):
        r = y / GROUND_Y
        c = tuple(int(top[i]*(1-r)+bot[i]*r) for i in range(3))
        pygame.draw.line(surf, c, (0,y), (SW,y))

def draw_bg(surf, cam, frame, night_pct):
    draw_sky(surf, 0, night_pct)
    # Buildings parallax
    for bx, bi in BG_BUILDINGS:
        sx = bx - cam.x * 0.3
        sx = sx % (SW + 200) - 100
        img = building_imgs[bi]
        by = GROUND_Y - img.get_height()
        dark = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        dark.fill((0,0,0,int(80*night_pct)))
        dimmed = img.copy()
        dimmed.blit(dark, (0,0))
        surf.blit(dimmed, (sx, by))
    # Fires
    for fx, fy in BG_FIRES:
        sx, sy = cam.apply(fx, fy)
        if -20 < sx < SW + 20:
            fi = frame // 6 % len(fire_frames)
            surf.blit(fire_frames[fi], (sx, sy))
    # Ground
    gc = (60,50,40)
    if night_pct > 0:
        gc = tuple(max(0,int(gc[i]*(1-night_pct*0.5))) for i in range(3))
    for gx, gw in GROUND_SEGS:
        sx, _ = cam.apply(gx, GROUND_Y)
        pygame.draw.rect(surf, gc, (sx, GROUND_Y, gw, SH-GROUND_Y))
        pygame.draw.rect(surf, tuple(min(255,c+20) for c in gc), (sx, GROUND_Y, gw, 4))
    # Platforms
    for px, py, pw in PLATFORMS:
        sx, sy = cam.apply(px, py)
        if -pw-20 < sx < SW + 20:
            pygame.draw.rect(surf, (80,70,60), (sx, sy, pw, 12))
            pygame.draw.rect(surf, (100,90,75), (sx, sy, pw, 4))
    # Night overlay
    if night_pct > 0:
        ov = pygame.Surface((SW,SH), pygame.SRCALPHA)
        ov.fill((0,0,0,int(60*night_pct)))
        surf.blit(ov, (0,0))

def draw_hud(surf, player, night_pct, game_time, boss=None):
    # HP bar
    pygame.draw.rect(surf, C_HP_BG, (10,10,200,20))
    hw = int(200 * player.hp / player.max_hp)
    pygame.draw.rect(surf, C_HP_BAR, (10,10,hw,20))
    pygame.draw.rect(surf, C_WHITE, (10,10,200,20), 2)
    t = font_sm.render(f"HP {player.hp}/{player.max_hp}", True, C_WHITE)
    surf.blit(t, (15,12))
    # Ammo
    gun_name = "SPREAD GUN" if player.has_spread_gun else ("RIFLE" if player.ammo > 0 else "PISTOL")
    ac = C_AMMO if player.ammo > 0 else (180,180,180)
    t = font_md.render(f"[GUN] {gun_name}: {player.ammo}", True, ac)
    surf.blit(t, (10,36))
    # Shield
    if player.shield > 0:
        t = font_sm.render(f"<SHIELD> x{player.shield}", True, (100,180,255))
        surf.blit(t, (10,60))
    # Jump boost
    if player.jump_boost_timer > 0:
        secs = player.jump_boost_timer // 60
        t = font_sm.render(f"<BOOTS> JUMP BOOST {secs}s", True, (100,255,200))
        surf.blit(t, (10,78))
    # Time
    mins = int(game_time) // 60
    secs = int(game_time) % 60
    tcolor = (255,100,100) if night_pct > 0.5 else C_WHITE
    phase_text = "* NIGHT *" if night_pct > 0.5 else "~ DUSK ~"
    t = font_md.render(f"{phase_text}  {mins:02d}:{secs:02d}", True, tcolor)
    surf.blit(t, (SW-t.get_width()-10, 10))
    # Boss HP bar (top center)
    if boss and boss.alive:
        bx = SW//2 - 150
        pygame.draw.rect(surf, C_HP_BG, (bx,10,300,24))
        bw = int(300*boss.hp/boss.max_hp)
        bc = (200,30,30) if boss.phase == 1 else (255,50,20)
        pygame.draw.rect(surf, bc, (bx,10,bw,24))
        pygame.draw.rect(surf, C_WHITE, (bx,10,300,24), 2)
        t = font_md.render("BARON", True, C_WHITE)
        surf.blit(t, (SW//2-t.get_width()//2, 12))
        if boss.phase == 2:
            t2 = font_sm.render("!! ENRAGED !!", True, (255,80,80))
            surf.blit(t2, (SW//2-t2.get_width()//2, 36))

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = ST_INTRO
        self.frame = 0
        self.game_time = 0.0
        self.cam = Camera()
        self.player = Player(200, GROUND_Y - 100)
        self.bullets = []
        self.fireballs = []
        self.shockwaves = []
        self.particles = []
        self.enemies = make_enemies(False)
        self.items = make_items()
        self.boss = None
        self.night_pct = 0.0
        self.night_triggered = False
        self.boss_spawned = False
        self.boss_barrier_x = 0
        self.intro_timer = 0
        self.msg_text = ""
        self.msg_timer = 0
        self.clear_timer = 0
        self.heli_x = 200.0
        self.heli_y = 80.0
        self.heli_exploded = False
        self.dropped_spread = False

    def show_msg(self, text, duration=180):
        self.msg_text = text
        self.msg_timer = duration

    def spawn_drops(self, x, y, is_night):
        chance = 0.5 if is_night else 0.3
        if random.random() < chance:
            self.items.append(Item(x + random.randint(-20,20), y, "ammo"))
        if is_night and random.random() < 0.35:
            self.items.append(Item(x + random.randint(-20,20), y-10, "health"))

    def run_intro(self):
        self.intro_timer += 1
        t = self.intro_timer
        # Helicopter flies in then explodes
        if t < 60:
            self.heli_x = -80 + t * 6
            self.heli_y = 80
        elif t < 90:
            self.heli_x += 2
            self.heli_y += 1
            if t > 75 and not self.heli_exploded:
                self.heli_exploded = True
                for _ in range(30):
                    self.particles.append(Particle(self.heli_x+40,self.heli_y+20,
                        random.choice([(255,100,0),(255,200,50),(255,50,0)]),
                        random.uniform(-4,4),random.uniform(-5,1),40,random.randint(3,6)))
        elif t < 120:
            self.player.y = min(self.player.y + 4, GROUND_Y - self.player.h//2)
            self.player.vy = 0
        elif t < 240:
            pass
        else:
            self.state = ST_PLAY
            self.show_msg('Mission: Breakthrough and eliminate "BARON" the Gatekeeper', 240)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_r and (self.state == ST_OVER or self.state == ST_CLEAR):
                    self.reset()

    def update_play(self):
        keys = pygame.key.get_pressed()
        self.game_time += 1/FPS

        # Night transition
        if not self.night_triggered:
            if self.game_time >= NIGHT_TRIGGER_TIME or self.player.x >= NIGHT_TRIGGER_X:
                self.night_triggered = True
                self.show_msg("!! Nightfall !! -- Demons grow stronger!", 180)
        if self.night_triggered and self.night_pct < 1.0:
            self.night_pct = min(1.0, self.night_pct + 0.005)
            for etype, e in self.enemies:
                e.apply_night_buff()

        # Player update
        lw = self.boss_barrier_x if self.boss_spawned else 0
        self.player.update(keys, PLATFORMS, GROUND_SEGS, lw, LEVEL_WIDTH)

        # Shooting
        if keys[pygame.K_z] or keys[pygame.K_x] or keys[pygame.K_LCTRL]:
            b = self.player.shoot()
            if b:
                self.bullets.append(b)
                if self.player.has_spread_gun and not b.is_pistol:
                    self.bullets.append(Bullet(b.x, b.y-15, self.player.facing))
                    self.bullets.append(Bullet(b.x, b.y+15, self.player.facing))

        # Bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # Fireballs
        for fb in self.fireballs:
            fb.update()
            if fb.get_rect().colliderect(self.player.get_rect()):
                self.player.take_damage(GAZER_DMG)
                fb.alive = False
                for _ in range(5):
                    self.particles.append(Particle(fb.x,fb.y,(255,100,0),0,0,20,2))
        self.fireballs = [f for f in self.fireballs if f.alive]

        # Shockwaves
        for sw in self.shockwaves:
            sw.update()
            if sw.get_rect().colliderect(self.player.get_rect()):
                self.player.take_damage(BARON_SHOCKWAVE_DMG)
                sw.alive = False
        self.shockwaves = [s for s in self.shockwaves if s.alive]

        # Enemies
        for etype, e in self.enemies:
            if not e.alive:
                continue
            if etype == "hound":
                e.update(self.player.x, GROUND_SEGS, PLATFORMS)
                if e.get_rect().colliderect(self.player.get_rect()):
                    self.player.take_damage(HELLHOUND_DMG)
                    for _ in range(3):
                        self.particles.append(Particle(self.player.x,self.player.y,(255,50,50),0,0,15,2))
            elif etype == "gazer":
                e.update(self.player.x, self.frame)
                fb = e.should_shoot(self.player.x)
                if fb:
                    self.fireballs.append(fb)
            # Bullet hits
            for b in self.bullets:
                if b.alive and e.alive and b.get_rect().colliderect(e.get_rect()):
                    e.take_damage(b.damage)
                    b.alive = False
                    for _ in range(4):
                        self.particles.append(Particle(b.x,b.y,(255,200,50),0,0,15,2))
                    if not e.alive:
                        self.spawn_drops(e.x, e.y, self.night_triggered)
                        for _ in range(8):
                            self.particles.append(Particle(e.x,e.y,
                                (200,50,50),random.uniform(-3,3),random.uniform(-4,0),25,3))
        self.enemies = [(t,e) for t,e in self.enemies if e.alive]

        # Boss trigger
        if not self.boss_spawned and self.player.x >= BOSS_ARENA_X:
            self.boss_spawned = True
            self.boss_barrier_x = BOSS_ARENA_X - 50
            self.boss = Baron(BOSS_ARENA_X + 400)
            self.state = ST_BOSS_INTRO
            self.intro_timer = 0
            self.show_msg("BARON the Gatekeeper has appeared!", 150)
            self.night_pct = 1.0
            self.night_triggered = True
            return

        # Boss update
        if self.boss and self.boss.alive:
            self.boss.update(self.player.x, self.player.y)
            atk = self.boss.get_attack(self.player.get_rect())
            if atk:
                atype, data = atk
                if atype == "hammer":
                    self.player.take_damage(data)
                    for _ in range(6):
                        self.particles.append(Particle(self.player.x,self.player.y,(255,200,0),0,0,20,3))
                elif atype == "fireballs":
                    self.fireballs.extend(data)
                elif atype == "shockwave":
                    self.shockwaves.extend(data)
                    for _ in range(10):
                        self.particles.append(Particle(self.boss.x,GROUND_Y,(255,150,0),
                            random.uniform(-3,3),random.uniform(-5,-1),30,4))
            if self.boss.should_summon():
                self.enemies.append(("hound", HellHound(self.boss.x - 80, NIGHT_HP_MULT)))
                self.enemies.append(("hound", HellHound(self.boss.x + 80, NIGHT_HP_MULT)))
                self.show_msg("Baron summons Hell-Hounds!", 120)
            # Contact damage
            if self.boss.get_rect().colliderect(self.player.get_rect()):
                self.player.take_damage(10)
            # Bullets hit boss
            for b in self.bullets:
                if b.alive and self.boss.alive and b.get_rect().colliderect(self.boss.get_rect()):
                    self.boss.take_damage(b.damage)
                    b.alive = False
                    for _ in range(3):
                        self.particles.append(Particle(b.x,b.y,(255,255,100),0,0,10,2))
            if not self.boss.alive:
                # Boss death
                for _ in range(40):
                    self.particles.append(Particle(self.boss.x+random.randint(-50,50),
                        self.boss.y+random.randint(-60,30),
                        random.choice([(255,50,0),(255,100,0),(255,200,50)]),
                        random.uniform(-5,5),random.uniform(-6,1),50,random.randint(3,7)))
                if not self.dropped_spread:
                    self.dropped_spread = True
                    self.items.append(Item(self.boss.x, GROUND_Y-30, "spread_gun"))
                self.state = ST_CLEAR
                self.clear_timer = 0

        # Items
        for item in self.items:
            if not item.alive:
                continue
            item.update()
            if item.get_rect().colliderect(self.player.get_rect()):
                item.alive = False
                if item.item_type == "ammo":
                    self.player.ammo += AMMO_RESTORE
                    self.show_msg(f"+{AMMO_RESTORE} AMMO!", 60)
                elif item.item_type == "health":
                    self.player.hp = min(self.player.max_hp, self.player.hp + HEALTH_RESTORE)
                    self.show_msg(f"+{HEALTH_RESTORE} HP!", 60)
                elif item.item_type == "boots":
                    self.player.jump_boost_timer = BOOT_DURATION
                    self.show_msg("Winged Boots! Jump higher!", 90)
                elif item.item_type == "shield":
                    self.player.shield = SHIELD_HITS
                    self.show_msg("Shield! Block 1 hit!", 90)
                elif item.item_type == "spread_gun":
                    self.player.has_spread_gun = True
                    self.player.ammo += 50
                    self.show_msg("Spread Gun acquired!", 120)
                for _ in range(6):
                    self.particles.append(Particle(item.x,item.y,(255,255,100),
                        random.uniform(-2,2),random.uniform(-2,0),20,2))
        self.items = [i for i in self.items if i.alive]

        # Particles
        self.particles = [p for p in self.particles if p.update()]

        # Player death
        if not self.player.alive:
            self.state = ST_OVER

    def draw(self):
        screen.fill(C_BLACK)
        draw_bg(screen, self.cam, self.frame, self.night_pct)

        # Items
        for item in self.items:
            if item.alive:
                item.draw(screen, self.cam, item_imgs)

        # Enemies
        for etype, e in self.enemies:
            if e.alive:
                if etype == "hound":
                    e.draw(screen, self.cam, hound_img)
                elif etype == "gazer":
                    e.draw(screen, self.cam, gazer_img, self.frame)

        # Boss
        if self.boss and self.boss.alive:
            self.boss.draw(screen, self.cam, baron_img)

        # Player
        if self.player.alive:
            self.player.draw(screen, self.cam, player_img)

        # Projectiles
        for b in self.bullets:
            b.draw(screen, self.cam, bullet_img, pistol_img)
        for fb in self.fireballs:
            fb.draw(screen, self.cam, fb_frames)
        for sw in self.shockwaves:
            sw.draw(screen, self.cam, sw_img)

        # Particles
        for p in self.particles:
            p.draw(screen, self.cam)

        # Barrier visual
        if self.boss_spawned and (self.boss is None or self.boss.alive):
            bsx, _ = self.cam.apply(self.boss_barrier_x, 0)
            for yy in range(0, GROUND_Y, 4):
                a = int(120 + 40*math.sin(yy*0.1+self.frame*0.1))
                pygame.draw.rect(screen, (100,50,200,a), (bsx-2, yy, 4, 4))

        # HUD
        draw_hud(screen, self.player, self.night_pct, self.game_time, self.boss)

        # Messages
        if self.msg_timer > 0:
            self.msg_timer -= 1
            alpha = min(255, self.msg_timer * 4)
            t = font_md.render(self.msg_text, True, C_WHITE)
            ts = pygame.Surface(t.get_size(), pygame.SRCALPHA)
            ts.blit(t, (0,0))
            ts.set_alpha(alpha)
            bg = pygame.Surface((t.get_width()+20, t.get_height()+10), pygame.SRCALPHA)
            bg.fill((0,0,0,min(180,alpha)))
            screen.blit(bg, (SW//2-t.get_width()//2-10, SH//2-60))
            screen.blit(ts, (SW//2-t.get_width()//2, SH//2-55))

        # Intro overlay
        if self.state == ST_INTRO:
            if not self.heli_exploded:
                sx, sy = self.cam.apply(self.heli_x, self.heli_y)
                screen.blit(heli_img, (sx, sy))
            if self.intro_timer > 120:
                t = font_lg.render("SECTOR 7 - The Ruined Sector", True, (255,200,100))
                screen.blit(t, (SW//2-t.get_width()//2, SH//3))
                t2 = font_md.render("The Ruined Sector", True, (200,180,150))
                screen.blit(t2, (SW//2-t2.get_width()//2, SH//3+45))

        # Boss intro
        if self.state == ST_BOSS_INTRO:
            self.intro_timer += 1
            if self.intro_timer > 60:
                self.state = ST_BOSS

        # Stage clear
        if self.state == ST_CLEAR:
            self.clear_timer += 1
            if self.clear_timer > 30:
                t = font_lg.render("STAGE 1 CLEAR!", True, (255,220,50))
                screen.blit(t, (SW//2-t.get_width()//2, SH//3))
                t2 = font_md.render("Spread Gun Acquired!", True, C_WHITE)
                screen.blit(t2, (SW//2-t2.get_width()//2, SH//3+50))
                if self.clear_timer > 60:
                    t3 = font_sm.render("Press R to Restart", True, (180,180,180))
                    screen.blit(t3, (SW//2-t3.get_width()//2, SH//3+90))

        # Game over
        if self.state == ST_OVER:
            ov = pygame.Surface((SW,SH), pygame.SRCALPHA)
            ov.fill((0,0,0,150))
            screen.blit(ov, (0,0))
            t = font_lg.render("GAME OVER", True, C_RED)
            screen.blit(t, (SW//2-t.get_width()//2, SH//3))
            t2 = font_md.render("Press R to Restart", True, C_WHITE)
            screen.blit(t2, (SW//2-t2.get_width()//2, SH//3+50))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.frame += 1

            # Extra restart check via key state (fixes missed KEYDOWN)
            if self.state in (ST_OVER, ST_CLEAR):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.reset()
                    continue

            if self.state == ST_INTRO:
                self.run_intro()
            elif self.state in (ST_PLAY, ST_BOSS, ST_BOSS_INTRO):
                self.update_play()
            elif self.state == ST_CLEAR:
                self.update_play()  # keep particles updating

            self.cam.update(self.player.x, LEVEL_WIDTH)
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
