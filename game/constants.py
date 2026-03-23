# Mind Heist: Neural Hacker - Game Configuration & Settings

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Mind Heist: Neural Hacker"

# Game states
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_LEVEL_COMPLETE = "LEVEL_COMPLETE"
STATE_GAME_OVER = "GAME_OVER"

# Player settings
PLAYER_SPEED = 150          # pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ENERGY = 200
PLAYER_SIZE = 10            # 10x10 pixels
PLAYER_ENERGY_REGEN = 15    # energy per second

# Enemy settings
ENEMY_SPEED_FIREWALL = 120      # pixels per second
ENEMY_SPEED_BOT = 120
ENEMY_SPEED_CORRUPTION = 30
ENEMY_DETECTION_RANGE = 200     # pixels
ENEMY_SIZE = 8                  # 8x8 pixels

ENEMY_DAMAGE_FIREWALL = 10      # HP per contact
ENEMY_DAMAGE_BOT = 15           # HP per contact
ENEMY_DAMAGE_CORRUPTION = 5     # HP per second in zone
CORRUPTION_RADIUS = 100         # pixels

# Ability keys
ABILITY_PULSE_DASH = "q"
ABILITY_CLOAK = "e"
ABILITY_MEMORY_PULL = "r"
ABILITY_OVERCLOCK = "f"

# Ability settings
PULSE_DASH_COOLDOWN = 3.0       # seconds
PULSE_DASH_ENERGY = 20
PULSE_DASH_DISTANCE = 150       # pixels

CLOAK_COOLDOWN = 5.0
CLOAK_ENERGY = 30
CLOAK_DURATION = 3.0            # seconds

MEMORY_PULL_COOLDOWN = 4.0
MEMORY_PULL_ENERGY = 25
MEMORY_PULL_RADIUS = 200        # pixels
MEMORY_PULL_DURATION = 2.0      # seconds

OVERCLOCK_COOLDOWN = 6.0
OVERCLOCK_ENERGY = 40
OVERCLOCK_SLOWDOWN = 0.5        # time multiplier
OVERCLOCK_DURATION = 2.0        # seconds

# Scoring
SCORE_MEMORY_FRAGMENT = 10      # points per fragment
SCORE_TIME_BONUS = 5            # points per second survived

# Level configurations
LEVEL_CONFIGS = {
    1: {
        "name": "Surface Thoughts",
        "difficulty": 1,
        "score_multiplier": 1.0,
        "enemies": {
            "firewall": 2,
            "bot": 1,
            "corruption": 0,
        },
        "memory_fragments": 5,
        "node_count_min": 15,
        "node_count_max": 20,
        "connection_prob": 0.3,
        "description": "Tutorial level, basic mechanics",
    },
    2: {
        "name": "Emotional Core",
        "difficulty": 2,
        "score_multiplier": 1.5,
        "enemies": {
            "firewall": 3,
            "bot": 2,
            "corruption": 0,
        },
        "memory_fragments": 8,
        "node_count_min": 25,
        "node_count_max": 30,
        "connection_prob": 0.4,
        "description": "Moderate challenge",
    },
    3: {
        "name": "Subconscious",
        "difficulty": 3,
        "score_multiplier": 2.0,
        "enemies": {
            "firewall": 3,
            "bot": 2,
            "corruption": 2,
        },
        "memory_fragments": 12,
        "node_count_min": 35,
        "node_count_max": 40,
        "connection_prob": 0.5,
        "description": "High challenge",
    },
    4: {
        "name": "Trauma Vault",
        "difficulty": 4,
        "score_multiplier": 3.0,
        "enemies": {
            "firewall": 4,
            "bot": 3,
            "corruption": 3,
        },
        "memory_fragments": 15,
        "node_count_min": 45,
        "node_count_max": 50,
        "connection_prob": 0.7,
        "description": "Final boss level",
    },
}

# Graph bounds (playfield)
GRAPH_X_MIN = 100
GRAPH_X_MAX = 1180
GRAPH_Y_MIN = 100
GRAPH_Y_MAX = 620
NODE_MIN_SPACING = 50           # minimum pixels between nodes

# Memory fragment collect radius
MEMORY_COLLECT_RADIUS = 20

# HUD layout
HUD_TOP_HEIGHT = 50
HUD_BOTTOM_HEIGHT = 60
HUD_LOG_MAX = 5
