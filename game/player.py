# Mind Heist: Neural Hacker - Player Class

import pygame
from game.constants import (
    PLAYER_SPEED, PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY,
    PLAYER_SIZE, PLAYER_ENERGY_REGEN,
    ABILITY_PULSE_DASH, ABILITY_CLOAK, ABILITY_MEMORY_PULL, ABILITY_OVERCLOCK,
)
from utils import colors


class Player:
    """Represents the player character (neural hacker agent)."""

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.energy = PLAYER_MAX_ENERGY
        self.max_energy = PLAYER_MAX_ENERGY
        self.score = 0
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.visible = True             # False when cloaked
        self.alive = True

        # Energy regeneration tracker
        self._energy_regen_rate = PLAYER_ENERGY_REGEN

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, dx: float, dy: float, dt: float,
             screen_width: int, screen_height: int) -> None:
        """Move the player by (dx, dy) direction vector, clamped to screen."""
        if dx != 0 or dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx /= length
            dy /= length

        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        half = self.size / 2
        self.x = max(half, min(screen_width - half, self.x))
        self.y = max(half, min(screen_height - half, self.y))

    # ------------------------------------------------------------------
    # Health / Energy
    # ------------------------------------------------------------------

    def take_damage(self, amount: float) -> None:
        """Decrease health by *amount*.  Ignores damage if cloaked."""
        if not self.visible:
            return
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False

    def heal(self, amount: float) -> None:
        """Increase health up to max_health."""
        self.health = min(self.max_health, self.health + amount)

    def use_energy(self, amount: float) -> bool:
        """Consume *amount* energy.  Returns True if successful."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def restore_energy(self, amount: float) -> None:
        """Restore energy up to max_energy."""
        self.energy = min(self.max_energy, self.energy + amount)

    def update_energy_regen(self, dt: float) -> None:
        """Passively regenerate energy each frame."""
        self.restore_energy(self._energy_regen_rate * dt)

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def add_score(self, points: int) -> None:
        self.score += points

    # ------------------------------------------------------------------
    # Visibility (Cloak mechanic)
    # ------------------------------------------------------------------

    def set_visibility(self, visible: bool) -> None:
        self.visible = visible

    # ------------------------------------------------------------------
    # Collision
    # ------------------------------------------------------------------

    def get_rect(self) -> pygame.Rect:
        """Return a pygame.Rect centered on the player's position."""
        half = self.size // 2
        return pygame.Rect(
            int(self.x) - half,
            int(self.y) - half,
            self.size,
            self.size,
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player on *surface*."""
        alpha = 80 if not self.visible else 255
        color = colors.neon_blue

        # Outer glow
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        glow_color = (*color, max(20, alpha // 4))
        pygame.draw.circle(
            glow_surf, glow_color,
            (self.size * 2, self.size * 2),
            self.size * 2,
        )
        surface.blit(
            glow_surf,
            (int(self.x) - self.size * 2, int(self.y) - self.size * 2),
        )

        # Core
        core_color = (*color, alpha)
        core_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.rect(
            core_surf, core_color,
            pygame.Rect(0, 0, self.size, self.size),
        )
        surface.blit(
            core_surf,
            (int(self.x) - self.size // 2, int(self.y) - self.size // 2),
        )

    # ------------------------------------------------------------------
    # Serialisation helper
    # ------------------------------------------------------------------

    def get_data(self) -> dict:
        """Return a dict snapshot of the player's current state."""
        return {
            "x": self.x,
            "y": self.y,
            "health": self.health,
            "max_health": self.max_health,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "score": self.score,
            "visible": self.visible,
            "alive": self.alive,
        }
