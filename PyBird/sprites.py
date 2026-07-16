import pygame
import math


BIRD_NAMES = ["Classic", "Red", "Blue", "Purple", "Golden", "Zombie", "Blush", "Rainbow"]
BIRD_PRICES = [0, 0, 0, 0, 50, 30, 25, 75]

BG_NAMES = ["Day", "Sunset", "Night", "Storm", "Autumn", "Space"]
BG_PRICES = [0, 20, 30, 35, 25, 40]

BRIGHT_WHITE = (255, 255, 255)
SHADOW_BLACK = (10, 10, 10)
GOLD = (255, 215, 0)
GOLD_DARK = (200, 170, 0)
BRIGHT_GREEN = (100, 255, 100)
BRIGHT_RED = (255, 80, 80)
BRIGHT_CYAN = (100, 255, 255)
BRIGHT_YELLOW = (255, 255, 100)
PANEL_BG = (40, 35, 50)
PANEL_BORDER = (100, 90, 120)
PANEL_INNER = (55, 50, 70)
BUTTON_GREEN = (60, 180, 80)
BUTTON_GREEN_DARK = (40, 140, 60)
BUTTON_RED = (200, 70, 70)
BUTTON_RED_DARK = (160, 50, 50)
BUTTON_BLUE = (70, 130, 200)
BUTTON_BLUE_DARK = (50, 100, 160)
BUTTON_GRAY = (90, 85, 100)
BUTTON_GRAY_DARK = (70, 65, 80)
TEXT_DIM = (170, 170, 180)
SLIDER_TRACK = (60, 55, 75)
SLIDER_FILL = (100, 200, 120)
SLIDER_HANDLE = BRIGHT_WHITE
TOGGLE_ON = (80, 200, 100)
TOGGLE_OFF = (80, 70, 90)


def draw_text_with_shadow(surface, text, font, color, pos, shadow_color=SHADOW_BLACK, offset=2):
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (pos[0] + offset, pos[1] + offset))
    main = font.render(text, True, color)
    surface.blit(main, pos)
    return main.get_width()


def draw_text_centered(surface, text, font, color, y, screen_width=288, shadow=True):
    rendered = font.render(text, True, color)
    x = screen_width // 2 - rendered.get_width() // 2
    if shadow:
        s = font.render(text, True, SHADOW_BLACK)
        surface.blit(s, (x + 2, y + 2))
    surface.blit(rendered, (x, y))
    return rendered.get_width()


