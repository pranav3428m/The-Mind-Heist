# Mind Heist: Neural Hacker - In-Game HUD

import pygame
from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    HUD_TOP_HEIGHT, HUD_BOTTOM_HEIGHT, HUD_LOG_MAX,
    ABILITY_PULSE_DASH, ABILITY_CLOAK, ABILITY_MEMORY_PULL, ABILITY_OVERCLOCK,
)
from utils import colors


class HUD:
    """Renders the in-game heads-up display (health, energy, score, cooldowns)."""

    ABILITY_LABELS = [
        (ABILITY_PULSE_DASH, "Q Dash"),
        (ABILITY_CLOAK,       "E Cloak"),
        (ABILITY_MEMORY_PULL, "R Pull"),
        (ABILITY_OVERCLOCK,   "F Clock"),
    ]

    def __init__(self):
        self._log: list[str] = []
        try:
            self._font_large = pygame.font.SysFont("monospace", 22, bold=True)
            self._font_small = pygame.font.SysFont("monospace", 16)
        except Exception:
            self._font_large = pygame.font.Font(None, 22)
            self._font_small = pygame.font.Font(None, 16)

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------

    def add_log(self, message: str) -> None:
        """Append a message to the event log (max HUD_LOG_MAX entries)."""
        self._log.append(message)
        if len(self._log) > HUD_LOG_MAX:
            self._log.pop(0)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, player_data: dict) -> None:
        """Receive updated player data snapshot (from player.get_data())."""
        # Reserved for future animations or reactive HUD elements
        pass

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, player, level, abilities) -> None:
        """Render the full HUD on *surface*.

        Args:
            surface: Destination surface.
            player: Player instance.
            level: Level instance.
            abilities: AbilitySystem instance.
        """
        self._draw_top_bar(surface, player, level)
        self._draw_bottom_bar(surface, player, abilities)

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_top_bar(self, surface: pygame.Surface, player, level) -> None:
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_TOP_HEIGHT)
        pygame.draw.rect(surface, colors.hud_bg, bar_rect)
        pygame.draw.rect(surface, colors.hud_border, bar_rect, 1)

        # Score
        score_text = self._font_large.render(
            f"SCORE: {player.score}", True, colors.neon_yellow
        )
        surface.blit(score_text, (12, 14))

        # Level name
        level_name = level.config.get("name", f"LEVEL {level.current_level}")
        level_text = self._font_large.render(
            f"LEVEL {level.current_level}: {level_name}", True, colors.neon_green
        )
        lx = SCREEN_WIDTH // 2 - level_text.get_width() // 2
        surface.blit(level_text, (lx, 14))

        # Memories remaining
        remaining = level.get_remaining_memories()
        total = len(level.memories)
        mem_text = self._font_small.render(
            f"MEMORIES: {total - remaining}/{total}", True, colors.neon_blue
        )
        surface.blit(mem_text, (SCREEN_WIDTH - mem_text.get_width() - 200, 16))

        # Health bar
        self._draw_bar(
            surface,
            x=SCREEN_WIDTH - 380, y=8,
            width=160, height=14,
            value=player.health, max_value=player.max_health,
            fill_color=colors.hud_health, label="HP",
        )
        # Energy bar
        self._draw_bar(
            surface,
            x=SCREEN_WIDTH - 380, y=28,
            width=160, height=14,
            value=player.energy, max_value=player.max_energy,
            fill_color=colors.hud_energy, label="EN",
        )

    def _draw_bottom_bar(self, surface: pygame.Surface, player, abilities) -> None:
        bar_y = SCREEN_HEIGHT - HUD_BOTTOM_HEIGHT
        bar_rect = pygame.Rect(0, bar_y, SCREEN_WIDTH, HUD_BOTTOM_HEIGHT)
        pygame.draw.rect(surface, colors.hud_bg, bar_rect)
        pygame.draw.rect(surface, colors.hud_border, bar_rect, 1)

        # Ability cooldown indicators
        slot_w = 90
        for i, (key, label) in enumerate(self.ABILITY_LABELS):
            slot_x = 10 + i * (slot_w + 6)
            slot_y = bar_y + 6
            available = abilities.is_available(key)
            cd_pct = abilities.get_cooldown_percent(key)
            cd_remaining = abilities.get_cooldown_remaining(key)

            slot_color = colors.neon_blue if available else colors.dark_gray
            pygame.draw.rect(surface, colors.dark_gray,
                             pygame.Rect(slot_x, slot_y, slot_w, 48))
            pygame.draw.rect(surface, slot_color,
                             pygame.Rect(slot_x, slot_y, slot_w, 48), 1)

            # Cooldown fill (from bottom)
            if cd_pct > 0:
                fill_h = int(48 * cd_pct)
                pygame.draw.rect(
                    surface, (30, 30, 50),
                    pygame.Rect(slot_x + 1, slot_y + 1, slot_w - 2, 48 - 2),
                )
                pygame.draw.rect(
                    surface, (50, 50, 80),
                    pygame.Rect(slot_x + 1, slot_y + 48 - fill_h - 1,
                                slot_w - 2, fill_h),
                )

            lbl_surf = self._font_small.render(label, True, slot_color)
            surface.blit(lbl_surf, (slot_x + slot_w // 2 - lbl_surf.get_width() // 2,
                                    slot_y + 6))
            if cd_remaining > 0:
                cd_surf = self._font_small.render(
                    f"{cd_remaining:.1f}s", True, colors.light_gray
                )
                surface.blit(cd_surf,
                             (slot_x + slot_w // 2 - cd_surf.get_width() // 2,
                              slot_y + 28))

        # Event log
        log_x = 400
        for idx, msg in enumerate(reversed(self._log[-HUD_LOG_MAX:])):
            alpha = 255 - idx * 40
            alpha = max(60, alpha)
            log_color = colors.neon_green if idx == 0 else colors.light_gray
            log_surf = self._font_small.render(msg, True, log_color)
            surface.blit(log_surf, (log_x, bar_y + 8 + idx * 14))

    def _draw_bar(self, surface: pygame.Surface,
                  x: int, y: int, width: int, height: int,
                  value: float, max_value: float,
                  fill_color: tuple, label: str) -> None:
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, colors.dark_gray, bg_rect)
        fill_w = int(width * max(0, value) / max_value) if max_value > 0 else 0
        if fill_w > 0:
            pygame.draw.rect(surface, fill_color,
                             pygame.Rect(x, y, fill_w, height))
        pygame.draw.rect(surface, colors.hud_border, bg_rect, 1)
        lbl_surf = self._font_small.render(
            f"{label} {int(value)}/{int(max_value)}", True, colors.light_gray
        )
        surface.blit(lbl_surf, (x + 2, y + (height - lbl_surf.get_height()) // 2))
