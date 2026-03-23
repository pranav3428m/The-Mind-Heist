# Mind Heist: Neural Hacker - Main Menu

import random
import math
import pygame
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from utils import colors


class Particle:
    """A glowing neural-background particle."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(-20, 20)
        self.radius = random.randint(2, 5)
        self.alpha = random.randint(80, 200)
        self.color = random.choice([
            colors.neon_blue, colors.neon_purple, colors.neon_green,
        ])

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        if (self.x < -20 or self.x > SCREEN_WIDTH + 20
                or self.y < -20 or self.y > SCREEN_HEIGHT + 20):
            self.reset()


class MenuButton:
    """A single clickable menu button."""

    def __init__(self, label: str, x: int, y: int, width: int, height: int):
        self.label = label
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if this button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        bg_color = (*colors.neon_blue, 40) if self.hovered else (*colors.dark_gray, 180)
        border_color = colors.neon_blue if self.hovered else colors.dark_gray

        btn_surf = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(btn_surf, bg_color,
                         pygame.Rect(0, 0, self.rect.width, self.rect.height),
                         border_radius=6)
        surface.blit(btn_surf, self.rect.topleft)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)

        text_color = colors.neon_blue if self.hovered else colors.light_gray
        text_surf = font.render(self.label, True, text_color)
        tx = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        ty = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))


class Menu:
    """Animated main menu with neural particle background."""

    PARTICLE_COUNT = 50
    CONNECTION_DIST = 120       # max distance to draw a connection line

    def __init__(self):
        self._particles: list[Particle] = []
        self._buttons: list[MenuButton] = []
        self._time = 0.0
        self._action: str = ""   # set when a button is clicked

        try:
            self._font_title = pygame.font.SysFont("monospace", 72, bold=True)
            self._font_subtitle = pygame.font.SysFont("monospace", 28)
            self._font_button = pygame.font.SysFont("monospace", 24)
        except Exception:
            self._font_title = pygame.font.Font(None, 72)
            self._font_subtitle = pygame.font.Font(None, 28)
            self._font_button = pygame.font.Font(None, 24)

        self.init_particles()
        self._init_buttons()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def init_particles(self) -> None:
        self._particles = [Particle() for _ in range(self.PARTICLE_COUNT)]

    def _init_buttons(self) -> None:
        cx = SCREEN_WIDTH // 2
        button_defs = [
            ("START HEIST",   320),
            ("PUZZLE MODE",   390),
            ("SETTINGS",      460),
            ("QUIT",          530),
        ]
        for label, y in button_defs:
            self._buttons.append(MenuButton(label, cx, y, 260, 48))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._time += dt
        for p in self._particles:
            p.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.dark_bg)
        self._draw_particles(surface)
        self._draw_title(surface)
        for btn in self._buttons:
            btn.draw(surface, self._font_button)

    def handle_event(self, event: pygame.event.Event) -> str:
        """Process input events.  Returns an action string on button click.

        Possible return values:
            "start"   – Start Heist button
            "puzzle"  – Puzzle Mode button
            "settings"– Settings button
            "quit"    – Quit button
            ""        – No action
        """
        for i, btn in enumerate(self._buttons):
            if btn.handle_event(event):
                actions = ["start", "puzzle", "settings", "quit"]
                return actions[i]
        return ""

    def on_start(self) -> None:
        """Called when the game transitions away from the menu."""
        pass

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_particles(self, surface: pygame.Surface) -> None:
        for i, p in enumerate(self._particles):
            # Draw connections to nearby particles
            for j in range(i + 1, len(self._particles)):
                q = self._particles[j]
                dist = math.hypot(p.x - q.x, p.y - q.y)
                if dist < self.CONNECTION_DIST:
                    alpha = int(100 * (1 - dist / self.CONNECTION_DIST))
                    line_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                                              pygame.SRCALPHA)
                    pygame.draw.line(
                        line_surf,
                        (*colors.neon_blue, alpha),
                        (int(p.x), int(p.y)),
                        (int(q.x), int(q.y)),
                        1,
                    )
                    surface.blit(line_surf, (0, 0))

            # Draw particle core
            glow = pygame.Surface(
                (p.radius * 4, p.radius * 4), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow, (*p.color, max(10, p.alpha // 3)),
                (p.radius * 2, p.radius * 2), p.radius * 2,
            )
            surface.blit(glow, (int(p.x) - p.radius * 2,
                                int(p.y) - p.radius * 2))
            pygame.draw.circle(surface, p.color,
                               (int(p.x), int(p.y)), p.radius)

    def _draw_title(self, surface: pygame.Surface) -> None:
        # Pulsing glow offset
        pulse = math.sin(self._time * 2) * 3

        title_surf = self._font_title.render("MIND HEIST", True, colors.neon_purple)
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = int(140 + pulse)
        surface.blit(title_surf, (tx, ty))

        sub_surf = self._font_subtitle.render(
            "Neural Hacker", True, colors.neon_blue
        )
        sx = SCREEN_WIDTH // 2 - sub_surf.get_width() // 2
        surface.blit(sub_surf, (sx, ty + title_surf.get_height() + 6))
