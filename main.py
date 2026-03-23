#!/usr/bin/env python3
"""
Mind Heist: Neural Hacker
=========================
Main entry point – initialises Pygame, manages the top-level game-state
machine, and drives the main loop.

Controls
--------
  WASD / Arrow Keys  – Move
  Q                  – Pulse Dash
  E                  – Cloak
  R                  – Memory Pull
  F                  – Overclock
  ESC                – Pause / Resume
"""

import sys
import pygame

from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_LEVEL_COMPLETE, STATE_GAME_OVER,
    ABILITY_PULSE_DASH, ABILITY_CLOAK, ABILITY_MEMORY_PULL, ABILITY_OVERCLOCK,
    ENEMY_TYPE_CORRUPTION, SCORE_TIME_BONUS,
    LEVEL_CONFIGS,
)
from game.player import Player
from game.level import Level
from game.abilities import AbilitySystem
from game.enemy import ENEMY_TYPE_FIREWALL, ENEMY_TYPE_BOT
from ui.menu import Menu
from ui.hud import HUD
from utils import colors


# ---------------------------------------------------------------------------
# Overlay helpers
# ---------------------------------------------------------------------------

def draw_overlay_text(surface, font_large, font_medium, lines,
                      alpha=200, y_start=None):
    """Draw a semi-transparent centred overlay with multiple text lines."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))

    if y_start is None:
        y_start = SCREEN_HEIGHT // 2 - len(lines) * 30

    y = y_start
    for text, color, big in lines:
        font = font_large if big else font_medium
        surf = font.render(text, True, color)
        x = SCREEN_WIDTH // 2 - surf.get_width() // 2
        surface.blit(surf, (x, y))
        y += surf.get_height() + 12


# ---------------------------------------------------------------------------
# Main Game Class
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        try:
            self.font_large = pygame.font.SysFont("monospace", 52, bold=True)
            self.font_medium = pygame.font.SysFont("monospace", 28)
        except Exception:
            self.font_large = pygame.font.Font(None, 52)
            self.font_medium = pygame.font.Font(None, 28)

        # Sub-systems
        self.menu = Menu()
        self.hud = HUD()
        self.level = Level()
        self.player = None
        self.abilities = None

        self.state = STATE_MENU
        self._damage_timer = {}  # enemy_id -> cooldown timer
        self._score_timer = 0.0        # for time-based score

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def start_game(self):
        """Begin a fresh game from level 1."""
        self.level.load_level(1)
        spawn = self.level.get_player_spawn()
        self.player = Player(*spawn)
        self.abilities = AbilitySystem(self.player)
        self.hud = HUD()
        self._damage_timer.clear()
        self._score_timer = 0.0
        self.state = STATE_PLAYING
        self.hud.add_log(f"Level 1: {self.level.config['name']}")

    def advance_level(self):
        """Proceed to the next level, or end the game if none remain."""
        advanced = self.level.advance_level()
        if not advanced:
            # All levels complete – show game over / win screen
            self.state = STATE_GAME_OVER
            return
        spawn = self.level.get_player_spawn()
        self.player.x, self.player.y = spawn
        self.player.heal(30)          # small heal between levels
        self.abilities = AbilitySystem(self.player)
        self._damage_timer.clear()
        self._score_timer = 0.0
        self.state = STATE_PLAYING
        self.hud.add_log(
            f"Level {self.level.current_level}: {self.level.config['name']}"
        )

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_event(self, event):
        if self.state == STATE_MENU:
            action = self.menu.handle_event(event)
            if action == "start":
                self.menu.on_start()
                self.start_game()
            elif action == "quit":
                pygame.quit()
                sys.exit()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                return

            if self.state == STATE_PLAYING and self.player and self.abilities:
                key_map = {
                    pygame.K_q: ABILITY_PULSE_DASH,
                    pygame.K_e: ABILITY_CLOAK,
                    pygame.K_r: ABILITY_MEMORY_PULL,
                    pygame.K_f: ABILITY_OVERCLOCK,
                }
                if event.key in key_map:
                    ability_key = key_map[event.key]
                    keys = pygame.key.get_pressed()
                    dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - \
                         (keys[pygame.K_a] or keys[pygame.K_LEFT])
                    dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - \
                         (keys[pygame.K_w] or keys[pygame.K_UP])
                    if dx == 0 and dy == 0:
                        dy = -1  # default dash upward
                    msg = self.abilities.activate_ability(ability_key, (dx, dy))
                    if msg:
                        self.hud.add_log(msg)

            if self.state == STATE_LEVEL_COMPLETE:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.advance_level()

            if self.state == STATE_GAME_OVER:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = STATE_MENU

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt):
        if self.state == STATE_MENU:
            self.menu.update(dt)
            return

        if self.state in (STATE_PAUSED, STATE_LEVEL_COMPLETE, STATE_GAME_OVER):
            return

        if self.state != STATE_PLAYING:
            return

        # Apply time scale (Overclock)
        scaled_dt = dt * self.abilities.time_scale

        # Player movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - \
             (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - \
             (keys[pygame.K_w] or keys[pygame.K_UP])
        self.player.move(float(dx), float(dy), scaled_dt,
                         SCREEN_WIDTH, SCREEN_HEIGHT)

        # Energy regeneration
        self.player.update_energy_regen(scaled_dt)

        # Ability cooldowns
        self.abilities.update_cooldowns(dt)   # real time for cooldowns

        # Time-based score
        self._score_timer += scaled_dt
        if self._score_timer >= 1.0:
            self.player.add_score(
                self.level.calculate_score(SCORE_TIME_BONUS)
            )
            self._score_timer -= 1.0

        # Memory collection
        points = self.level.collect_nearby_memories(
            self.player.x, self.player.y,
            pull_active=self.abilities.memory_pull_active,
        )
        if points:
            total = self.level.calculate_score(points * 10)
            self.player.add_score(total)
            self.hud.add_log(f"+{total} memory fragment(s) collected!")

        # Enemy updates & damage
        player_rect = self.player.get_rect()
        for i, enemy in enumerate(self.level.enemies):
            enemy.update((self.player.x, self.player.y), scaled_dt)
            if enemy.check_collision(player_rect):
                timer_key = id(enemy)
                self._damage_timer.setdefault(timer_key, 0.0)
                self._damage_timer[timer_key] += dt
                interval = 1.0 if enemy.enemy_type == ENEMY_TYPE_CORRUPTION else 0.5
                if self._damage_timer[timer_key] >= interval:
                    dmg = enemy.deal_damage()
                    self.player.take_damage(dmg)
                    self._damage_timer[timer_key] = 0.0
                    self.hud.add_log(f"Damage! -{int(dmg)} HP")
            else:
                self._damage_timer[id(enemy)] = 0.0

        # Level update
        self.level.update(scaled_dt, (self.player.x, self.player.y),
                          self.player.alive)

        # HUD update
        self.hud.update(self.player.get_data())

        # State transitions
        if not self.player.alive:
            self.state = STATE_GAME_OVER
        elif self.level.complete:
            bonus = self.level.calculate_score(50)
            self.player.add_score(bonus)
            self.hud.add_log(f"Level Complete! +{bonus} bonus!")
            self.state = STATE_LEVEL_COMPLETE

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        self.screen.fill(colors.dark_bg)

        if self.state == STATE_MENU:
            self.menu.draw(self.screen)
            return

        # Playing / Paused / Level Complete / Game Over – draw level & HUD
        if self.player and self.level and self.abilities:
            self.level.draw(self.screen)
            self.player.draw(self.screen)
            self.hud.draw(self.screen, self.player, self.level, self.abilities)

        if self.state == STATE_PAUSED:
            draw_overlay_text(self.screen, self.font_large, self.font_medium, [
                ("PAUSED", colors.neon_blue, True),
                ("Press ESC to resume", colors.light_gray, False),
            ])

        elif self.state == STATE_LEVEL_COMPLETE:
            next_lvl = self.level.current_level + 1
            has_next = next_lvl in LEVEL_CONFIGS
            lines = [
                ("LEVEL COMPLETE!", colors.neon_green, True),
                (f"Score: {self.player.score}", colors.neon_yellow, False),
            ]
            if has_next:
                lines.append((f"Next: Level {next_lvl} – "
                               f"{LEVEL_CONFIGS[next_lvl]['name']}",
                               colors.neon_blue, False))
                lines.append(("Press ENTER to continue", colors.light_gray, False))
            else:
                lines.append(("All levels complete! You WIN!", colors.neon_purple, False))
                lines.append(("Press ENTER to return to menu", colors.light_gray, False))
            draw_overlay_text(self.screen, self.font_large, self.font_medium, lines)

        elif self.state == STATE_GAME_OVER:
            lines = [
                ("GAME OVER", colors.neon_red, True),
                (f"Final Score: {self.player.score if self.player else 0}",
                 colors.neon_yellow, False),
                ("Press ENTER to return to menu", colors.light_gray, False),
            ]
            draw_overlay_text(self.screen, self.font_large, self.font_medium, lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()