# Mind Heist: Neural Hacker - Ability System

import math
import pygame
from game.constants import (
    ABILITY_PULSE_DASH, ABILITY_CLOAK, ABILITY_MEMORY_PULL, ABILITY_OVERCLOCK,
    PULSE_DASH_COOLDOWN, PULSE_DASH_ENERGY, PULSE_DASH_DISTANCE,
    CLOAK_COOLDOWN, CLOAK_ENERGY, CLOAK_DURATION,
    MEMORY_PULL_COOLDOWN, MEMORY_PULL_ENERGY, MEMORY_PULL_RADIUS, MEMORY_PULL_DURATION,
    OVERCLOCK_COOLDOWN, OVERCLOCK_ENERGY, OVERCLOCK_SLOWDOWN, OVERCLOCK_DURATION,
)
from utils import colors


class AbilitySystem:
    """Manages all four player abilities and their cooldowns/effects."""

    # Metadata table: key -> (name, cooldown, energy_cost, description)
    ABILITY_META = {
        ABILITY_PULSE_DASH: ("Pulse Dash",   PULSE_DASH_COOLDOWN,   PULSE_DASH_ENERGY,   "Teleport 150px forward"),
        ABILITY_CLOAK:      ("Cloak",        CLOAK_COOLDOWN,        CLOAK_ENERGY,        "Invisible for 3s"),
        ABILITY_MEMORY_PULL:("Memory Pull",  MEMORY_PULL_COOLDOWN,  MEMORY_PULL_ENERGY,  "Attract items in 200px"),
        ABILITY_OVERCLOCK:  ("Overclock",    OVERCLOCK_COOLDOWN,    OVERCLOCK_ENERGY,    "Slow time to 0.5x for 2s"),
    }

    def __init__(self, player):
        self._player = player
        # Remaining cooldown per ability key (seconds)
        self._cooldowns = {k: 0.0 for k in self.ABILITY_META}
        # Active duration timers
        self._active_timers = {k: 0.0 for k in self.ABILITY_META}
        # Time multiplier (modified by Overclock)
        self.time_scale = 1.0
        # Memory Pull active flag (consumed by level)
        self.memory_pull_active = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def activate_ability(self, ability_key: str, direction: tuple = (0, -1)) -> str:
        """Attempt to activate *ability_key*.

        Args:
            ability_key: One of the ABILITY_* constants.
            direction: (dx, dy) normalised direction vector (for Pulse Dash).

        Returns:
            A log message string describing the outcome.
        """
        if ability_key not in self.ABILITY_META:
            return ""

        name, cooldown, energy_cost, desc = self.ABILITY_META[ability_key]

        if self._cooldowns[ability_key] > 0:
            remaining = self._cooldowns[ability_key]
            return f"{name} on cooldown ({remaining:.1f}s)"

        if not self._player.use_energy(energy_cost):
            return f"Not enough energy for {name}"

        # Apply the effect
        if ability_key == ABILITY_PULSE_DASH:
            self._apply_pulse_dash(direction)
        elif ability_key == ABILITY_CLOAK:
            self._apply_cloak()
        elif ability_key == ABILITY_MEMORY_PULL:
            self._apply_memory_pull()
        elif ability_key == ABILITY_OVERCLOCK:
            self._apply_overclock()

        self._cooldowns[ability_key] = cooldown
        return f"{name} activated!"

    def update_cooldowns(self, dt: float) -> None:
        """Tick cooldown and active-effect timers each frame."""
        for key in self._cooldowns:
            if self._cooldowns[key] > 0:
                self._cooldowns[key] = max(0.0, self._cooldowns[key] - dt)

        # Cloak duration
        if self._active_timers[ABILITY_CLOAK] > 0:
            self._active_timers[ABILITY_CLOAK] -= dt
            if self._active_timers[ABILITY_CLOAK] <= 0:
                self._player.set_visibility(True)
                self._active_timers[ABILITY_CLOAK] = 0.0

        # Memory Pull duration
        if self._active_timers[ABILITY_MEMORY_PULL] > 0:
            self._active_timers[ABILITY_MEMORY_PULL] -= dt
            if self._active_timers[ABILITY_MEMORY_PULL] <= 0:
                self.memory_pull_active = False
                self._active_timers[ABILITY_MEMORY_PULL] = 0.0

        # Overclock duration
        if self._active_timers[ABILITY_OVERCLOCK] > 0:
            self._active_timers[ABILITY_OVERCLOCK] -= dt
            if self._active_timers[ABILITY_OVERCLOCK] <= 0:
                self.time_scale = 1.0
                self._active_timers[ABILITY_OVERCLOCK] = 0.0

    def get_cooldown_percent(self, ability_key: str) -> float:
        """Return remaining cooldown as a 0.0–1.0 fraction."""
        if ability_key not in self.ABILITY_META:
            return 0.0
        _, cooldown, _, _ = self.ABILITY_META[ability_key]
        remaining = self._cooldowns[ability_key]
        return remaining / cooldown if cooldown > 0 else 0.0

    def is_available(self, ability_key: str) -> bool:
        """Return True if the ability can be activated."""
        if ability_key not in self.ABILITY_META:
            return False
        _, _, energy_cost, _ = self.ABILITY_META[ability_key]
        return (
            self._cooldowns[ability_key] <= 0
            and self._player.energy >= energy_cost
        )

    def get_cooldown_remaining(self, ability_key: str) -> float:
        """Return remaining cooldown seconds for the given ability."""
        return self._cooldowns.get(ability_key, 0.0)

    # ------------------------------------------------------------------
    # Private effect applicators
    # ------------------------------------------------------------------

    def _apply_pulse_dash(self, direction: tuple) -> None:
        dx, dy = direction
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
        self._player.x += dx * PULSE_DASH_DISTANCE
        self._player.y += dy * PULSE_DASH_DISTANCE

    def _apply_cloak(self) -> None:
        self._player.set_visibility(False)
        self._active_timers[ABILITY_CLOAK] = CLOAK_DURATION

    def _apply_memory_pull(self) -> None:
        self.memory_pull_active = True
        self._active_timers[ABILITY_MEMORY_PULL] = MEMORY_PULL_DURATION

    def _apply_overclock(self) -> None:
        self.time_scale = OVERCLOCK_SLOWDOWN
        self._active_timers[ABILITY_OVERCLOCK] = OVERCLOCK_DURATION
