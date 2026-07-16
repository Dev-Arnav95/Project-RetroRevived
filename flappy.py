#!/usr/bin/env python3
"""
Flappy Bird - Pixel Art Edition
"""

import pygame
import random
import sys
import os
import json
import math

from sprites import (
    create_bird, create_pipe, create_background, create_background_with_stars,
    create_city_skyline, create_ground,
    create_get_ready_screen, create_game_over_screen,
    create_medal, create_shop_screen, create_pause_screen,
    create_rebirth_screen, create_coin_icon, create_settings_screen,
    draw_text_with_shadow, draw_text_centered, draw_button, draw_gear,
    BIRD_NAMES, BIRD_PRICES, BG_NAMES, BG_PRICES,
    BRIGHT_WHITE, SHADOW_BLACK, GOLD, GOLD_DARK, BRIGHT_GREEN,
    BRIGHT_RED, BRIGHT_CYAN, BRIGHT_YELLOW, PANEL_BG, PANEL_BORDER,
    PANEL_INNER, BUTTON_GREEN, BUTTON_GREEN_DARK, BUTTON_RED,
    BUTTON_RED_DARK, BUTTON_BLUE, BUTTON_BLUE_DARK, BUTTON_GRAY,
    BUTTON_GRAY_DARK, TEXT_DIM
)

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60
GRAVITY = 0.5
FLAP_STRENGTH = -8
MAX_FALL_SPEED = 12
BIRD_X = 60
GROUND_HEIGHT = 112

STATE_MENU = 0
STATE_READY = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3
STATE_SPRITE_SELECT = 4
STATE_SHOP = 5
STATE_PAUSED = 6
STATE_REBIRTH = 7
STATE_SETTINGS = 8

LEVELS = {
    1:  {"name": "Easy",      "color": (100, 200, 100), "req": 0},
    2:  {"name": "Normal",    "color": (200, 200, 100), "req": 10},
    3:  {"name": "Medium",    "color": (200, 150, 100), "req": 25},
    4:  {"name": "Hard",      "color": (200, 100, 100), "req": 45},
    5:  {"name": "Insane",    "color": (180, 50, 50),   "req": 70},
    6:  {"name": "Extreme",   "color": (150, 0, 150),   "req": 100},
    7:  {"name": "Elite",     "color": (100, 0, 200),   "req": 135},
    8:  {"name": "Mythic",    "color": (0, 150, 200),   "req": 175},
    9:  {"name": "Legendary", "color": (255, 215, 0),   "req": 220},
    10: {"name": "Godlike",   "color": (255, 50, 50),   "req": 270},
}

BASE_GAP = 150
BASE_SPEED = 2.0
BASE_FREQ = 2200
MIN_GAP = 90
MAX_SPEED = 5.5
MIN_FREQ = 1000
RAMP_SPEED = 0.08
RAMP_GAP = 0.15
RAMP_FREQ = 8

REBIRTH_LEVEL_REQ = 10
REBIRTH_MULTIPLIER = 1.1

DEFAULT_SETTINGS = {
    "master_vol": 0.7,
    "bird_sfx_vol": 0.8,
    "point_sfx_vol": 0.8,
    "ui_sfx_vol": 0.6,
    "quality": "medium",
    "screen_shake": True,
    "show_fps": False,
}


def exp_for_level(level):
    if level <= 1:
        return 0
    return 5 * (level - 1) * (level + 2) // 2


def make_bird_frames(bird_type):
    n = 16 if bird_type == 7 else 3
    return [create_bird(i, bird_type) for i in range(n)]


