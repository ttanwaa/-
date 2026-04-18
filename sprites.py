"""Procedural pixel-art sprite generator for Sector 7 - Demon Contra."""
import pygame, math, os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

def _try_load(filename, w, h):
    path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (w, h))
        except Exception:
            pass
    return None

# ─── Player ───
def create_player(w=48, h=56):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Helmet
    pygame.draw.rect(s, (50,60,90), (16,0,16,12))
    pygame.draw.rect(s, (70,80,120), (18,2,12,8))
    pygame.draw.rect(s, (150,220,255), (22,4,8,4))  # Visor
    pygame.draw.rect(s, (220,180,140), (20,8,10,6))  # Face
    # Body armor
    pygame.draw.rect(s, (40,50,80), (12,14,24,16))
    pygame.draw.rect(s, (60,75,110), (16,16,16,12))
    pygame.draw.rect(s, (120,100,60), (14,28,20,3))  # Belt
    # Arms
    pygame.draw.rect(s, (40,50,80), (6,16,8,10))
    pygame.draw.rect(s, (220,180,140), (8,26,6,4))
    pygame.draw.rect(s, (40,50,80), (34,16,8,10))
    pygame.draw.rect(s, (220,180,140), (36,26,6,4))
    # Gun
    pygame.draw.rect(s, (100,100,110), (40,20,8,4))
    pygame.draw.rect(s, (140,140,150), (42,18,4,8))
    pygame.draw.rect(s, (255,200,50), (48,21,2,2))  # Muzzle flash
    # Legs & Boots
    pygame.draw.rect(s, (50,45,35), (14,31,8,14))
    pygame.draw.rect(s, (50,45,35), (26,31,8,14))
    pygame.draw.rect(s, (35,35,45), (12,45,10,11))
    pygame.draw.rect(s, (35,35,45), (26,45,10,11))
    pygame.draw.rect(s, (50,50,60), (12,48,12,4))
    pygame.draw.rect(s, (50,50,60), (26,48,12,4))
    return s

# ─── Hell-Hound (Melee Demon) ───
def create_hellhound(w=44, h=36):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Body (dog-like)
    pygame.draw.ellipse(s, (80,30,30), (8,8,28,18))
    pygame.draw.ellipse(s, (100,40,35), (10,10,24,14))
    # Head
    pygame.draw.ellipse(s, (90,35,30), (0,4,16,14))
    # Eyes (glowing red)
    pygame.draw.rect(s, (255,50,20), (3,8,4,3))
    pygame.draw.rect(s, (255,200,50), (4,9,2,1))
    # Mouth/fangs
    pygame.draw.rect(s, (40,10,10), (1,14,10,3))
    pygame.draw.rect(s, (255,255,220), (2,14,2,3))
    pygame.draw.rect(s, (255,255,220), (7,14,2,3))
    # Horns
    pygame.draw.polygon(s, (60,20,15), [(4,6),(6,0),(8,6)])
    pygame.draw.polygon(s, (60,20,15), [(10,6),(12,1),(14,6)])
    # Legs (4 legs, dog-like)
    pygame.draw.rect(s, (70,25,25), (10,24,5,10))
    pygame.draw.rect(s, (70,25,25), (18,24,5,10))
    pygame.draw.rect(s, (70,25,25), (26,24,5,10))
    pygame.draw.rect(s, (70,25,25), (33,24,5,10))
    # Claws
    pygame.draw.rect(s, (50,15,15), (9,32,7,4))
    pygame.draw.rect(s, (50,15,15), (17,32,7,4))
    pygame.draw.rect(s, (50,15,15), (25,32,7,4))
    pygame.draw.rect(s, (50,15,15), (32,32,7,4))
    # Tail
    pygame.draw.polygon(s, (80,30,30), [(36,10),(44,4),(42,12)])
    return s

# ─── Gazer (Ranged Demon) ───
def create_gazer(w=36, h=40):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Main eye body (large sphere)
    pygame.draw.ellipse(s, (100,40,80), (2,4,32,28))
    pygame.draw.ellipse(s, (120,50,100), (5,7,26,22))
    # Giant eye
    pygame.draw.ellipse(s, (255,255,200), (8,10,20,16))
    pygame.draw.ellipse(s, (200,50,50), (13,13,10,10))
    pygame.draw.ellipse(s, (30,0,0), (16,15,5,6))
    pygame.draw.ellipse(s, (255,100,100), (17,16,2,2))
    # Tentacles/roots
    for i, (tx, tw) in enumerate([(4,4),(10,4),(18,4),(26,4)]):
        pygame.draw.rect(s, (80,30,70), (tx, 30, tw, 8))
        pygame.draw.rect(s, (60,20,50), (tx+1, 36, tw-2, 4))
    # Small horns/spikes
    pygame.draw.polygon(s, (140,50,90), [(8,6),(10,0),(14,6)])
    pygame.draw.polygon(s, (140,50,90), [(22,6),(26,0),(28,6)])
    # Aura glow
    glow = pygame.Surface((36,40), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255,100,50,40), (0,2,36,32))
    s.blit(glow, (0,0))
    return s

