# Mind Heist: Neural Hacker - Enemy System

import math
import random
import pygame
from game.constants import (
    ENEMY_SPEED_FIREWALL, ENEMY_SPEED_BOT, ENEMY_SPEED_CORRUPTION,
    ENEMY_DETECTION_RANGE, ENEMY_SIZE,
    ENEMY_DAMAGE_FIREWALL, ENEMY_DAMAGE_BOT, ENEMY_DAMAGE_CORRUPTION,
    CORRUPTION_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT,
)
from utils import colors

ENEMY_TYPE_FIREWALL = "firewall"
ENEMY_TYPE_BOT = "bot"
ENEMY_TYPE_CORRUPTION = "corruption"


class Enemy:
    """Base class / factory for all enemy types."""

    def __init__(self, enemy_type: str, x: float, y: float):
        self.enemy_type = enemy_type
        self.x = float(x)
        self.y = float(y)
        self.size = ENEMY_SIZE
        self.alive = True

        if enemy_type == ENEMY_TYPE_FIREWALL:
            self.speed = ENEMY_SPEED_FIREWALL
            self.damage = ENEMY_DAMAGE_FIREWALL
            self.color = colors.color_firewall
            # Wave patrol: store origin and phase
            self._origin_x = float(x)
            self._origin_y = float(y)
            self._wave_phase = random.uniform(0, math.pi * 2)
            self._wave_amplitude = random.randint(60, 120)
            self._patrol_dir = random.choice([-1, 1])
            self._patrol_distance = random.randint(100, 200)
            self._patrol_progress = 0.0

        elif enemy_type == ENEMY_TYPE_BOT:
            self.speed = ENEMY_SPEED_BOT
            self.damage = ENEMY_DAMAGE_BOT
            self.color = colors.color_bot
            self.detection_range = ENEMY_DETECTION_RANGE
            self._chasing = False

        elif enemy_type == ENEMY_TYPE_CORRUPTION:
            self.speed = ENEMY_SPEED_CORRUPTION
            self.damage = ENEMY_DAMAGE_CORRUPTION   # per second in zone
            self.color = colors.color_corruption
            self.radius = CORRUPTION_RADIUS
            # Slow drift direction
            angle = random.uniform(0, math.pi * 2)
            self._drift_dx = math.cos(angle)
            self._drift_dy = math.sin(angle)
            self._drift_timer = 0.0
            self._drift_change = random.uniform(2.0, 5.0)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, player_pos: tuple, dt: float) -> None:
        """Update enemy position/state each frame.

        Args:
            player_pos: (px, py) player world coordinates.
            dt: Delta time in seconds.
        """
        if not self.alive:
            return

        if self.enemy_type == ENEMY_TYPE_FIREWALL:
            self._update_firewall(dt)
        elif self.enemy_type == ENEMY_TYPE_BOT:
            self._update_bot(player_pos, dt)
        elif self.enemy_type == ENEMY_TYPE_CORRUPTION:
            self._update_corruption(dt)

    # ------------------------------------------------------------------
    # Collision / detection
    # ------------------------------------------------------------------

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        """Return True if enemy overlaps the player's rect."""
        if self.enemy_type == ENEMY_TYPE_CORRUPTION:
            dist = math.hypot(
                self.x - (player_rect.x + player_rect.width / 2),
                self.y - (player_rect.y + player_rect.height / 2),
            )
            return dist <= self.radius
        return self.get_rect().colliderect(player_rect)

    def deal_damage(self) -> float:
        """Return damage amount for this enemy (per contact or per second)."""
        return self.damage

    def detect_player(self, player_pos: tuple) -> bool:
        """Return True if the player is within detection range (bots only)."""
        if self.enemy_type != ENEMY_TYPE_BOT:
            return False
        dist = math.hypot(self.x - player_pos[0], self.y - player_pos[1])
        return dist <= self.detection_range

    def get_rect(self) -> pygame.Rect:
        half = self.size // 2
        return pygame.Rect(int(self.x) - half, int(self.y) - half,
                           self.size, self.size)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        if self.enemy_type == ENEMY_TYPE_CORRUPTION:
            self._draw_corruption(surface)
        else:
            self._draw_solid(surface)

    # ------------------------------------------------------------------
    # Private update helpers
    # ------------------------------------------------------------------

    def _update_firewall(self, dt: float) -> None:
        """Predictable wave-patrol movement."""
        self._wave_phase += dt * 2.0
        self._patrol_progress += self.speed * dt * self._patrol_dir

        if abs(self._patrol_progress) >= self._patrol_distance:
            self._patrol_dir *= -1

        self.x = self._origin_x + self._patrol_progress
        self.y = self._origin_y + math.sin(self._wave_phase) * self._wave_amplitude

        # Clamp to playfield
        self.x = max(10, min(SCREEN_WIDTH - 10, self.x))
        self.y = max(10, min(SCREEN_HEIGHT - 10, self.y))

    def _update_bot(self, player_pos: tuple, dt: float) -> None:
        """Chase player when detected, wander otherwise."""
        self._chasing = self.detect_player(player_pos)
        if self._chasing:
            dx = player_pos[0] - self.x
            dy = player_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt

    def _update_corruption(self, dt: float) -> None:
        """Slow random drift around the map."""
        self._drift_timer += dt
        if self._drift_timer >= self._drift_change:
            angle = random.uniform(0, math.pi * 2)
            self._drift_dx = math.cos(angle)
            self._drift_dy = math.sin(angle)
            self._drift_timer = 0.0
            self._drift_change = random.uniform(2.0, 5.0)

        self.x += self._drift_dx * self.speed * dt
        self.y += self._drift_dy * self.speed * dt

        # Bounce off playfield edges
        if self.x < self.radius or self.x > SCREEN_WIDTH - self.radius:
            self._drift_dx *= -1
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        if self.y < self.radius or self.y > SCREEN_HEIGHT - self.radius:
            self._drift_dy *= -1
            self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_solid(self, surface: pygame.Surface) -> None:
        half = self.size // 2
        rect = pygame.Rect(int(self.x) - half, int(self.y) - half,
                           self.size, self.size)
        # Glow
        glow = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 60),
                         pygame.Rect(0, 0, self.size * 3, self.size * 3))
        surface.blit(glow, (rect.x - self.size, rect.y - self.size))
        pygame.draw.rect(surface, self.color, rect)

    def _draw_corruption(self, surface: pygame.Surface) -> None:
        zone_surf = pygame.Surface(
            (int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA
        )
        pygame.draw.circle(
            zone_surf, (*self.color, 60),
            (int(self.radius), int(self.radius)), int(self.radius),
        )
        pygame.draw.circle(
            zone_surf, (*colors.color_corruption_border, 150),
            (int(self.radius), int(self.radius)), int(self.radius), 2,
        )
        surface.blit(
            zone_surf,
            (int(self.x - self.radius), int(self.y - self.radius)),
        )
