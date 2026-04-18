"""Entity classes: Player, Bullet, Enemies, Boss, Items."""
import pygame, math, random
from constants import *

class Camera:
    def __init__(self):
        self.x = 0
        self.target_x = 0
    def update(self, player_x, level_w):
        self.target_x = player_x - SW // 3
        self.target_x = max(0, min(self.target_x, level_w - SW))
        self.x += (self.target_x - self.x) * 0.08
    def apply(self, x, y):
        return x - self.x, y

class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=30, size=3):
        self.x, self.y = x, y
        self.color = color
        self.vx = vx + random.uniform(-1, 1)
        self.vy = vy + random.uniform(-2, 0)
        self.life = life
        self.max_life = life
        self.size = size
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
        return self.life > 0
    def draw(self, surf, cam):
        alpha = int(255 * self.life / self.max_life)
        sx, sy = cam.apply(self.x, self.y)
        if -10 < sx < SW + 10:
            c = (*self.color[:3], min(255, alpha))
            ps = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(ps, c, (self.size, self.size), self.size)
            surf.blit(ps, (sx - self.size, sy - self.size))

class Bullet:
    def __init__(self, x, y, direction, is_pistol=False):
        self.x, self.y = x, y
        self.vx = BULLET_SPEED * direction
        self.is_pistol = is_pistol
        self.damage = PISTOL_DMG if is_pistol else MAIN_GUN_DMG
        self.w = 8 if is_pistol else 14
        self.h = 4 if is_pistol else 6
        self.alive = True
    def update(self):
        self.x += self.vx
        if self.x < -50 or self.x > LEVEL_WIDTH + 50:
            self.alive = False
    def draw(self, surf, cam, img, pistol_img):
        sx, sy = cam.apply(self.x, self.y)
        if -20 < sx < SW + 20:
            i = pistol_img if self.is_pistol else img
            if self.vx < 0:
                i = pygame.transform.flip(i, True, False)
            surf.blit(i, (sx - self.w//2, sy - self.h//2))
    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

class Fireball:
    def __init__(self, x, y, vx, vy=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.frame = 0
        self.alive = True
        self.w, self.h = 24, 20
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.frame = (self.frame + 1) % 16
        if self.x < -50 or self.x > LEVEL_WIDTH + 50 or self.y > SH + 50:
            self.alive = False
    def draw(self, surf, cam, frames):
        sx, sy = cam.apply(self.x, self.y)
        if -30 < sx < SW + 30:
            surf.blit(frames[self.frame // 4], (sx - 12, sy - 10))
    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 8, 20, 16)

class Shockwave:
    def __init__(self, x, y, direction):
        self.x, self.y = x, y
        self.vx = 5 * direction
        self.alive = True
        self.w, self.h = 60, 20
        self.life = 180
    def update(self):
        self.x += self.vx
        self.life -= 1
        if self.life <= 0 or self.x < -100 or self.x > LEVEL_WIDTH + 100:
            self.alive = False
    def draw(self, surf, cam, img):
        sx, sy = cam.apply(self.x, self.y)
        if -70 < sx < SW + 70:
            surf.blit(img, (sx - 30, sy - 10))
    def get_rect(self):
        return pygame.Rect(self.x - 30, self.y - 8, 60, 16)

class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 36, 52
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.ammo = PLAYER_START_AMMO
        self.facing = 1
        self.on_ground = False
        self.iframes = 0
        self.shield = 0
        self.jump_boost_timer = 0
        self.shoot_cd = 0
        self.alive = True
        self.has_spread_gun = False
    def take_damage(self, dmg):
        if self.iframes > 0:
            return False
        if self.shield > 0:
            self.shield -= 1
            self.iframes = 30
            return False
        self.hp -= dmg
        self.iframes = PLAYER_IFRAMES
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True
    def shoot(self):
        if self.shoot_cd > 0:
            return None
        is_pistol = self.ammo <= 0
        if not is_pistol:
            self.ammo -= 1
        self.shoot_cd = 8 if not is_pistol else 15
        bx = self.x + self.facing * 30
        by = self.y - 8
        return Bullet(bx, by, self.facing, is_pistol)
    def update(self, keys, platforms, ground_segments, left_wall=0, right_wall=LEVEL_WIDTH):
        # Movement
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing = 1
        # Jump
        if self.on_ground and (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]):
            jv = PLAYER_JUMP_BOOSTED if self.jump_boost_timer > 0 else PLAYER_JUMP
            self.vy = jv
            self.on_ground = False
        # Physics
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        # Clamp to walls
        self.x = max(left_wall + self.w//2, min(self.x, right_wall - self.w//2))
        # Ground collision
        self.on_ground = False
        for gx, gw in ground_segments:
            if gx <= self.x <= gx + gw and self.y + self.h//2 >= GROUND_Y and self.vy >= 0:
                self.y = GROUND_Y - self.h//2
                self.vy = 0
                self.on_ground = True
                break
        # Platform collision (one-way, only when falling)
        if self.vy >= 0 and not self.on_ground:
            for px, py, pw in platforms:
                if (px <= self.x <= px + pw and
                    self.y + self.h//2 >= py and self.y + self.h//2 - self.vy <= py + 4):
                    self.y = py - self.h//2
                    self.vy = 0
                    self.on_ground = True
                    break
        # Fall death
        if self.y > SH + 100:
            self.take_damage(50)
            if self.alive:
                self.y = GROUND_Y - self.h//2 - 100
                self.vy = 0
        # Timers
        if self.iframes > 0:
            self.iframes -= 1
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.jump_boost_timer > 0:
            self.jump_boost_timer -= 1
    def draw(self, surf, cam, img):
        if self.iframes > 0 and self.iframes % 4 < 2:
            return
        sx, sy = cam.apply(self.x, self.y)
        i = img if self.facing > 0 else pygame.transform.flip(img, True, False)
        surf.blit(i, (sx - self.w//2 - 6, sy - self.h//2 - 2))
        # Shield glow
        if self.shield > 0:
            gs = pygame.Surface((self.w+16, self.h+16), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (80,140,240,80), (0,0,self.w+16,self.h+16))
            surf.blit(gs, (sx-self.w//2-8, sy-self.h//2-8))
    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

class HellHound:
    def __init__(self, x, hp_mult=1.0):
        self.x, self.y = float(x), GROUND_Y - 18.0
        self.w, self.h = 40, 36
        self.hp = int(HELLHOUND_HP * hp_mult)
        self.max_hp = self.hp
        self.speed = HELLHOUND_SPEED
        self.direction = -1
        self.alive = True
        self.night_buffed = False
        self.patrol_min = x - 120
        self.patrol_max = x + 120
        self.hurt_flash = 0
    def apply_night_buff(self):
        if not self.night_buffed:
            self.night_buffed = True
            self.speed *= NIGHT_SPEED_MULT
            self.hp = int(self.hp * NIGHT_HP_MULT)
            self.max_hp = int(self.max_hp * NIGHT_HP_MULT)
    def take_damage(self, dmg):
        self.hp -= dmg
        self.hurt_flash = 8
        if self.hp <= 0:
            self.alive = False
    def update(self, player_x, ground_segments, platforms):
        # Chase player if close
        dist = abs(player_x - self.x)
        if dist < 300:
            self.direction = 1 if player_x > self.x else -1
        nx = self.x + self.speed * self.direction
        # Edge detection - don't fall off ground
        on_ground = False
        for gx, gw in ground_segments:
            if gx <= nx <= gx + gw:
                on_ground = True
                break
        if not on_ground:
            self.direction *= -1
        else:
            self.x = nx
        # Patrol bounds
        if self.x < self.patrol_min or self.x > self.patrol_max:
            if abs(player_x - self.x) > 300:
                self.direction *= -1
        if self.hurt_flash > 0:
            self.hurt_flash -= 1
    def draw(self, surf, cam, img):
        sx, sy = cam.apply(self.x, self.y)
        if -50 < sx < SW + 50:
            i = img if self.direction > 0 else pygame.transform.flip(img, True, False)
            if self.hurt_flash > 0:
                flash = i.copy()
                flash.fill((255,100,100), special_flags=pygame.BLEND_RGB_ADD)
                i = flash
            surf.blit(i, (sx - self.w//2, sy - self.h//2))
            # Night aura
            if self.night_buffed:
                gs = pygame.Surface((self.w+12, self.h+12), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (255,30,0,50), (0,0,self.w+12,self.h+12))
                surf.blit(gs, (sx-self.w//2-6, sy-self.h//2-6))
            # HP bar
            if self.hp < self.max_hp:
                bw = 30
                pygame.draw.rect(surf, C_HP_BG, (sx-bw//2, sy-self.h//2-8, bw, 4))
                pygame.draw.rect(surf, C_HP_BAR, (sx-bw//2, sy-self.h//2-8, int(bw*self.hp/self.max_hp), 4))
    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

class Gazer:
    def __init__(self, x, y=None, hp_mult=1.0):
        self.x = float(x)
        self.y = float(y if y else GROUND_Y - 20)
        self.w, self.h = 36, 40
        self.hp = int(GAZER_HP * hp_mult)
        self.max_hp = self.hp
        self.shoot_timer = random.randint(30, GAZER_SHOOT_CD)
        self.alive = True
        self.night_buffed = False
        self.hurt_flash = 0
        self.bob_offset = random.uniform(0, math.pi*2)
    def apply_night_buff(self):
        if not self.night_buffed:
            self.night_buffed = True
            self.hp = int(self.hp * NIGHT_HP_MULT)
            self.max_hp = int(self.max_hp * NIGHT_HP_MULT)
            self.shoot_timer = max(30, self.shoot_timer // 2)
    def take_damage(self, dmg):
        self.hp -= dmg
        self.hurt_flash = 8
        if self.hp <= 0:
            self.alive = False
    def update(self, player_x, frame_count):
        self.shoot_timer -= 1
        self.bob_offset += 0.03
        if self.hurt_flash > 0:
            self.hurt_flash -= 1
    def should_shoot(self, player_x):
        if self.shoot_timer <= 0:
            cd = GAZER_SHOOT_CD // 2 if self.night_buffed else GAZER_SHOOT_CD
            self.shoot_timer = cd
            dist = abs(player_x - self.x)
            if dist < 500:
                d = 1 if player_x > self.x else -1
                return Fireball(self.x + d * 20, self.y, FIREBALL_SPEED * d)
        return None
    def draw(self, surf, cam, img, frame_count):
        bob = math.sin(self.bob_offset) * 3
        sx, sy = cam.apply(self.x, self.y + bob)
        if -50 < sx < SW + 50:
            i = img
            if self.hurt_flash > 0:
                i = img.copy()
                i.fill((255,100,100), special_flags=pygame.BLEND_RGB_ADD)
            surf.blit(i, (sx - self.w//2, sy - self.h//2))
            if self.night_buffed:
                gs = pygame.Surface((self.w+16, self.h+16), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (255,30,0,50), (0,0,self.w+16,self.h+16))
                surf.blit(gs, (sx-self.w//2-8, sy-self.h//2-8))
            if self.hp < self.max_hp:
                bw = 30
                pygame.draw.rect(surf, C_HP_BG, (sx-bw//2, sy-self.h//2-8, bw, 4))
                pygame.draw.rect(surf, C_HP_BAR, (sx-bw//2, sy-self.h//2-8, int(bw*self.hp/self.max_hp), 4))
    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

class Baron:
    def __init__(self, x):
        self.x, self.y = float(x), GROUND_Y - 70.0
        self.w, self.h = 100, 140
        self.hp = BARON_HP
        self.max_hp = BARON_HP
        self.alive = True
        self.phase = 1
        self.state = "walk"  # walk, swing, shoot, jump, pound, idle
        self.state_timer = 0
        self.direction = -1
        self.speed = BARON_SPEED
        self.hurt_flash = 0
        self.summoned = False
        self.attack_cd = 90
        self.ground_y = GROUND_Y - 70.0
        self.vy = 0
        self.enraged = False
    def take_damage(self, dmg):
        self.hp -= dmg
        self.hurt_flash = 8
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        elif self.hp <= self.max_hp // 2 and self.phase == 1:
            self.phase = 2
            self.enraged = True
            self.speed = BARON_SPEED * 1.8
    def update(self, player_x, player_y):
        self.direction = 1 if player_x > self.x else -1
        dist = abs(player_x - self.x)
        if self.hurt_flash > 0:
            self.hurt_flash -= 1
        self.attack_cd -= 1
        # Gravity for jumps
        if self.y < self.ground_y:
            self.vy += GRAVITY * 0.8
            self.y += self.vy
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vy = 0
                if self.state == "jump":
                    self.state = "pound"
                    self.state_timer = 30
        if self.state == "pound":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = "walk"
                self.attack_cd = 60
            return
        if self.state == "swing":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = "walk"
                self.attack_cd = 60
            return
        if self.state == "shoot":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = "walk"
                self.attack_cd = 90
            return
        # Walk toward player
        if self.state == "walk":
            if dist > 60:
                self.x += self.speed * self.direction
            if self.attack_cd <= 0:
                if self.phase == 2 and random.random() < 0.35:
                    self.state = "jump"
                    self.vy = -14
                    self.attack_cd = 120
                elif dist < 80:
                    self.state = "swing"
                    self.state_timer = 30
                    self.attack_cd = 60
                else:
                    self.state = "shoot"
                    self.state_timer = 20
                    self.attack_cd = 90
    def get_attack(self, player_rect):
        """Returns (attack_type, data) or None."""
        if self.state == "swing" and self.state_timer == 25:
            hr = pygame.Rect(self.x + self.direction*40 - 30, self.y - 30, 60, 80)
            if hr.colliderect(player_rect):
                return ("hammer", BARON_HAMMER_DMG)
        if self.state == "shoot" and self.state_timer == 15:
            fireballs = []
            d = self.direction
            fireballs.append(Fireball(self.x + d*50, self.y - 20, FIREBALL_SPEED*1.5*d))
            fireballs.append(Fireball(self.x + d*50, self.y + 10, FIREBALL_SPEED*1.5*d))
            return ("fireballs", fireballs)
        if self.state == "pound" and self.state_timer == 28:
            shocks = []
            shocks.append(Shockwave(self.x, GROUND_Y - 10, 1))
            shocks.append(Shockwave(self.x, GROUND_Y - 10, -1))
            return ("shockwave", shocks)
        return None
    def should_summon(self):
        if self.phase == 2 and not self.summoned and self.hp < self.max_hp * 0.4:
            self.summoned = True
            return True
        return False
    def draw(self, surf, cam, img):
        sx, sy = cam.apply(self.x, self.y)
        if -120 < sx < SW + 120:
            i = img if self.direction > 0 else pygame.transform.flip(img, True, False)
            if self.hurt_flash > 0:
                i = i.copy()
                i.fill((255,80,80), special_flags=pygame.BLEND_RGB_ADD)
            if self.enraged:
                gs = pygame.Surface((self.w+30, self.h+30), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (255,20,0,60), (0,0,self.w+30,self.h+30))
                surf.blit(gs, (sx-self.w//2-15, sy-self.h//2-15))
            surf.blit(i, (sx - self.w//2 - 10, sy - self.h//2))
            # HP bar
            bw = 100
            pygame.draw.rect(surf, C_HP_BG, (sx-bw//2, sy-self.h//2-14, bw, 8))
            pygame.draw.rect(surf, (200,30,30), (sx-bw//2, sy-self.h//2-14, int(bw*self.hp/self.max_hp), 8))
            pygame.draw.rect(surf, C_WHITE, (sx-bw//2, sy-self.h//2-14, bw, 8), 1)
    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

class Item:
    def __init__(self, x, y, item_type):
        self.x, self.y = float(x), float(y)
        self.item_type = item_type  # "ammo", "health", "boots", "shield", "spread_gun"
        self.alive = True
        self.bob = random.uniform(0, math.pi*2)
    def update(self):
        self.bob += 0.05
    def draw(self, surf, cam, images):
        bob = math.sin(self.bob) * 4
        sx, sy = cam.apply(self.x, self.y + bob)
        if -30 < sx < SW + 30:
            img = images.get(self.item_type)
            if img:
                surf.blit(img, (sx - img.get_width()//2, sy - img.get_height()//2))
            # Glow
            gs = pygame.Surface((30,30), pygame.SRCALPHA)
            colors = {"ammo":(255,220,50), "health":(50,255,50), "boots":(100,200,255),
                      "shield":(80,140,240), "spread_gun":(255,200,50)}
            c = colors.get(self.item_type, (255,255,255))
            pygame.draw.circle(gs, (*c, 40), (15,15), 15)
            surf.blit(gs, (sx-15, sy+bob-15))
    def get_rect(self):
        return pygame.Rect(self.x - 11, self.y - 10, 22, 20)