# ─── Baron Boss ───
def create_baron(w=120, h=140):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # --- Body (massive ogre) ---
    pygame.draw.rect(s, (100,60,50), (25,40,70,50))   # Torso
    pygame.draw.rect(s, (120,70,55), (30,44,60,42))    # Inner
    # Head
    pygame.draw.rect(s, (110,65,50), (35,10,50,34))
    pygame.draw.rect(s, (130,75,60), (38,14,44,28))
    # Horns (short thick)
    pygame.draw.polygon(s, (80,60,40), [(38,14),(30,0),(42,10)])
    pygame.draw.polygon(s, (80,60,40), [(82,14),(90,0),(78,10)])
    # Eyes (angry, glowing)
    pygame.draw.rect(s, (255,180,0), (42,20,14,8))
    pygame.draw.rect(s, (255,180,0), (64,20,14,8))
    pygame.draw.rect(s, (255,255,100), (45,22,8,4))
    pygame.draw.rect(s, (255,255,100), (67,22,8,4))
    # Mouth
    pygame.draw.rect(s, (60,20,15), (44,34,32,8))
    for i in range(6):
        pygame.draw.rect(s, (255,240,200), (46+i*5, 34, 3, 5))
    # Scars
    pygame.draw.line(s, (180,80,60), (36,18), (46,30), 2)
    pygame.draw.line(s, (180,80,60), (74,16), (84,28), 2)
    pygame.draw.line(s, (180,80,60), (35,50), (50,70), 2)
    pygame.draw.line(s, (180,80,60), (70,55), (90,65), 2)
    pygame.draw.line(s, (180,80,60), (40,60), (55,80), 2)
    # Chest detail / muscles
    pygame.draw.rect(s, (90,50,40), (42,48,16,10))
    pygame.draw.rect(s, (90,50,40), (62,48,16,10))
    pygame.draw.rect(s, (90,50,40), (42,60,16,8))
    pygame.draw.rect(s, (90,50,40), (62,60,16,8))
    # Arms (massive)
    pygame.draw.rect(s, (100,60,50), (5,42,22,16))
    pygame.draw.rect(s, (100,60,50), (93,42,22,16))
    pygame.draw.rect(s, (110,65,50), (2,56,18,14))
    pygame.draw.rect(s, (110,65,50), (100,56,18,14))
    # Fists
    pygame.draw.rect(s, (120,70,55), (0,68,16,12))
    pygame.draw.rect(s, (120,70,55), (104,68,16,12))
    # Hammer in right hand
    pygame.draw.rect(s, (80,70,50), (106,30,6,50))  # Handle
    pygame.draw.rect(s, (90,90,100), (98,20,22,16))  # Head
    pygame.draw.rect(s, (110,110,120), (100,22,18,12))
    # Legs
    pygame.draw.rect(s, (90,55,45), (30,90,20,30))
    pygame.draw.rect(s, (90,55,45), (70,90,20,30))
    # Feet
    pygame.draw.rect(s, (60,40,30), (26,118,26,22))
    pygame.draw.rect(s, (60,40,30), (68,118,26,22))
    return s

