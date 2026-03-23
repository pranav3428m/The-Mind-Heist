# Mind Heist: Neural Hacker - Level Management

import random
import math
import pygame

from game.constants import (
    LEVEL_CONFIGS, SCREEN_WIDTH, SCREEN_HEIGHT,
    MEMORY_COLLECT_RADIUS, SCORE_MEMORY_FRAGMENT,
    GRAPH_X_MIN, GRAPH_X_MAX, GRAPH_Y_MIN, GRAPH_Y_MAX,
)
from game.enemy import Enemy, ENEMY_TYPE_FIREWALL, ENEMY_TYPE_BOT, ENEMY_TYPE_CORRUPTION
from utils import colors
from utils.graph_generator import GraphGenerator


class MemoryFragment:
    """A collectible memory fragment node placed in the level."""

    SIZE = 8

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
        self.collected = False
        self._pulse = 0.0

    def update(self, dt: float) -> None:
        self._pulse = (self._pulse + dt * 3.0) % (math.pi * 2)

    def draw(self, surface: pygame.Surface) -> None:
        if self.collected:
            return
        pulse_scale = 1.0 + 0.3 * math.sin(self._pulse)
        r = int(self.SIZE * pulse_scale)
        pygame.draw.circle(surface, colors.memory_color,
                           (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, colors.neon_yellow,
                           (int(self.x), int(self.y)), r, 1)

    def get_rect(self) -> pygame.Rect:
        half = self.SIZE // 2
        return pygame.Rect(int(self.x) - half, int(self.y) - half,
                           self.SIZE, self.SIZE)


class Level:
    """Manages all per-level state: graph, enemies, memory fragments."""

    def __init__(self):
        self.current_level = 1
        self.graph = GraphGenerator()
        self.enemies: list[Enemy] = []
        self.memories: list[MemoryFragment] = []
        self.node_positions: dict = {}
        self.edges: list = []
        self.config: dict = {}
        self._time_elapsed = 0.0
        self.complete = False
        self.failed = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load_level(self, level_num: int) -> dict:
        """Initialize the given level number and return its config dict."""
        self.current_level = level_num
        self.config = LEVEL_CONFIGS.get(level_num, LEVEL_CONFIGS[1])
        self._time_elapsed = 0.0
        self.complete = False
        self.failed = False

        cfg = self.config
        # Generate neural graph
        self.graph.generate_graph(
            difficulty=cfg["difficulty"],
            node_count=random.randint(cfg["node_count_min"], cfg["node_count_max"]),
            connection_prob=cfg["connection_prob"],
        )
        self.node_positions = self.graph.get_node_positions()
        self.edges = self.graph.get_edges()

        self.spawn_enemies()
        self.spawn_memories()
        return cfg

    def spawn_enemies(self) -> None:
        """Create enemies as defined by the current level config."""
        self.enemies.clear()
        cfg = self.config
        enemy_counts = cfg.get("enemies", {})

        for _ in range(enemy_counts.get("firewall", 0)):
            x, y = self._random_spawn()
            self.enemies.append(Enemy(ENEMY_TYPE_FIREWALL, x, y))

        for _ in range(enemy_counts.get("bot", 0)):
            x, y = self._random_spawn()
            self.enemies.append(Enemy(ENEMY_TYPE_BOT, x, y))

        for _ in range(enemy_counts.get("corruption", 0)):
            x, y = self._random_spawn()
            self.enemies.append(Enemy(ENEMY_TYPE_CORRUPTION, x, y))

    def spawn_memories(self) -> None:
        """Place memory fragments at random node positions."""
        self.memories.clear()
        node_ids = list(self.node_positions.keys())
        count = self.config.get("memory_fragments", 5)
        if count > len(node_ids):
            count = len(node_ids)
        chosen = random.sample(node_ids, count)
        for nid in chosen:
            x, y = self.node_positions[nid]
            self.memories.append(MemoryFragment(x, y))

    def check_objectives(self) -> bool:
        """Return True if all memory fragments have been collected."""
        return all(m.collected for m in self.memories)

    def advance_level(self) -> bool:
        """Move to the next level.  Returns False if already at max level."""
        next_level = self.current_level + 1
        if next_level > max(LEVEL_CONFIGS.keys()):
            return False
        self.load_level(next_level)
        return True

    def calculate_score(self, base_score: int) -> int:
        """Apply the level's score multiplier to *base_score*."""
        multiplier = self.config.get("score_multiplier", 1.0)
        return int(base_score * multiplier)

    def collect_nearby_memories(self, player_x: float, player_y: float,
                                 pull_active: bool = False) -> int:
        """Collect memory fragments near the player.  Returns points earned."""
        points = 0
        collect_r = MEMORY_COLLECT_RADIUS
        pull_r = 200 if pull_active else collect_r

        for mem in self.memories:
            if mem.collected:
                continue
            dist = math.hypot(player_x - mem.x, player_y - mem.y)
            if dist <= pull_r:
                if pull_active and dist > collect_r:
                    # Move memory fragment toward player
                    dx = player_x - mem.x
                    dy = player_y - mem.y
                    speed = 200
                    length = math.hypot(dx, dy)
                    if length > 0:
                        mem.x += (dx / length) * speed * 0.016
                        mem.y += (dy / length) * speed * 0.016
                else:
                    mem.collected = True
                    points += SCORE_MEMORY_FRAGMENT
        return points

    # ------------------------------------------------------------------
    # Update / draw
    # ------------------------------------------------------------------

    def update(self, dt: float, player_pos: tuple,
               player_alive: bool) -> None:
        """Update all enemies and memory fragment animations."""
        self._time_elapsed += dt
        for enemy in self.enemies:
            enemy.update(player_pos, dt)
        for mem in self.memories:
            mem.update(dt)

        if self.check_objectives():
            self.complete = True

    def draw(self, surface: pygame.Surface) -> None:
        """Render the neural graph, memories, and enemies."""
        self._draw_graph(surface)
        for mem in self.memories:
            mem.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

    def get_time_elapsed(self) -> float:
        return self._time_elapsed

    def get_remaining_memories(self) -> int:
        return sum(1 for m in self.memories if not m.collected)

    def get_player_spawn(self) -> tuple:
        """Return a suitable player spawn position for this level."""
        return self.graph.get_random_spawn_point()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_spawn(self) -> tuple:
        x = random.randint(GRAPH_X_MIN, GRAPH_X_MAX)
        y = random.randint(GRAPH_Y_MIN, GRAPH_Y_MAX)
        return x, y

    def _draw_graph(self, surface: pygame.Surface) -> None:
        # Draw edges (synapses)
        for u, v in self.edges:
            if u in self.node_positions and v in self.node_positions:
                pygame.draw.line(
                    surface, colors.edge_color,
                    self.node_positions[u],
                    self.node_positions[v], 1,
                )
        # Draw nodes (neurons)
        for nid, pos in self.node_positions.items():
            pygame.draw.circle(surface, colors.node_fill, pos, 5)
            pygame.draw.circle(surface, colors.node_border, pos, 5, 1)