class FloatingText:
    def __init__(self, x, y, text, color, font_size=24, speed=1.0, lifetime=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.speed = speed
        self.lifetime = lifetime
        self.age = 0
        self.alive = True

    def update(self):
        self.age += 1
        self.y -= self.speed
        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, surface):
        alpha = max(0, 255 - int(255 * self.age / self.lifetime))
        rendered = self.font.render(self.text, True, self.color)
        shadow = self.font.render(self.text, True, SHADOW_BLACK)
        temp = pygame.Surface((rendered.get_width() + 2, rendered.get_height() + 2), pygame.SRCALPHA)
        temp.blit(shadow, (2, 2))
        temp.blit(rendered, (0, 0))
        temp.set_alpha(alpha)
        surface.blit(temp, (int(self.x - rendered.get_width() // 2), int(self.y)))


class FlappyBird:
    def __init__(self):
        self.display = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Flappy Bird - Pixel Art")

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "flappybird.png"
        )
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)

        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.save_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "save_data.json"
        )
        self.settings_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "settings.json"
        )
        self.save_data = self.load_save()
        self.settings = self.load_settings()

        self.selected_bird = self.save_data.get("selected_bird", 0)
        self.unlocked_birds = self.save_data.get("unlocked_birds", [0])
        self.selected_bg = self.save_data.get("selected_background", 0)
        self.unlocked_bgs = self.save_data.get("unlocked_backgrounds", [0])
        self.coins = self.save_data.get("coins", 0)
        self.exp = self.save_data.get("exp", 0)
        self.player_level = self.save_data.get("level", 1)
        self.total_score = self.save_data.get("total_score", 0)
        self.games_played = self.save_data.get("games_played", 0)
        self.rebirth_count = self.save_data.get("rebirth_count", 0)
        self.coin_multiplier = self.save_data.get("coin_multiplier", 1.0)

        self.bird_frames = make_bird_frames(self.selected_bird)
        self.bird_current_frame = 0
        self.bird = self.bird_frames[0]

        self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, self.selected_bg)
        self.skyline = create_city_skyline(SCREEN_WIDTH)
        self.ground_original = create_ground(SCREEN_WIDTH)
        self.ground = self.ground_original.copy()

        self.get_ready_screen = create_get_ready_screen()
        self.game_over_screen = create_game_over_screen()

        self.flap_sound = self.create_flap_sound()
        self.score_sound = self.create_score_sound()
        self.hit_sound = self.create_hit_sound()
        self.fall_sound = self.create_fall_sound()
        self.level_up_sound = self.create_level_up_sound()
        self.coin_sound = self.create_coin_sound()
        self.rebirth_sound = self.create_rebirth_sound()

        self.shop_tab = 0
        self.shop_selected = 0
        self.shop_surface = None
        self.shop_buy_rect = None

        self.pause_surface = None
        self.pause_resume_rect = None
        self.pause_menu_rect = None

        self.rebirth_surface = None
        self.rebirth_do_rect = None
        self.rebirth_cancel_rect = None

        self.settings_surface = None
        self.settings_back_rect = None
        self.settings_sliders = {}
        self.settings_qual_buttons = {}
        self.settings_toggles = {}
        self.settings_reset_rect = None
        self.dragging_slider = None

        self.gear_rect = pygame.Rect(2, 2, 28, 28)

        self.sprite_select_cache = None
        self.skyline_x = 0.0
        self.floating_texts = []
        self.anim_timer = 0
        self.menu_pulse = 0.0

        self.reset_game()

    def create_flap_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(800, 1200, 0.1, 0.3))

    def create_score_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(1200, 1800, 0.15, 0.4))

    def create_hit_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(400, 100, 0.2, 0.5))

    def create_fall_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(600, 200, 0.3, 0.3))

    def create_level_up_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(600, 1200, 0.2, 0.4))

    def create_coin_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(1400, 2000, 0.08, 0.3))

    def create_rebirth_sound(self):
        return pygame.mixer.Sound(buffer=self._generate_tone(300, 900, 0.5, 0.4))

    def _generate_tone(self, start_freq, end_freq, duration, volume=0.5):
        import array
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            progress = i / num_samples
            freq = start_freq + (end_freq - start_freq) * progress
            val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
            fade = 1.0 - (progress * 0.5)
            val = int(val * fade)
            val = max(-32767, min(32767, val))
            buf[i] = val
        return buf

    def reset_game(self):
        self.state = STATE_MENU
        self.score = 0
        self.level = self.player_level
        self.bird_y = SCREEN_HEIGHT // 2
        self.bird_velocity = 0
        self.bird_rotation = 0
        self.bird_animation_timer = 0
        self.pipes = []
        self.last_pipe_time = 0
        self.ground_x = 0
        self.flash_alpha = 0
        self.score_panel_shown = False
        self.game_over_timer = 0
        self.level_up_timer = 0
        self.show_level_up = False
        self.exp_timer = 0.0
        self.skyline_x = 0.0
        self.floating_texts = []
        self.run_time = 0
        self.shake_offset = [0, 0]
        self.shake_timer = 0

    def add_floating(self, x, y, text, color, font_size=24, speed=1.0, lifetime=60):
        self.floating_texts.append(FloatingText(x, y, text, color, font_size, speed, lifetime))

    def load_save(self):
        try:
            with open(self.save_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "high_score": 0, "selected_bird": 0, "unlocked_birds": [0],
                "total_score": 0, "games_played": 0,
                "exp": 0, "level": 1, "coins": 0,
                "unlocked_skins": [0], "unlocked_backgrounds": [0],
                "selected_background": 0,
                "rebirth_count": 0, "coin_multiplier": 1.0
            }

    def save_save(self):
        try:
            data = {
                "high_score": self.save_data.get("high_score", 0),
                "selected_bird": self.selected_bird,
                "unlocked_birds": self.unlocked_birds,
                "total_score": self.total_score,
                "games_played": self.games_played,
                "exp": self.exp,
                "level": self.player_level,
                "coins": self.coins,
                "unlocked_skins": self.unlocked_birds,
                "unlocked_backgrounds": self.unlocked_bgs,
                "selected_background": self.selected_bg,
                "rebirth_count": self.rebirth_count,
                "coin_multiplier": self.coin_multiplier
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                merged = dict(DEFAULT_SETTINGS)
                merged.update(data)
                return merged
        except (FileNotFoundError, json.JSONDecodeError):
            return dict(DEFAULT_SETTINGS)

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception:
            pass

    def play_sound(self, sound, category="ui"):
        vol = self.settings.get("master_vol", 0.7)
        if category == "bird":
            vol *= self.settings.get("bird_sfx_vol", 0.8)
        elif category == "point":
            vol *= self.settings.get("point_sfx_vol", 0.8)
        elif category == "ui":
            vol *= self.settings.get("ui_sfx_vol", 0.6)
        sound.set_volume(max(0.0, min(1.0, vol)))
        sound.play()

    def get_level_config(self):
        return LEVELS.get(self.level, LEVELS[1])

    def get_current_difficulty(self):
        t = self.run_time
        speed = min(MAX_SPEED, BASE_SPEED + t * RAMP_SPEED)
        gap = max(MIN_GAP, BASE_GAP - t * RAMP_GAP)
        freq = max(MIN_FREQ, BASE_FREQ - t * RAMP_FREQ)
        config = self.get_level_config()
        return {"speed": speed, "gap": int(gap), "freq": int(freq), "color": config["color"]}

    def get_next_level_req(self):
        next_level = self.player_level + 1
        if next_level in LEVELS:
            return LEVELS[next_level]["req"]
        return None

    def check_level_up(self):
        while True:
            next_req = self.get_next_level_req()
            if next_req is not None and self.exp >= next_req:
                self.player_level += 1
                self.level = self.player_level
                self.show_level_up = True
                self.level_up_timer = pygame.time.get_ticks()
                self.play_sound(self.level_up_sound, "ui")
                self.add_floating(SCREEN_WIDTH // 2, 180, f"LEVEL {self.player_level}!", BRIGHT_YELLOW, 36, 1.2, 90)
            else:
                break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_SETTINGS:
                        self.state = STATE_MENU
                    elif self.state == STATE_SPRITE_SELECT:
                        self.state = STATE_MENU
                    elif self.state == STATE_SHOP:
                        self.state = STATE_MENU
                    elif self.state == STATE_REBIRTH:
                        self.state = STATE_MENU
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                        self.pause_surface, self.pause_resume_rect, self.pause_menu_rect = create_pause_screen()
                    elif self.state == STATE_MENU:
                        return False
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.state == STATE_MENU:
                        self.state = STATE_READY
                    elif self.state == STATE_READY:
                        self.state = STATE_PLAYING
                        self.bird_velocity = FLAP_STRENGTH
                        self.last_pipe_time = pygame.time.get_ticks()
                        self.play_sound(self.flap_sound, "bird")
                    elif self.state == STATE_PLAYING:
                        self.bird_velocity = FLAP_STRENGTH
                        self.play_sound(self.flap_sound, "bird")
                    elif self.state == STATE_GAME_OVER:
                        if self.score_panel_shown:
                            self.reset_game()
                            self.state = STATE_READY
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.state == STATE_PLAYING:
                        self.bird_velocity = FLAP_STRENGTH
                        self.play_sound(self.flap_sound, "bird")
                    elif self.state == STATE_MENU:
                        self.state = STATE_READY
                    elif self.state == STATE_READY:
                        self.state = STATE_PLAYING
                        self.bird_velocity = FLAP_STRENGTH
                        self.last_pipe_time = pygame.time.get_ticks()
                        self.play_sound(self.flap_sound, "bird")
                    elif self.state == STATE_GAME_OVER:
                        if self.score_panel_shown:
                            self.reset_game()
                            self.state = STATE_READY
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.state == STATE_SETTINGS:
                        self.handle_settings_click(event.pos)
                    elif self.gear_rect.collidepoint(event.pos) and self.state not in (STATE_PLAYING, STATE_READY):
                        self.state = STATE_SETTINGS
                        self.settings_surface = None
                    elif self.state == STATE_SPRITE_SELECT:
                        self.handle_sprite_click(event.pos)
                    elif self.state == STATE_SHOP:
                        self.handle_shop_click(event.pos)
                    elif self.state == STATE_REBIRTH:
                        self.handle_rebirth_click(event.pos)
                    elif self.state == STATE_PAUSED:
                        self.handle_pause_click(event.pos)
                    elif self.state == STATE_GAME_OVER and self.score_panel_shown:
                        if self.handle_game_over_click(event.pos):
                            pass
                        else:
                            self.handle_tap()
                    elif self.state == STATE_PLAYING:
                        pause_area = pygame.Rect(SCREEN_WIDTH - 30, 30, 30, 20)
                        if pause_area.collidepoint(event.pos):
                            self.state = STATE_PAUSED
                            self.pause_surface, self.pause_resume_rect, self.pause_menu_rect = create_pause_screen()
                        else:
                            self.handle_tap()
                    elif self.state == STATE_MENU:
                        if self.handle_menu_click(event.pos):
                            pass
                        else:
                            self.handle_tap()
                    else:
                        self.handle_tap()
            if event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.state == STATE_SETTINGS:
                    self.handle_settings_drag(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = None
        return True

    def handle_game_over_click(self, pos):
        play_button = pygame.Rect(88, 250, 112, 40)
        if play_button.collidepoint(pos):
            return False

        home_button = pygame.Rect(88, 380, 112, 32)
        if home_button.collidepoint(pos):
            self.reset_game()
            self.state = STATE_MENU
            return True

        num_birds = min(len(BIRD_NAMES), 8)
        spacing = min(30, (SCREEN_WIDTH - 40) // num_birds)
        start_x = (SCREEN_WIDTH - num_birds * spacing) // 2

        for i in range(num_birds):
            x = start_x + i * spacing
            y = 295
            box = pygame.Rect(x - 3, y - 3, 26, 20)
            if box.collidepoint(pos):
                if i in self.unlocked_birds:
                    self.selected_bird = i
                    self.bird_frames = make_bird_frames(i)
                    self.bird = self.bird_frames[0]
                    self.sprite_select_cache = None
                    self.save_save()
                    return True
        return False

    def handle_sprite_click(self, pos):
        for i in range(len(BIRD_NAMES)):
            x = 60 + (i % 2) * 100
            y = 110 + (i // 2) * 70
            box = pygame.Rect(x - 5, y - 5, 50, 40)
            if box.collidepoint(pos):
                if i in self.unlocked_birds:
                    self.selected_bird = i
                    self.bird_frames = make_bird_frames(i)
                    self.bird = self.bird_frames[0]
                    self.sprite_select_cache = None
                    self.save_save()

    def handle_shop_click(self, pos):
        tab_y = 240
        tab_w = 120
        tab_h = 28
        tab_gap = 8
        tab_start_x = (SCREEN_WIDTH - (tab_w * 2 + tab_gap)) // 2

        for i in range(2):
            tx = tab_start_x + i * (tab_w + tab_gap)
            tab_rect = pygame.Rect(tx, tab_y, tab_w, tab_h)
            if tab_rect.collidepoint(pos):
                if self.shop_tab != i:
                    self.shop_tab = i
                    self.shop_selected = 0
                return

        item_w = 58
        item_h = 68
        item_gap = 6
        items_per_row = 4
        total_items_w = items_per_row * item_w + (items_per_row - 1) * item_gap
        items_start_x = (SCREEN_WIDTH - total_items_w) // 2
        items_y = 280

        if self.shop_tab == 0:
            num_items = len(BIRD_NAMES)
        else:
            num_items = len(BG_NAMES)

        for i in range(num_items):
            row = i // items_per_row
            col = i % items_per_row
            ix = items_start_x + col * (item_w + item_gap)
            iy = items_y + row * (item_h + item_gap)
            item_rect = pygame.Rect(ix, iy, item_w, item_h)
            if item_rect.collidepoint(pos):
                self.shop_selected = i
                if self.shop_tab == 0:
                    if i in self.unlocked_birds:
                        self.selected_bird = i
                        self.bird_frames = make_bird_frames(i)
                        self.bird = self.bird_frames[0]
                        self.sprite_select_cache = None
                        self.save_save()
                else:
                    if i in self.unlocked_bgs:
                        self.selected_bg = i
                        self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, i)
                        self.save_save()
                return

        if self.shop_buy_rect and self.shop_buy_rect.collidepoint(pos):
            self.handle_buy()
            return

    def handle_buy(self):
        if self.shop_tab == 0:
            prices = BIRD_PRICES
            unlocked = self.unlocked_birds
        else:
            prices = BG_PRICES
            unlocked = self.unlocked_bgs

        item = self.shop_selected
        if item >= len(prices):
            return

        if item in unlocked:
            if self.shop_tab == 0:
                self.selected_bird = item
                self.bird_frames = make_bird_frames(item)
                self.bird = self.bird_frames[0]
            else:
                self.selected_bg = item
                self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, item)
            self.sprite_select_cache = None
            self.save_save()
            return

        if prices[item] <= 0:
            unlocked.append(item)
            if self.shop_tab == 0:
                self.selected_bird = item
                self.bird_frames = make_bird_frames(item)
                self.bird = self.bird_frames[0]
            else:
                self.selected_bg = item
                self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, item)
            self.save_save()
            return

        if self.coins >= prices[item]:
            self.coins -= prices[item]
            unlocked.append(item)
            if self.shop_tab == 0:
                self.selected_bird = item
                self.bird_frames = make_bird_frames(item)
                self.bird = self.bird_frames[0]
            else:
                self.selected_bg = item
                self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, item)
            self.add_floating(SCREEN_WIDTH // 2, 200, "PURCHASED!", BRIGHT_GREEN, 28, 1.0, 60)
            self.play_sound(self.coin_sound, "point")
            self.save_save()

    def handle_pause_click(self, pos):
        if self.pause_resume_rect and self.pause_resume_rect.collidepoint(pos):
            self.state = STATE_PLAYING
        elif self.pause_menu_rect and self.pause_menu_rect.collidepoint(pos):
            self.reset_game()
            self.state = STATE_MENU

    def handle_menu_click(self, pos):
        shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 430, 112, 28)
        if shop_rect.collidepoint(pos):
            self.state = STATE_SHOP
            self.shop_tab = 0
            self.shop_selected = 0
            return True

        rebirth_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 465, 112, 28)
        if rebirth_rect.collidepoint(pos):
            self.state = STATE_REBIRTH
            self.rebirth_surface, self.rebirth_do_rect, self.rebirth_cancel_rect = create_rebirth_screen(
                self.rebirth_count, self.coin_multiplier, self.player_level, REBIRTH_LEVEL_REQ
            )
            return True

        select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 497, 112, 22)
        if select_rect.collidepoint(pos):
            self.state = STATE_SPRITE_SELECT
            self.sprite_select_cache = None
            return True

        return False

    def handle_rebirth_click(self, pos):
        if self.rebirth_cancel_rect and self.rebirth_cancel_rect.collidepoint(pos):
            self.state = STATE_MENU
            return

        if self.rebirth_do_rect and self.rebirth_do_rect.collidepoint(pos):
            if self.player_level >= REBIRTH_LEVEL_REQ:
                self.rebirth_count += 1
                self.coin_multiplier = round(self.coin_multiplier * REBIRTH_MULTIPLIER, 1)
                self.coins = 0
                self.exp = 0
                self.player_level = 1
                self.level = 1
                self.unlocked_birds = [0]
                self.unlocked_bgs = [0]
                self.selected_bird = 0
                self.selected_bg = 0
                self.bird_frames = make_bird_frames(0)
                self.bird = self.bird_frames[0]
                self.background = create_background_with_stars(SCREEN_WIDTH, SCREEN_HEIGHT, 0)
                self.play_sound(self.rebirth_sound, "ui")
                self.save_save()
                self.state = STATE_MENU
                self.add_floating(SCREEN_WIDTH // 2, 200, f"REBIRTH #{self.rebirth_count}!", (255, 100, 255), 36, 1.0, 90)

    def handle_settings_click(self, pos):
        if self.settings_back_rect and self.settings_back_rect.collidepoint(pos):
            self.state = STATE_MENU
            self.save_settings()
            return

        for key, rect in self.settings_sliders.items():
            if rect.collidepoint(pos):
                self.dragging_slider = key
                self._update_slider_value(key, pos[0], rect)
                return

        for key, rect in self.settings_qual_buttons.items():
            if rect.collidepoint(pos):
                self.settings["quality"] = key
                self.save_settings()
                self.settings_surface = None
                return

        for key, rect in self.settings_toggles.items():
            if rect.collidepoint(pos):
                self.settings[key] = not self.settings.get(key, False)
                self.save_settings()
                self.settings_surface = None
                return

        if self.settings_reset_rect and self.settings_reset_rect.collidepoint(pos):
            self.settings = dict(DEFAULT_SETTINGS)
            self.save_settings()
            self.settings_surface = None
            return

    def handle_settings_drag(self, pos):
        if self.dragging_slider and self.dragging_slider in self.settings_sliders:
            rect = self.settings_sliders[self.dragging_slider]
            self._update_slider_value(self.dragging_slider, pos[0], rect)

    def _update_slider_value(self, key, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        ratio = max(0.0, min(1.0, ratio))
        self.settings[key] = round(ratio, 2)
        self.save_settings()
        self.settings_surface = None

    def handle_tap(self):
        if self.state == STATE_MENU:
            self.state = STATE_READY
        elif self.state == STATE_READY:
            self.state = STATE_PLAYING
            self.bird_velocity = FLAP_STRENGTH
            self.last_pipe_time = pygame.time.get_ticks()
            self.play_sound(self.flap_sound, "bird")
        elif self.state == STATE_PLAYING:
            self.bird_velocity = FLAP_STRENGTH
            self.play_sound(self.flap_sound, "bird")
        elif self.state == STATE_GAME_OVER:
            if self.score_panel_shown:
                self.reset_game()
                self.state = STATE_READY

    def update(self):
        current_time = pygame.time.get_ticks()
        self.anim_timer += 1
        self.menu_pulse = (math.sin(self.anim_timer * 0.05) + 1) * 0.5

        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_offset = [random.randint(-3, 3), random.randint(-3, 3)]
        else:
            self.shake_offset = [0, 0]

        for ft in self.floating_texts[:]:
            ft.update()
            if not ft.alive:
                self.floating_texts.remove(ft)

        if self.state == STATE_MENU:
            self.bird_animation_timer += 1
            if self.bird_animation_timer >= 8:
                self.bird_animation_timer = 0
                self.bird_current_frame = (self.bird_current_frame + 1) % len(self.bird_frames)
            self.bird_y = SCREEN_HEIGHT // 2 + math.sin(current_time / 300) * 10
            self.bird = self.bird_frames[self.bird_current_frame]
            self.bird_rotation = 0
            self.scroll_ground()

        elif self.state == STATE_READY:
            self.bird_animation_timer += 1
            if self.bird_animation_timer >= 8:
                self.bird_animation_timer = 0
                self.bird_current_frame = (self.bird_current_frame + 1) % len(self.bird_frames)
            self.bird_y = SCREEN_HEIGHT // 2 + math.sin(current_time / 300) * 10
            self.bird = self.bird_frames[self.bird_current_frame]
            self.bird_rotation = 0
            self.scroll_ground()

        elif self.state == STATE_PLAYING:
            config = self.get_current_difficulty()
            self.run_time += 1.0 / FPS

            self.bird_velocity += GRAVITY
            if self.bird_velocity > MAX_FALL_SPEED:
                self.bird_velocity = MAX_FALL_SPEED
            self.bird_y += self.bird_velocity

            if self.bird_velocity < 0:
                self.bird_rotation = -25
            else:
                self.bird_rotation = min(90, self.bird_velocity * 6)

            self.bird_animation_timer += 1
            if self.bird_animation_timer >= 6:
                self.bird_animation_timer = 0
                self.bird_current_frame = (self.bird_current_frame + 1) % len(self.bird_frames)
            self.bird = self.bird_frames[self.bird_current_frame]

            self.exp_timer += 1.0 / FPS
            if self.exp_timer >= 1.0:
                self.exp_timer -= 1.0
                self.exp += 1
                self.check_level_up()

            if current_time - self.last_pipe_time > config["freq"]:
                gap_y = random.randint(80, SCREEN_HEIGHT - GROUND_HEIGHT - 80 - config["gap"])
                result = create_pipe(SCREEN_WIDTH, gap_y, config["gap"], SCREEN_HEIGHT - GROUND_HEIGHT)
                top_pipe, bottom_pipe, pipe_width, gap_size = result
                self.pipes.append({
                    'x': SCREEN_WIDTH,
                    'top': top_pipe,
                    'bottom': bottom_pipe,
                    'width': pipe_width,
                    'gap_y': gap_y,
                    'gap_size': gap_size,
                    'bottom_y': gap_y + gap_size,
                    'scored': False
                })
                self.last_pipe_time = current_time

            for pipe in self.pipes:
                pipe['x'] -= config["speed"]

            self.pipes = [p for p in self.pipes if p['x'] > -p['width'] - 10]

            for pipe in self.pipes:
                if not pipe['scored'] and pipe['x'] + pipe['width'] < BIRD_X:
                    pipe['scored'] = True
                    self.score += 1
                    self.play_sound(self.score_sound, "point")
                    earned = max(1, int(1 * self.coin_multiplier))
                    self.coins += earned
                    self.play_sound(self.coin_sound, "point")
                    if earned > 1:
                        self.add_floating(BIRD_X + 30, int(self.bird_y) - 10, f"+{earned}", GOLD, 20, 1.5, 40)
                    else:
                        self.add_floating(BIRD_X + 30, int(self.bird_y) - 10, "+1", GOLD, 18, 1.2, 35)

            self.scroll_ground()
            self.scroll_skyline()

            if self.check_collision():
                self.state = STATE_GAME_OVER
                self.game_over_timer = current_time
                self.flash_alpha = 200
                self.play_sound(self.hit_sound, "bird")
                if self.settings.get("screen_shake", True):
                    self.shake_timer = 15
                self.games_played += 1
                self.total_score += self.score
                high = self.save_data.get("high_score", 0)
                if self.score > high:
                    self.save_data["high_score"] = self.score
                self.save_save()

        elif self.state == STATE_GAME_OVER:
            self.bird_velocity += GRAVITY
            if self.bird_velocity > MAX_FALL_SPEED:
                self.bird_velocity = MAX_FALL_SPEED
            self.bird_y += self.bird_velocity
            self.bird_rotation = 90

            if self.flash_alpha > 0:
                self.flash_alpha -= 8

            if not self.score_panel_shown and current_time - self.game_over_timer > 500:
                self.score_panel_shown = True
                self.play_sound(self.fall_sound, "ui")

        return True

    def scroll_ground(self):
        speed = self.get_current_difficulty()["speed"]
        self.ground_x -= speed
        if self.ground_x <= -SCREEN_WIDTH:
            self.ground_x = 0

    def scroll_skyline(self):
        speed = self.get_current_difficulty()["speed"]
        self.skyline_x -= speed * 0.3
        if self.skyline_x <= -SCREEN_WIDTH:
            self.skyline_x += SCREEN_WIDTH

    def check_collision(self):
        bird_rect = pygame.Rect(BIRD_X + 6, int(self.bird_y) + 6, 36, 24)

        if self.bird_y + 36 >= SCREEN_HEIGHT - GROUND_HEIGHT:
            return True
        if self.bird_y <= 0:
            return True

        for pipe in self.pipes:
            top_rect = pygame.Rect(pipe['x'], 0, pipe['width'], pipe['gap_y'])
            bottom_rect = pygame.Rect(pipe['x'], pipe['bottom_y'], pipe['width'], SCREEN_HEIGHT - pipe['bottom_y'])

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True

        return False

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        sx = int(self.skyline_x)
        skyline_y = SCREEN_HEIGHT - GROUND_HEIGHT - 120
        self.screen.blit(self.skyline, (sx, skyline_y))
        self.screen.blit(self.skyline, (sx + SCREEN_WIDTH, skyline_y))

        for pipe in self.pipes:
            self.screen.blit(pipe['top'], (pipe['x'], 0))
            self.screen.blit(pipe['bottom'], (pipe['x'], pipe['bottom_y']))

        gx = int(self.ground_x)
        self.screen.blit(self.ground, (gx, SCREEN_HEIGHT - GROUND_HEIGHT))
        self.screen.blit(self.ground, (gx + SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))

        rotated_bird = pygame.transform.rotate(self.bird, self.bird_rotation)
        bird_rect = rotated_bird.get_rect(center=(BIRD_X + 24, int(self.bird_y) + 18))
        self.screen.blit(rotated_bird, bird_rect)

        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_READY:
            self.draw_ready()
        elif self.state == STATE_PLAYING:
            self.draw_hud()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == STATE_SPRITE_SELECT:
            self.draw_sprite_select()
        elif self.state == STATE_SHOP:
            self.draw_shop()
        elif self.state == STATE_REBIRTH:
            self.draw_rebirth()
        elif self.state == STATE_PAUSED:
            self.draw_hud()
            if self.pause_surface:
                self.screen.blit(self.pause_surface, (0, 0))
        elif self.state == STATE_SETTINGS:
            self.draw_hud()

        for ft in self.floating_texts:
            ft.draw(self.screen)

        if self.flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.fill((255, 255, 255))
            flash.set_alpha(int(self.flash_alpha))
            self.screen.blit(flash, (0, 0))

        if self.state not in (STATE_PLAYING, STATE_READY, STATE_PAUSED, STATE_SETTINGS):
            draw_gear(self.screen, 16, 16, 12, (200, 200, 210))

        if self.state == STATE_SETTINGS:
            self.draw_settings()

        if self.settings.get("show_fps", False):
            fps_font = pygame.font.Font(None, 20)
            fps_text = fps_font.render(f"FPS: {int(self.clock.get_fps())}", True, BRIGHT_GREEN)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 70, 2))

        self.display.blit(self.screen, self.shake_offset)
        pygame.display.flip()

    def draw_menu(self):
        font_big = pygame.font.Font(None, 56)
        font_small = pygame.font.Font(None, 32)
        font_tiny = pygame.font.Font(None, 24)

        draw_text_centered(self.screen, "Flappy Bird", font_big, BRIGHT_WHITE, 70)

        pulse_alpha = int(180 + 75 * self.menu_pulse)
        start_color = (255, 255, pulse_alpha)
        draw_text_centered(self.screen, "TAP TO START", font_small, start_color, 270)

        hs = self.save_data.get("high_score", 0)
        if hs > 0:
            draw_text_centered(self.screen, f"Best: {hs}", font_small, BRIGHT_CYAN, 305)

        coin_icon = create_coin_icon(16)
        self.screen.blit(coin_icon, (SCREEN_WIDTH // 2 - 48, 340))
        coin_s = font_small.render(str(self.coins), True, SHADOW_BLACK)
        self.screen.blit(coin_s, (SCREEN_WIDTH // 2 - 28, 343))
        coin_t = font_small.render(str(self.coins), True, GOLD)
        self.screen.blit(coin_t, (SCREEN_WIDTH // 2 - 30, 341))

        if self.coin_multiplier > 1.0:
            mult_t = font_tiny.render(f"x{self.coin_multiplier} coins", True, BRIGHT_GREEN)
            self.screen.blit(mult_t, (SCREEN_WIDTH // 2 + 10, 346))

        next_exp = exp_for_level(self.player_level + 1) if self.player_level < 10 else None
        if next_exp is not None:
            lv_text = font_tiny.render(f"Lv{self.player_level}  EXP: {self.exp}/{next_exp}", True, TEXT_DIM)
        else:
            lv_text = font_tiny.render(f"Lv{self.player_level}  MAX", True, GOLD)
        self.screen.blit(lv_text, (SCREEN_WIDTH // 2 - lv_text.get_width() // 2, 370))

        shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 398, 112, 28)
        draw_button(self.screen, shop_rect, "SHOP", font_tiny, BUTTON_BLUE, BUTTON_BLUE_DARK)

        rebirth_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 432, 112, 28)
        rebirth_text = f"REBIRTH ({self.rebirth_count})"
        draw_button(self.screen, rebirth_rect, rebirth_text, font_tiny, (180, 60, 200), (140, 40, 160))

        select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 56, 466, 112, 28)
        draw_button(self.screen, select_rect, "SELECT BIRD", font_tiny, BUTTON_GRAY, BUTTON_GRAY_DARK)

    def draw_ready(self):
        self.screen.blit(self.get_ready_screen, (0, 0))

    def draw_hud(self):
        config = self.get_current_difficulty()

        score_str = str(self.score)
        font = pygame.font.Font(None, 52)
        draw_text_with_shadow(self.screen, score_str, font, BRIGHT_WHITE, (SCREEN_WIDTH // 2 - font.render(score_str, True, (0,0,0)).get_width() // 2, 48))

        next_req = self.get_next_level_req()
        if next_req is not None:
            current_req = LEVELS.get(self.player_level, LEVELS[1])["req"]
            needed = next_req - current_req
            progress = (self.exp - current_req) / needed if needed > 0 else 0
            progress = max(0, min(1, progress))

            bar_x = 10
            bar_y = 12
            bar_width = 100
            bar_height = 8

            pygame.draw.rect(self.screen, (30, 30, 40), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            pygame.draw.rect(self.screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height))
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(self.screen, config["color"], (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(self.screen, PANEL_BORDER, (bar_x, bar_y, bar_width, bar_height), 1)

            font_small = pygame.font.Font(None, 18)
            level_text = font_small.render(f"Lv{self.player_level}", True, BRIGHT_WHITE)
            self.screen.blit(level_text, (bar_x, bar_y + bar_height + 2))

            exp_to_next = next_req - self.exp
            next_text = font_small.render(f"{exp_to_next} EXP to next", True, TEXT_DIM)
            self.screen.blit(next_text, (bar_x + bar_width + 5, bar_y))
        else:
            font_small = pygame.font.Font(None, 18)
            draw_text_with_shadow(self.screen, "MAX LEVEL", font_small, GOLD, (10, 12))

        font_small = pygame.font.Font(None, 20)
        coin_icon = create_coin_icon(12)
        self.screen.blit(coin_icon, (SCREEN_WIDTH - 54, 12))
        coin_s = font_small.render(str(self.coins), True, SHADOW_BLACK)
        self.screen.blit(coin_s, (SCREEN_WIDTH - 38, 13))
        coin_t = font_small.render(str(self.coins), True, GOLD)
        self.screen.blit(coin_t, (SCREEN_WIDTH - 40, 11))

        pause_bg = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.rect(pause_bg, (255, 255, 255, 180), (0, 0, 6, 18))
        pygame.draw.rect(pause_bg, (255, 255, 255, 180), (10, 0, 6, 18))
        self.screen.blit(pause_bg, (SCREEN_WIDTH - 20, 34))

        if self.show_level_up:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.level_up_timer
            if elapsed < 2000:
                t = elapsed / 2000.0
                alpha = int(255 * (1.0 - t))
                scale = 1.0 + 0.3 * math.sin(t * math.pi)
                font_big = pygame.font.Font(None, int(48 * scale))
                txt = f"Level {self.player_level}!"
                rendered = font_big.render(txt, True, BRIGHT_YELLOW)
                rendered.set_alpha(alpha)
                shadow_r = font_big.render(txt, True, SHADOW_BLACK)
                shadow_r.set_alpha(alpha)
                cx = SCREEN_WIDTH // 2 - rendered.get_width() // 2
                self.screen.blit(shadow_r, (cx + 2, 202))
                self.screen.blit(rendered, (cx, 200))
            else:
                self.show_level_up = False

    def draw_game_over(self):
        if not self.score_panel_shown:
            return

        self.screen.blit(self.game_over_screen, (0, 0))

        font_med = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        font_label = pygame.font.Font(None, 22)
        font_tiny = pygame.font.Font(None, 18)

        panel_rect = pygame.Rect(34, 130, 220, 120)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel_rect, 2)

        inner = panel_rect.inflate(-8, -8)
        pygame.draw.rect(self.screen, PANEL_INNER, inner)

        label = font_label.render("SCORE", True, TEXT_DIM)
        self.screen.blit(label, (55, 140))

        score_text = font_med.render(str(self.score), True, BRIGHT_WHITE)
        self.screen.blit(score_text, (70, 170))

        best_label = font_label.render("BEST", True, TEXT_DIM)
        self.screen.blit(best_label, (170, 140))

        hs = self.save_data.get("high_score", 0)
        best_text = font_med.render(str(hs), True, GOLD)
        self.screen.blit(best_text, (175, 170))

        if self.score > 0:
            medal = create_medal(self.score)
            self.screen.blit(medal, (44, 158))

        if self.score == hs and self.score > 0:
            new_text = font_small.render("NEW!", True, BRIGHT_RED)
            self.screen.blit(new_text, (195, 195))

        pygame.draw.line(self.screen, PANEL_BORDER, (60, 235), (230, 235), 2)

        button_rect = pygame.Rect(88, 250, 112, 40)
        draw_button(self.screen, button_rect, "PLAY", font_small, BUTTON_GREEN, BUTTON_GREEN_DARK)

        home_rect = pygame.Rect(88, 380, 112, 32)
        draw_button(self.screen, home_rect, "HOME", font_small, BUTTON_BLUE, BUTTON_BLUE_DARK)

        sprite_label = font_tiny.render("Bird:", True, TEXT_DIM)
        self.screen.blit(sprite_label, (20, 300))

        num_birds = min(len(BIRD_NAMES), 8)
        spacing = min(30, (SCREEN_WIDTH - 40) // num_birds)
        start_x = (SCREEN_WIDTH - num_birds * spacing) // 2

        for i in range(num_birds):
            x = start_x + i * spacing
            y = 295
            bird = create_bird(0, i)
            bird_small = pygame.transform.scale(bird, (20, 15))

            if i in self.unlocked_birds:
                if i == self.selected_bird:
                    pygame.draw.rect(self.screen, GOLD, (x - 2, y - 2, 24, 19), 2)
                self.screen.blit(bird_small, (x, y))
            else:
                pygame.draw.rect(self.screen, (60, 60, 70), (x, y, 20, 15))
                pygame.draw.rect(self.screen, PANEL_BORDER, (x, y, 20, 15), 1)
                lock_text = font_tiny.render("?", True, TEXT_DIM)
                self.screen.blit(lock_text, (x + 8, y + 2))

        draw_text_centered(self.screen, "Tap to play again", font_small, BRIGHT_WHITE, 330)

    def draw_sprite_select(self):
        if self.sprite_select_cache is None:
            self.sprite_select_cache = self._build_sprite_select()
        self.screen.blit(self.sprite_select_cache, (0, 0))

    def _build_sprite_select(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))

        font_title = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 28)
        font_tiny = pygame.font.Font(None, 20)

        draw_text_centered(surf, "Select Bird", font_title, BRIGHT_WHITE, 60)

        num_birds = len(BIRD_NAMES)
        for i in range(num_birds):
            x = 60 + (i % 2) * 100
            y = 110 + (i // 2) * 70

            box = pygame.Rect(x - 5, y - 5, 50, 40)
            if i == self.selected_bird:
                pygame.draw.rect(surf, GOLD, box, 3)
            else:
                pygame.draw.rect(surf, PANEL_BORDER, box, 2)

            bird_sprite = create_bird(0, i)
            surf.blit(bird_sprite, (x, y))

            name = font_small.render(BIRD_NAMES[i], True, BRIGHT_WHITE)
            surf.blit(name, (x + 16 - name.get_width()//2, y + 30))

            if i not in self.unlocked_birds:
                price = BIRD_PRICES[i]
                if price > 0:
                    lock = font_tiny.render(f"{price} coins", True, GOLD)
                    surf.blit(lock, (x + 16 - lock.get_width()//2, y + 46))

        hint = font_small.render("Click to select, ESC back", True, TEXT_DIM)
        surf.blit(hint, (144 - hint.get_width()//2, 460))

        return surf

    def draw_shop(self):
        self.shop_surface, self.shop_buy_rect = create_shop_screen(
            self.shop_tab, self.shop_selected, self.coins,
            self.unlocked_birds if self.shop_tab == 0 else self.unlocked_bgs
        )
        self.screen.blit(self.shop_surface, (0, 0))

    def draw_rebirth(self):
        self.rebirth_surface, self.rebirth_do_rect, self.rebirth_cancel_rect = create_rebirth_screen(
            self.rebirth_count, self.coin_multiplier, self.player_level, REBIRTH_LEVEL_REQ
        )
        self.screen.blit(self.rebirth_surface, (0, 0))

    def draw_settings(self):
        if self.settings_surface is None:
            self.settings_surface, self.settings_back_rect, self.settings_sliders, \
                self.settings_qual_buttons, self.settings_toggles, self.settings_reset_rect = \
                create_settings_screen(self.settings)
        self.screen.blit(self.settings_surface, (0, 0))

    def run(self):
        while True:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = FlappyBird()
    game.run()