# ─── Projectiles & Effects ───
def create_fireball():
    frames = []
    for i in range(4):
        s = pygame.Surface((24,20), pygame.SRCALPHA)
        r = 8 + (i % 2) * 2
        pygame.draw.circle(s, (255,80,0), (12,10), r)
        pygame.draw.circle(s, (255,180,50), (12,10), r//2)
        pygame.draw.circle(s, (255,255,150), (12,10), max(2, r//3))
        frames.append(s)
    return frames

def create_bullet():
    s = pygame.Surface((14,6), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (255,255,100), (0,0,14,6))
    pygame.draw.ellipse(s, (255,255,220), (4,1,8,4))
    return s

def create_pistol_bullet():
    s = pygame.Surface((8,4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (200,200,80), (0,0,8,4))
    pygame.draw.ellipse(s, (255,255,150), (2,1,4,2))
    return s

def create_shockwave_frame():
    s = pygame.Surface((60,20), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (255,100,0,180), (0,4,60,12))
    pygame.draw.ellipse(s, (255,200,50,120), (10,6,40,8))
    return s

# ─── Items ───
def create_ammo_box():
    s = pygame.Surface((22,18), pygame.SRCALPHA)
    pygame.draw.rect(s, (60,80,50), (0,2,22,16))
    pygame.draw.rect(s, (80,110,70), (2,4,18,12))
    pygame.draw.rect(s, (255,220,50), (8,6,6,8))
    pygame.draw.rect(s, (255,255,100), (9,7,4,6))
    return s

def create_health_kit():
    s = pygame.Surface((22,20), pygame.SRCALPHA)
    pygame.draw.rect(s, (200,200,200), (0,2,22,18))
    pygame.draw.rect(s, (240,240,240), (2,4,18,14))
    pygame.draw.rect(s, (220,40,40), (8,6,6,12))
    pygame.draw.rect(s, (220,40,40), (5,9,12,6))
    return s

def create_winged_boots():
    s = pygame.Surface((24,20), pygame.SRCALPHA)
    # Boot
    pygame.draw.rect(s, (140,100,50), (4,6,14,14))
    pygame.draw.rect(s, (160,120,60), (6,8,10,10))
    pygame.draw.rect(s, (140,100,50), (14,10,8,6))
    # Wings
    pygame.draw.polygon(s, (200,220,255), [(2,6),(0,0),(8,4)])
    pygame.draw.polygon(s, (200,220,255), [(2,10),(0,4),(6,8)])
    pygame.draw.polygon(s, (220,240,255), [(3,7),(1,2),(7,5)])
    return s

def create_shield_item():
    s = pygame.Surface((20,24), pygame.SRCALPHA)
    pygame.draw.polygon(s, (50,100,200), [(10,0),(0,4),(0,14),(10,24),(20,14),(20,4)])
    pygame.draw.polygon(s, (80,140,240), [(10,3),(3,6),(3,13),(10,21),(17,13),(17,6)])
    pygame.draw.rect(s, (200,220,255), (8,6,4,12))
    pygame.draw.rect(s, (200,220,255), (4,10,12,3))
    return s

def create_spread_gun():
    s = pygame.Surface((32,16), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(s, (140,140,150), (0,4,24,8))
    pygame.draw.rect(s, (160,160,170), (2,5,20,6))
    # Barrel (wide)
    pygame.draw.polygon(s, (120,120,130), [(24,2),(32,0),(32,16),(24,14)])
    pygame.draw.polygon(s, (140,140,150), [(25,4),(30,2),(30,14),(25,12)])
    # Stock
    pygame.draw.rect(s, (100,80,50), (0,6,6,8))
    # Glow
    glow = pygame.Surface((32,16), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255,200,50,60), (20,0,12,16))
    s.blit(glow, (0,0))
    return s

# ─── Background Elements ───
def create_ruined_building(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Main structure
    pygame.draw.rect(s, (60,55,50), (0, 0, w, h))
    pygame.draw.rect(s, (70,65,58), (3, 3, w-6, h-3))
    # Broken top edge
    for i in range(0, w, 8):
        bh = (i * 7 + 13) % 15
        pygame.draw.rect(s, (0,0,0,0), (i, 0, 8, bh))
        pygame.draw.rect(s, (60,55,50), (i, bh, 8, 3))
    # Windows (some broken)
    for row in range(2, h-20, 20):
        for col in range(6, w-10, 16):
            if (row + col) % 3 == 0:
                pygame.draw.rect(s, (20,20,30), (col, row, 10, 12))
            else:
                pygame.draw.rect(s, (30,25,20), (col, row, 10, 12))
                pygame.draw.line(s, (50,45,35), (col,row), (col+10,row+12), 1)
    return s

def create_fire_particle():
    frames = []
    for i in range(6):
        s = pygame.Surface((12,16), pygame.SRCALPHA)
        h = 10 + (i % 3) * 2
        pygame.draw.ellipse(s, (255,100+i*20,0,200-i*20), (1,16-h,10,h))
        pygame.draw.ellipse(s, (255,200,50,150), (3,16-h+2,6,h-4))
        frames.append(s)
    return frames

def create_helicopter():
    s = pygame.Surface((80,40), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(s, (60,70,60), (10,14,50,22))
    pygame.draw.ellipse(s, (80,90,80), (14,16,42,18))
    # Tail
    pygame.draw.polygon(s, (50,60,50), [(55,22),(80,18),(80,26)])
    # Tail rotor
    pygame.draw.rect(s, (100,100,100), (76,14,4,16))
    # Main rotor
    pygame.draw.rect(s, (120,120,120), (0,10,70,3))
    # Cockpit
    pygame.draw.ellipse(s, (150,200,255,180), (16,18,20,12))
    # Skids
    pygame.draw.rect(s, (80,80,80), (18,34,30,2))
    return s
