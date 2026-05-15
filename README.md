# Mind Heist: Neural Hacker

A cyberpunk arcade puzzle game where you navigate through a human brain, steal memories, avoid immune defenses, and solve neural puzzles using hacking abilities.

This repository also includes a production-ready **AI stock signal backend** in `backend/` (FastAPI + Postgres + Redis + Discord alerts).

---

## Features

- **4 Progressive Levels** – Surface Thoughts → Emotional Core → Subconscious → Trauma Vault
- **3 Enemy Types** – Firewall Waves, Immune Bots (chase AI), Corruption Zones (damage-over-time)
- **4 Special Abilities** – Pulse Dash, Cloak, Memory Pull, Overclock
- **Procedural Neural Graphs** – Different neural layout every playthrough (powered by NetworkX)
- **Neon Cyberpunk Visuals** – Glowing particles, animated menu, HUD bars, event log
- **Score System** – Fragments, time bonuses, and level-difficulty multipliers

---

## Installation

```bash
pip install -r requirements.txt
```

**Dependencies:**

| Library | Purpose |
|---------|---------|
| pygame 2.5.2 | Game engine, rendering, events |
| networkx 3.2 | Neural graph generation |
| numpy 1.24.3 | Math calculations |
| pygame-gui 0.6.9 | UI components |

---

## How to Play

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| W / A / S / D | Move up / left / down / right |
| Arrow Keys | Alternative movement |
| Q | **Pulse Dash** – teleport 150 px in movement direction |
| E | **Cloak** – become invisible for 3 seconds |
| R | **Memory Pull** – attract memory fragments within 200 px |
| F | **Overclock** – slow time to 0.5× speed for 2 seconds |
| ESC | Pause / Resume |
| ENTER | Confirm / Advance level |

### Objective

Collect all **memory fragments** (glowing yellow circles) in each level without being destroyed by enemies.

---

## Game States

| State | Description |
|-------|-------------|
| MENU | Animated neural particle background; click **START HEIST** to begin |
| PLAYING | Main gameplay loop |
| PAUSED | Press ESC to pause; ESC again to resume |
| LEVEL_COMPLETE | All fragments collected; press ENTER to advance |
| GAME_OVER | Player HP reached 0; press ENTER to return to menu |

---

## Project Structure

```
mind-heist/
├── main.py                      # Main game loop & state machine
├── requirements.txt             # Dependencies
├── README.md                    # This file
│
├── backend/                     # AI stock signal backend (FastAPI)
│   ├── app/                      # API + services
│   ├── docker-compose.yml        # Postgres + Redis + API
│   ├── Dockerfile                # Backend container
│   ├── requirements.txt          # Backend dependencies
│   └── README.md                 # Backend docs
│
├── game/
│   ├── __init__.py
│   ├── constants.py             # Centralised settings (speed, HP, cooldowns, levels)
│   ├── player.py                # Player class (movement, health, energy, visibility)
│   ├── enemy.py                 # Enemy classes (Firewall, Bot, Corruption)
│   ├── abilities.py             # Ability system with cooldown tracking
│   └── level.py                 # Level management, graph layout, scoring
│
├── ui/
│   ├── __init__.py
│   ├── menu.py                  # Animated main menu with particle system
│   └── hud.py                   # In-game HUD (bars, cooldowns, event log)
│
└── utils/
    ├── __init__.py
    ├── colors.py                # Neon cyberpunk colour palette
    └── graph_generator.py       # Procedural neural-network graph generation
```

---

## Gameplay Tips

- **Cloak** makes you invulnerable to all damage – use it to pass through Corruption Zones safely.
- **Memory Pull** (R) lets you collect fragments from a distance – great when enemies are nearby.
- **Overclock** (F) slows everything down – use it when surrounded.
- **Pulse Dash** (Q) teleports you in your movement direction – escape tight spots instantly.
- Energy regenerates automatically; plan ability combos around your energy bar.

---

## Level Balancing

| Level | Name | Enemies | Memories | Nodes | Score ×|
|-------|------|---------|----------|-------|-------|
| 1 | Surface Thoughts | 3 | 5 | 15–20 | 1× |
| 2 | Emotional Core | 5 | 8 | 25–30 | 1.5× |
| 3 | Subconscious | 7 | 12 | 35–40 | 2× |
| 4 | Trauma Vault | 10 | 15 | 45–50 | 3× |

---

## Tech Stack

- **Python 3.10+**
- **Pygame 2** – rendering, input, game loop
- **NetworkX** – procedural graph generation (neurons & synapses)
- **NumPy** – numerical helpers

---

## Roadmap

- [ ] Sound effects & ambient music
- [ ] Sprite assets (replace geometric placeholders)
- [ ] Puzzle mode mini-game
- [ ] Save / leaderboard system
- [ ] AI difficulty scaling
- [ ] Additional levels and enemy types

---

## License

MIT