def draw_button(surface, rect, text, font, bg_color, border_color, text_color=BRIGHT_WHITE, hovered=False):
    if hovered:
        lighter = tuple(min(255, c + 30) for c in bg_color)
        pygame.draw.rect(surface, lighter, rect)
    else:
        pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    tw = font.render(text, True, text_color)
    surface.blit(tw, (rect.centerx - tw.get_width() // 2, rect.centery - tw.get_height() // 2))


def create_coin_icon(size=14):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    r = size // 2 - 1
    cx, cy = size // 2, size // 2
    pygame.draw.circle(icon, GOLD, (cx, cy), r)
    pygame.draw.circle(icon, GOLD_DARK, (cx, cy), r, 2)
    if size >= 12:
        f = pygame.font.Font(None, max(10, size - 2))
        c = f.render("c", True, GOLD_DARK)
        icon.blit(c, (cx - c.get_width() // 2, cy - c.get_height() // 2))
    return icon


def create_bird(frame=0, bird_type=0):
    bird = pygame.Surface((48, 36), pygame.SRCALPHA)

    bird_colors = [
        {"body": (255, 200, 50), "dark": (200, 150, 30), "belly": (255, 230, 100), "wing": (220, 170, 40), "wing_d": (180, 130, 20)},
        {"body": (255, 120, 70), "dark": (200, 80, 40), "belly": (255, 170, 130), "wing": (220, 100, 50), "wing_d": (180, 70, 30)},
        {"body": (100, 180, 255), "dark": (60, 130, 200), "belly": (160, 210, 255), "wing": (70, 150, 220), "wing_d": (50, 120, 180)},
        {"body": (170, 120, 255), "dark": (130, 80, 200), "belly": (200, 160, 255), "wing": (140, 100, 220), "wing_d": (110, 70, 180)},
        {"body": (255, 215, 0), "dark": (200, 170, 0), "belly": (255, 240, 100), "wing": (230, 190, 20), "wing_d": (190, 150, 0)},
        {"body": (120, 160, 80), "dark": (80, 120, 50), "belly": (150, 190, 110), "wing": (100, 140, 65), "wing_d": (70, 110, 40)},
        {"body": (255, 150, 180), "dark": (220, 100, 140), "belly": (255, 200, 220), "wing": (240, 130, 160), "wing_d": (200, 90, 130)},
    ]
    if bird_type == 7:
        num_frames = 16
        rainbow_stops = [
            (255, 80, 80),
            (255, 160, 40),
            (255, 230, 50),
            (80, 220, 80),
            (50, 180, 160),
            (80, 140, 255),
            (140, 80, 230),
            (220, 80, 200),
            (255, 80, 80),
        ]
        t = (frame % num_frames) / num_frames
        seg = t * (len(rainbow_stops) - 1)
        idx = int(seg)
        frac = seg - idx
        c1 = rainbow_stops[idx]
        c2 = rainbow_stops[min(idx + 1, len(rainbow_stops) - 1)]
        body = tuple(int(c1[i] + (c2[i] - c1[i]) * frac) for i in range(3))
        dark = tuple(max(0, c - 50) for c in body)
        belly = tuple(min(255, c + 40) for c in body)
        wing = tuple(max(0, c - 20) for c in body)
        wing_d = tuple(max(0, c - 60) for c in body)
        c = {"body": body, "dark": dark, "belly": belly, "wing": wing, "wing_d": wing_d}
    else:
        c = bird_colors[bird_type % len(bird_colors)]

    pygame.draw.rect(bird, c["body"], (6, 6, 28, 22))
    pygame.draw.rect(bird, c["dark"], (6, 6, 28, 22), 2)
    pygame.draw.rect(bird, c["belly"], (12, 14, 16, 10))
    wing_y = [8, 5, 11][frame % 3]
    pygame.draw.rect(bird, c["wing"], (8, wing_y, 14, 12))
    pygame.draw.rect(bird, c["wing_d"], (8, wing_y, 14, 12), 2)
    pygame.draw.rect(bird, (255, 255, 255), (28, 8, 10, 10))
    pygame.draw.rect(bird, (0, 0, 0), (32, 8, 5, 10))
    pygame.draw.rect(bird, (255, 255, 255), (33, 10, 2, 3))
    pygame.draw.rect(bird, (255, 100, 50), (36, 14, 12, 6))
    pygame.draw.rect(bird, (200, 80, 30), (36, 18, 12, 6))

    if bird_type == 4:
        for sx, sy in [(8, 8), (20, 12), (28, 18)]:
            pygame.draw.rect(bird, (255, 255, 200, 180), (sx, sy, 3, 3))

    return bird


def create_pipe(surface_width, gap_y, gap_size, screen_height):
    pipe_width = 52
    cap_height = 24
    cap_width = 58
    cap_offset = (cap_width - pipe_width) // 2

    top_pipe = pygame.Surface((cap_width, gap_y), pygame.SRCALPHA)
    pygame.draw.rect(top_pipe, (80, 200, 80), (cap_offset, 0, pipe_width, gap_y - cap_height))
    pygame.draw.rect(top_pipe, (80, 200, 80), (0, gap_y - cap_height, cap_width, cap_height))
    for y in range(0, gap_y - cap_height, 8):
        pygame.draw.rect(top_pipe, (100, 230, 100), (cap_offset + 2, y, 6, 8))
    for y in range(0, cap_height, 8):
        pygame.draw.rect(top_pipe, (100, 230, 100), (2, gap_y - cap_height + y, 6, 8))
    for y in range(0, gap_y - cap_height, 8):
        pygame.draw.rect(top_pipe, (60, 160, 60), (cap_width - cap_offset - 8, y, 6, 8))
    for y in range(0, cap_height, 8):
        pygame.draw.rect(top_pipe, (60, 160, 60), (cap_width - 8, gap_y - cap_height + y, 6, 8))
    pygame.draw.rect(top_pipe, (50, 130, 50), (0, gap_y - cap_height, cap_width, cap_height), 2)
    pygame.draw.rect(top_pipe, (50, 130, 50), (cap_offset, 0, pipe_width, gap_y - cap_height), 2)

    bottom_start = gap_y + gap_size
    bottom_height = screen_height - bottom_start
    bottom_pipe = pygame.Surface((cap_width, bottom_height), pygame.SRCALPHA)
    pygame.draw.rect(bottom_pipe, (80, 200, 80), (cap_offset, cap_height, pipe_width, bottom_height - cap_height))
    pygame.draw.rect(bottom_pipe, (80, 200, 80), (0, 0, cap_width, cap_height))
    for y in range(cap_height, bottom_height, 8):
        pygame.draw.rect(bottom_pipe, (100, 230, 100), (cap_offset + 2, y, 6, 8))
    for y in range(0, cap_height, 8):
        pygame.draw.rect(bottom_pipe, (100, 230, 100), (2, y, 6, 8))
    for y in range(cap_height, bottom_height, 8):
        pygame.draw.rect(bottom_pipe, (60, 160, 60), (cap_width - cap_offset - 8, y, 6, 8))
    for y in range(0, cap_height, 8):
        pygame.draw.rect(bottom_pipe, (60, 160, 60), (cap_width - 8, y, 6, 8))
    pygame.draw.rect(bottom_pipe, (50, 130, 50), (0, 0, cap_width, cap_height), 2)
    pygame.draw.rect(bottom_pipe, (50, 130, 50), (cap_offset, cap_height, pipe_width, bottom_height - cap_height), 2)

    return top_pipe, bottom_pipe, cap_width, gap_size


def create_background(screen_width, screen_height, bg_id=0):
    bg = pygame.Surface((screen_width, screen_height))
    gradients = {
        0: ((78, 192, 200), (135, 206, 230)),
        1: ((255, 140, 50), (200, 100, 150)),
        2: ((20, 30, 80), (40, 50, 100)),
        3: ((60, 70, 80), (80, 100, 80)),
        4: ((180, 120, 60), (200, 160, 100)),
        5: ((60, 20, 100), (20, 10, 40)),
    }
    top, bottom = gradients.get(bg_id, gradients[0])
    for y in range(screen_height):
        ratio = y / screen_height
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        pygame.draw.line(bg, (r, g, b), (0, y), (screen_width, y))
    return bg


def create_background_with_stars(screen_width, screen_height, bg_id):
    bg = create_background(screen_width, screen_height, bg_id)
    if bg_id in (2, 5):
        import random
        rng = random.Random(42)
        for _ in range(40):
            sx = rng.randint(0, screen_width - 2)
            sy = rng.randint(0, screen_height // 2)
            brightness = rng.randint(180, 255)
            size = rng.choice([1, 1, 1, 2])
            pygame.draw.rect(bg, (brightness, brightness, brightness), (sx, sy, size, size))
    return bg


def create_city_skyline(screen_width):
    skyline = pygame.Surface((screen_width * 2, 120), pygame.SRCALPHA)
    building_color = (90, 170, 90)
    dark_color = (70, 140, 70)

    buildings = [
        (0, 60, 40, 60), (35, 40, 30, 80), (60, 55, 25, 65),
        (80, 35, 35, 85), (110, 50, 28, 70), (133, 45, 32, 75),
        (160, 55, 25, 65), (180, 30, 40, 90), (215, 50, 30, 70),
        (240, 40, 35, 80), (270, 55, 28, 65), (293, 45, 32, 75),
        (320, 35, 30, 85), (345, 50, 35, 70), (375, 42, 28, 78),
        (398, 55, 32, 65), (425, 38, 30, 82), (450, 48, 35, 72),
        (480, 55, 28, 65), (503, 42, 32, 78), (530, 35, 35, 85),
        (560, 50, 28, 70), (585, 40, 35, 80), (615, 55, 30, 65),
        (640, 35, 40, 85), (675, 48, 28, 72), (700, 55, 32, 65),
    ]

    for x, y, w, h in buildings:
        pygame.draw.rect(skyline, building_color, (x, 120 - h, w, h))
        pygame.draw.rect(skyline, dark_color, (x, 120 - h, w, h), 1)
        for wy in range(120 - h + 4, 116, 10):
            for wx in range(x + 4, x + w - 4, 10):
                if wy < 118:
                    pygame.draw.rect(skyline, (200, 230, 255), (wx, wy, 5, 6))

    return skyline


def create_ground(screen_width):
    ground = pygame.Surface((screen_width * 2, 112))
    ground.fill((222, 216, 149))
    pygame.draw.rect(ground, (180, 170, 110), (0, 0, screen_width * 2, 4))
    pygame.draw.rect(ground, (212, 196, 119), (0, 0, screen_width * 2, 2))
    for x in range(0, screen_width * 2, 16):
        pygame.draw.rect(ground, (195, 185, 125), (x, 6, 8, 8))
        pygame.draw.rect(ground, (185, 175, 115), (x + 8, 14, 8, 8))
    return ground


def create_get_ready_screen():
    surf = pygame.Surface((288, 512), pygame.SRCALPHA)
    font_big = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 36)
    draw_text_centered(surf, "Get Ready!", font_big, BRIGHT_WHITE, 120)
    draw_text_centered(surf, "TAP TO START", font_small, BRIGHT_YELLOW, 240)
    return surf


def create_game_over_screen():
    surf = pygame.Surface((288, 512), pygame.SRCALPHA)
    overlay = pygame.Surface((288, 512), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surf.blit(overlay, (0, 0))
    font_big = pygame.font.Font(None, 56)
    draw_text_centered(surf, "Game Over", font_big, BRIGHT_RED, 80)
    return surf


def create_medal(score):
    surf = pygame.Surface((44, 44), pygame.SRCALPHA)
    if score >= 40:
        color = (255, 215, 0)
    elif score >= 30:
        color = (192, 192, 192)
    elif score >= 20:
        color = (205, 127, 50)
    else:
        return surf

    pygame.draw.rect(surf, color, (4, 4, 36, 36))
    pygame.draw.rect(surf, SHADOW_BLACK, (4, 4, 36, 36), 2)
    pygame.draw.rect(surf, (255, 255, 255, 100), (8, 8, 12, 12))
    font = pygame.font.Font(None, 28)
    star = font.render("*", True, BRIGHT_WHITE)
    surf.blit(star, (22 - star.get_width()//2, 22 - star.get_height()//2))
    return surf


def create_shop_screen(tab, selected_item, player_coins, unlocked_items, screen_width=288, screen_height=512):
    surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surf.blit(overlay, (0, 0))

    font_title = pygame.font.Font(None, 42)
    font_med = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 22)
    font_tiny = pygame.font.Font(None, 18)

    draw_text_centered(surf, "SHOP", font_title, GOLD, 10, screen_width)

    coin_icon = create_coin_icon(16)
    surf.blit(coin_icon, (screen_width - 90, 12))
    coin_shadow = font_med.render(str(player_coins), True, SHADOW_BLACK)
    surf.blit(coin_shadow, (screen_width - 70, 14))
    coin_text = font_med.render(str(player_coins), True, GOLD)
    surf.blit(coin_text, (screen_width - 72, 12))

    if tab == 0:
        names = BIRD_NAMES
        prices = BIRD_PRICES
        if 0 <= selected_item < len(names):
            preview_bird = create_bird(0, selected_item)
            big_bird = pygame.transform.scale(preview_bird, (96, 72))
            preview_y = 60

            box_rect = pygame.Rect(screen_width // 2 - 52, preview_y + 20, 104, 80)
            pygame.draw.rect(surf, PANEL_BG, box_rect)
            pygame.draw.rect(surf, PANEL_BORDER, box_rect, 2)
            surf.blit(big_bird, (screen_width // 2 - 48, preview_y + 30))

            draw_text_centered(surf, names[selected_item], font_med, BRIGHT_WHITE, preview_y + 108, screen_width, False)

            if selected_item in unlocked_items:
                draw_text_centered(surf, "OWNED", font_small, BRIGHT_GREEN, preview_y + 132, screen_width, False)
            else:
                draw_text_centered(surf, f"{prices[selected_item]} coins", font_small, GOLD, preview_y + 132, screen_width, False)
    else:
        names = BG_NAMES
        prices = BG_PRICES
        if 0 <= selected_item < len(names):
            preview_bg = create_background(200, 100, selected_item)
            preview_y = 60
            bg_rect = pygame.Rect(screen_width // 2 - 102, preview_y + 18, 204, 104)
            pygame.draw.rect(surf, PANEL_BG, bg_rect)
            pygame.draw.rect(surf, PANEL_BORDER, bg_rect, 2)
            surf.blit(preview_bg, (screen_width // 2 - 100, preview_y + 20))

            draw_text_centered(surf, names[selected_item], font_med, BRIGHT_WHITE, preview_y + 128, screen_width, False)

            if selected_item in unlocked_items:
                draw_text_centered(surf, "OWNED", font_small, BRIGHT_GREEN, preview_y + 152, screen_width, False)
            else:
                draw_text_centered(surf, f"{prices[selected_item]} coins", font_small, GOLD, preview_y + 152, screen_width, False)

    tab_y = 240
    tab_w = 120
    tab_h = 28
    tab_gap = 8
    tab_start_x = (screen_width - (tab_w * 2 + tab_gap)) // 2

    for i, label in enumerate(["Skins", "Backgrounds"]):
        tx = tab_start_x + i * (tab_w + tab_gap)
        if i == tab:
            pygame.draw.rect(surf, GOLD, (tx, tab_y, tab_w, tab_h))
            text_color = SHADOW_BLACK
        else:
            pygame.draw.rect(surf, BUTTON_GRAY, (tx, tab_y, tab_w, tab_h))
            text_color = BRIGHT_WHITE
        pygame.draw.rect(surf, PANEL_BORDER, (tx, tab_y, tab_w, tab_h), 1)
        tab_text = font_small.render(label, True, text_color)
        surf.blit(tab_text, (tx + tab_w // 2 - tab_text.get_width() // 2, tab_y + 5))

    items_y = 280
    item_w = 58
    item_h = 68
    item_gap = 6
    items_per_row = 4
    total_items_w = items_per_row * item_w + (items_per_row - 1) * item_gap
    items_start_x = (screen_width - total_items_w) // 2

    for i, name in enumerate(names):
        row = i // items_per_row
        col = i % items_per_row
        ix = items_start_x + col * (item_w + item_gap)
        iy = items_y + row * (item_h + item_gap)

        if i == selected_item:
            pygame.draw.rect(surf, GOLD, (ix - 2, iy - 2, item_w + 4, item_h + 4), 2)

        if i in unlocked_items:
            pygame.draw.rect(surf, (50, 80, 50), (ix, iy, item_w, item_h))
        else:
            pygame.draw.rect(surf, (40, 40, 50), (ix, iy, item_w, item_h))
        pygame.draw.rect(surf, PANEL_BORDER, (ix, iy, item_w, item_h), 1)

        if tab == 0:
            thumb = create_bird(0, i)
            thumb_small = pygame.transform.scale(thumb, (32, 24))
            surf.blit(thumb_small, (ix + item_w // 2 - 16, iy + 4))
        else:
            thumb = create_background(item_w - 8, 28, i)
            surf.blit(thumb, (ix + 4, iy + 4))

        name_t = font_tiny.render(name[:7], True, BRIGHT_WHITE)
        surf.blit(name_t, (ix + item_w // 2 - name_t.get_width() // 2, iy + 34))

        if i in unlocked_items:
            ok_t = font_tiny.render("OK", True, BRIGHT_GREEN)
            surf.blit(ok_t, (ix + item_w // 2 - ok_t.get_width() // 2, iy + 50))
        else:
            price_t = font_tiny.render(str(prices[i]), True, GOLD)
            surf.blit(price_t, (ix + item_w // 2 - price_t.get_width() // 2, iy + 50))

    buy_y = 440
    buy_w = 140
    buy_h = 32
    buy_x = screen_width // 2 - buy_w // 2
    buy_rect = pygame.Rect(buy_x, buy_y, buy_w, buy_h)

    can_buy = (selected_item not in unlocked_items and
               player_coins >= prices[selected_item] and
               prices[selected_item] > 0)

    if selected_item in unlocked_items:
        draw_button(surf, buy_rect, "SELECT", font_med, BUTTON_GRAY, BUTTON_GRAY_DARK, TEXT_DIM)
    elif can_buy:
        draw_button(surf, buy_rect, f"BUY {prices[selected_item]}", font_med, BUTTON_GREEN, BUTTON_GREEN_DARK)
    else:
        draw_button(surf, buy_rect, f"BUY {prices[selected_item]}", font_med, BUTTON_RED, BUTTON_RED_DARK, (180, 120, 120))

    esc_text = font_tiny.render("ESC - Back", True, TEXT_DIM)
    surf.blit(esc_text, (screen_width // 2 - esc_text.get_width() // 2, screen_height - 20))

    return surf, buy_rect


def create_pause_screen():
    surf = pygame.Surface((288, 512), pygame.SRCALPHA)
    overlay = pygame.Surface((288, 512), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))

    font_big = pygame.font.Font(None, 56)
    font_med = pygame.font.Font(None, 32)

    draw_text_centered(surf, "PAUSED", font_big, BRIGHT_WHITE, 160)

    resume_rect = pygame.Rect(88, 240, 112, 40)
    draw_button(surf, resume_rect, "Resume", font_med, BUTTON_GREEN, BUTTON_GREEN_DARK)

    menu_rect = pygame.Rect(88, 300, 112, 40)
    draw_button(surf, menu_rect, "Menu", font_med, BUTTON_RED, BUTTON_RED_DARK)

    return surf, resume_rect, menu_rect


def create_rebirth_screen(rebirth_count, coin_multiplier, player_level, required_level, screen_width=288, screen_height=512):
    surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surf.blit(overlay, (0, 0))

    font_big = pygame.font.Font(None, 48)
    font_med = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 22)
    font_tiny = pygame.font.Font(None, 18)

    draw_text_centered(surf, "REBIRTH", font_big, (255, 100, 255), 40, screen_width)

    info_y = 100
    draw_text_centered(surf, f"Rebirths: {rebirth_count}", font_med, GOLD, info_y, screen_width, False)
    draw_text_centered(surf, f"Coin Multiplier: x{coin_multiplier:.1f}", font_med, BRIGHT_GREEN, info_y + 35, screen_width, False)

    stat_y = 200
    panel = pygame.Rect(30, stat_y, screen_width - 60, 120)
    pygame.draw.rect(surf, PANEL_BG, panel)
    pygame.draw.rect(surf, PANEL_BORDER, panel, 2)

    draw_text_centered(surf, "Resets:", font_small, TEXT_DIM, stat_y + 10, screen_width, False)
    draw_text_centered(surf, "Level, EXP, Coins, Skins", font_tiny, BRIGHT_RED, stat_y + 35, screen_width, False)

    draw_text_centered(surf, "Keeps:", font_small, TEXT_DIM, stat_y + 60, screen_width, False)
    draw_text_centered(surf, "High Score, Rebirth Count", font_tiny, BRIGHT_GREEN, stat_y + 85, screen_width, False)

    req_y = 340
    can_rebirth = player_level >= required_level
    draw_text_centered(surf, f"Required: Level {required_level}", font_small, BRIGHT_YELLOW, req_y, screen_width, False)
    draw_text_centered(surf, f"Your Level: {player_level}", font_med, BRIGHT_GREEN if can_rebirth else BRIGHT_RED, req_y + 28, screen_width, False)

    do_rect = pygame.Rect(54, 400, 180, 44)
    if can_rebirth:
        draw_button(surf, do_rect, "REBIRTH!", font_big, (180, 60, 200), (140, 40, 160))
    else:
        draw_button(surf, do_rect, "REBIRTH!", font_big, BUTTON_GRAY, BUTTON_GRAY_DARK, (120, 120, 120))

    cancel_rect = pygame.Rect(88, 460, 112, 32)
    draw_button(surf, cancel_rect, "Cancel", font_small, BUTTON_RED, BUTTON_RED_DARK)

    return surf, do_rect, cancel_rect


def draw_gear(surface, cx, cy, size=10, color=(200, 200, 210)):
    bg_r = size + 4
    bg_color = (50, 45, 65)
    border_color = (90, 85, 105)
    pygame.draw.circle(surface, bg_color, (cx, cy), bg_r)
    pygame.draw.circle(surface, border_color, (cx, cy), bg_r, 2)

    r_outer = size * 0.8
    r_inner = size * 0.45
    r_hole = size * 0.22
    teeth = 8
    for i in range(teeth):
        angle = i * (2 * math.pi / teeth)
        x1 = cx + r_outer * math.cos(angle)
        y1 = cy + r_outer * math.sin(angle)
        x2 = cx + r_outer * math.cos(angle + 0.35)
        y2 = cy + r_outer * math.sin(angle + 0.35)
        x3 = cx + r_inner * math.cos(angle + 0.5)
        y3 = cy + r_inner * math.sin(angle + 0.5)
        x4 = cx + r_inner * math.cos(angle - 0.15)
        y4 = cy + r_inner * math.sin(angle - 0.15)
        pygame.draw.polygon(surface, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    pygame.draw.circle(surface, color, (int(cx), int(cy)), int(r_inner))
    pygame.draw.circle(surface, bg_color, (int(cx), int(cy)), int(r_hole))


def create_settings_screen(settings, screen_width=288, screen_height=512):
    surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surf.blit(overlay, (0, 0))

    font_title = pygame.font.Font(None, 36)
    font_med = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 20)
    font_tiny = pygame.font.Font(None, 16)

    panel_x = 24
    panel_y = 40
    panel_w = screen_width - 48
    panel_h = 420
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    pygame.draw.rect(surf, PANEL_BG, panel_rect)
    pygame.draw.rect(surf, PANEL_BORDER, panel_rect, 2)

    draw_text_centered(surf, "SETTINGS", font_title, GOLD, panel_y + 8, screen_width)

    back_rect = pygame.Rect(panel_x + 8, panel_y + 36, 80, 24)
    draw_button(surf, back_rect, "BACK", font_med, BUTTON_RED, BUTTON_RED_DARK)

    slider_x = panel_x + 30
    slider_w = panel_w - 60
    slider_h = 8
    handle_r = 7
    sliders = {}
    slider_defs = [
        ("master_vol", "Master", settings.get("master_vol", 1.0)),
        ("bird_sfx_vol", "Bird SFX", settings.get("bird_sfx_vol", 1.0)),
        ("point_sfx_vol", "Point SFX", settings.get("point_sfx_vol", 1.0)),
        ("ui_sfx_vol", "UI SFX", settings.get("ui_sfx_vol", 1.0)),
    ]

    sy = panel_y + 70
    for key, label, val in slider_defs:
        label_t = font_small.render(f"{label}:", True, BRIGHT_WHITE)
        surf.blit(label_t, (slider_x, sy))

        val_t = font_tiny.render(f"{int(val * 100)}%", True, GOLD)
        surf.blit(val_t, (slider_x + slider_w - val_t.get_width(), sy))

        track_y = sy + 20
        track_rect = pygame.Rect(slider_x, track_y, slider_w, slider_h)
        pygame.draw.rect(surf, SLIDER_TRACK, track_rect)
        fill_w = int(slider_w * val)
        if fill_w > 0:
            pygame.draw.rect(surf, SLIDER_FILL, (slider_x, track_y, fill_w, slider_h))
        pygame.draw.rect(surf, PANEL_BORDER, track_rect, 1)

        handle_x = slider_x + fill_w
        handle_y = track_y + slider_h // 2
        pygame.draw.circle(surf, SLIDER_HANDLE, (handle_x, handle_y), handle_r)
        pygame.draw.circle(surf, PANEL_BORDER, (handle_x, handle_y), handle_r, 1)

        sliders[key] = pygame.Rect(slider_x, track_y - 4, slider_w, slider_h + 8)

        sy += 50

    q_label = font_small.render("Quality:", True, BRIGHT_WHITE)
    surf.blit(q_label, (slider_x, sy))
    sy += 20

    qual_names = ["Low", "Med", "High"]
    qual_keys = ["low", "medium", "high"]
    btn_w = 60
    btn_gap = 8
    total_qw = 3 * btn_w + 2 * btn_gap
    qx_start = slider_x + (slider_w - total_qw) // 2
    qual_buttons = {}
    current_q = settings.get("quality", "medium")

    for i, (name, key) in enumerate(zip(qual_names, qual_keys)):
        bx = qx_start + i * (btn_w + btn_gap)
        btn_rect = pygame.Rect(bx, sy, btn_w, 24)
        if key == current_q:
            draw_button(surf, btn_rect, name, font_med, BUTTON_GREEN, BUTTON_GREEN_DARK)
        else:
            draw_button(surf, btn_rect, name, font_med, BUTTON_GRAY, BUTTON_GRAY_DARK)
        qual_buttons[key] = btn_rect

    sy += 38

    toggles = {}
    toggle_defs = [
        ("screen_shake", "Screen Shake", settings.get("screen_shake", True)),
        ("show_fps", "Show FPS", settings.get("show_fps", False)),
    ]

    for key, label, val in toggle_defs:
        label_t = font_small.render(f"{label}:", True, BRIGHT_WHITE)
        surf.blit(label_t, (slider_x, sy))

        toggle_x = slider_x + slider_w - 40
        toggle_y = sy + 2
        toggle_rect = pygame.Rect(toggle_x, toggle_y, 36, 18)
        if val:
            pygame.draw.rect(surf, TOGGLE_ON, toggle_rect)
            knob_x = toggle_x + 20
        else:
            pygame.draw.rect(surf, TOGGLE_OFF, toggle_rect)
            knob_x = toggle_x + 3
        pygame.draw.rect(surf, PANEL_BORDER, toggle_rect, 1)
        pygame.draw.circle(surf, BRIGHT_WHITE, (knob_x, toggle_y + 9), 7)

        state_t = font_tiny.render("ON" if val else "OFF", True, TOGGLE_ON if val else TEXT_DIM)
        surf.blit(state_t, (toggle_x - 30, sy + 2))

        toggles[key] = toggle_rect
        sy += 30

    reset_rect = pygame.Rect(slider_x, panel_y + panel_h - 40, slider_w, 28)
    draw_button(surf, reset_rect, "Reset All Settings", font_med, BUTTON_RED, BUTTON_RED_DARK)

    return surf, back_rect, sliders, qual_buttons, toggles, reset_rect
