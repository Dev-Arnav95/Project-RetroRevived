# PyBird

A retro Flappy Bird clone reimagined in pygame with modern progression systems.

## Features

- **EXP Leveling** — Earn experience while playing, level up through 10 tiers
- **Coin Shop** — Buy 8 unique bird skins and 6 backgrounds
- **Rebirth System** — Reset progress at Level 10 for permanent coin multipliers
- **Settings Panel** — Volume sliders, quality presets, screen shake, FPS counter
- **Subway Surfers-style Difficulty** — Smooth ramp based on survival time, not score
- **16-frame Rainbow Bird** — Smooth gradient color cycling through the full spectrum

## Quick Start

### Run from Source

```bash
# Install dependencies
pip install pygame

# Run the game
python PyBird/flappy.py
```

### Install Packages

| Platform | Package | Install |
|----------|---------|---------|
| Debian/Ubuntu | `pybird_1.0_amd64.deb` | `sudo dpkg -i pybird_1.0_amd64.deb` |
| Arch Linux | `pybird-1.0-1-any.pkg.tar.zst` | `sudo pacman -U pybird-1.0-1-any.pkg.tar.zst` |
| Linux (standalone) | `PyBird_linux_x64_standalone` | `chmod +x PyBird_linux_x64_standalone && ./PyBird_linux_x64_standalone` |
| macOS | `PyBird_macOS.zip` | Unzip, right-click `.app` → Open |

## Controls

| Input | Action |
|-------|--------|
| Click / Space / Enter | Flap |
| Escape | Pause |
| Mouse | Navigate menus |

## Project Structure

```
Project-RetroRevived/
├── PyBird/                    # Source code
│   ├── flappy.py              # Game logic
│   ├── sprites.py             # Procedural sprites & UI
│   ├── flappybird.png         # App icon
│   ├── save_data.json         # Progress (auto-created)
│   └── settings.json          # Settings (auto-created)
├── PreBuilts/
│   └── PyBird/
│       ├── pybird_1.0_amd64.deb
│       ├── pybird-1.0-1-any.pkg.tar.zst
│       ├── PyBird_linux_x64_standalone
│       └── PyBird_macOS.zip
├── LICENSE                    # MIT License
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).
