#!/usr/bin/env python3
"""Libethenite Loom — neon warp-weft arcade for ElbowOS. Python 3 + pygame.

Beat the copper shuttle into a matching warp thread to weave a stitch.
Left/Right choose a column. Space beats. R restarts.
Featured: https://x.com/ElbowOS
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/LIBETHENITE_LOOM_ElbowOS.mp4")
COLS = 8
CX0, CX1 = 150, 930
SHUT_Y = 560
COLORS = [(52, 230, 138), (255, 198, 64), (255, 78, 168), (78, 214, 255), (214, 122, 48)]
NAMES = ["EMERALD", "GOLD", "MAGENTA", "CYAN", "COPPER"]


def col_x(i):
    return CX0 + (CX1 - CX0) * i / (COLS - 1)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption("Libethenite Loom")
        self.font = pygame.font.Font(None, 78)
        self.mid = pygame.font.Font(None, 46)
        self.small = pygame.font.Font(None, 34)
        self.reset()

    def reset(self):
        self.t = 0.0
        self.score = 0
        self.combo = 0
        self.lives = 3
        self.col = 3
        self.shuttle = 540.0
        self.dir = 1
        self.weft = 0
        self.warp = [i % 5 for i in range(COLS)]
        self.rows = [[None] * COLS for _ in range(14)]
        self.row = 0
        self.cool = 0.0
        self.flash = 0.0
        self.sparks = []
        self.banner = "MATCH THE WEFT"

    def try_beat(self):
        if self.cool > 0:
            return
        cx = col_x(self.col)
        near = abs(self.shuttle - cx) < 96
        match = self.warp[self.col] == self.weft
        self.cool = 0.16
        if near and match and self.rows[self.row][self.col] is None:
            self.rows[self.row][self.col] = self.weft
            self.combo += 1
            self.score += 25 * self.combo
            self.banner = f"{NAMES[self.weft]} STITCH  x{self.combo}"
            self.flash = 0.25
            for _ in range(10):
                ang = random.random() * math.tau
                self.sparks.append([cx, SHUT_Y, math.cos(ang) * 280, math.sin(ang) * 220, 0.45, COLORS[self.weft]])
            if all(c is not None for c in self.rows[self.row]) or sum(c is not None for c in self.rows[self.row]) >= 6:
                self.row = min(self.row + 1, 13)
                self.combo += 1
                self.score += 80
        elif near:
            self.combo = 0
            self.lives = max(0, self.lives - 1)
            self.banner = "SNAG — WRONG HUE"
            self.flash = 0.35
            self.sparks.append([cx, SHUT_Y, 0, -80, 0.4, (255, 70, 70)])

    def update(self, dt, auto=False):
        self.t += dt
        self.cool = max(0, self.cool - dt)
        self.flash = max(0, self.flash - dt)
        self.shuttle += self.dir * 340 * dt
        if self.shuttle > CX1 + 20:
            self.shuttle = CX1 + 20
            self.dir = -1
            self.weft = (self.weft + 1 + (self.row % 2)) % 5
        elif self.shuttle < CX0 - 20:
            self.shuttle = CX0 - 20
            self.dir = 1
            self.weft = (self.weft + 2) % 5
        if auto:
            self._auto()
        alive = []
        for s in self.sparks:
            s[0] += s[2] * dt
            s[1] += s[3] * dt
            s[3] += 420 * dt
            s[4] -= dt
            if s[4] > 0:
                alive.append(s)
        self.sparks = alive

    def _auto(self):
        order = list(range(COLS)) if self.dir > 0 else list(range(COLS - 1, -1, -1))
        target = None
        for i in order:
            ahead = (self.dir > 0 and col_x(i) >= self.shuttle - 30) or (self.dir < 0 and col_x(i) <= self.shuttle + 30)
            if ahead and self.rows[self.row][i] is None:
                target = i
                break
        if target is None:
            target = min(range(COLS), key=lambda i: abs(col_x(i) - self.shuttle))
        self.col = target
        if abs(self.shuttle - col_x(self.col)) < 120:
            self.weft = self.warp[self.col]
        if abs(self.shuttle - col_x(self.col)) < 88 and self.rows[self.row][self.col] is None:
            self.try_beat()

    def draw(self):
        s = self.screen
        s.fill((6, 18, 14))
        for y in range(0, H, 8):
            k = y / H
            pygame.draw.line(s, (8 + int(18 * k), 28 + int(30 * k), 18), (0, y), (W, y))
        for x in (70, 1010):
            pygame.draw.rect(s, (92, 52, 24), (x, 250, 28, 1280), border_radius=8)
            pygame.draw.rect(s, (214, 140, 62), (x + 6, 250, 8, 1280))
        for i in range(COLS):
            x = int(col_x(i))
            c = COLORS[self.warp[i]]
            pygame.draw.line(s, (c[0] // 5, c[1] // 5, c[2] // 5), (x, 300), (x, 1560), 10)
            pygame.draw.line(s, c, (x, 300), (x, 1560), 3)
            if i == self.col:
                pygame.draw.circle(s, (255, 236, 180), (x, 320), 16, 3)
        base = 980
        for r, row in enumerate(self.rows):
            y = base + r * 40
            for i, cell in enumerate(row):
                if cell is None:
                    continue
                x = int(col_x(i))
                c = COLORS[cell]
                pygame.draw.polygon(s, c, [(x, y - 12), (x + 16, y), (x, y + 12), (x - 16, y)])
                pygame.draw.line(s, (255, 255, 230), (x - 10, y), (x + 10, y), 2)
        wc = COLORS[self.weft]
        pygame.draw.line(s, wc, (int(self.shuttle - self.dir * 160), SHUT_Y), (int(self.shuttle), SHUT_Y), 8)
        sx = int(self.shuttle)
        pygame.draw.ellipse(s, (240, 168, 72), (sx - 46, SHUT_Y - 22, 92, 44))
        pygame.draw.ellipse(s, wc, (sx - 22, SHUT_Y - 12, 44, 24))
        nose = (sx + self.dir * 54, SHUT_Y)
        pygame.draw.polygon(s, (255, 220, 140), [(sx + self.dir * 30, SHUT_Y - 14), nose, (sx + self.dir * 30, SHUT_Y + 14)])
        for sp in self.sparks:
            pygame.draw.circle(s, sp[5], (int(sp[0]), int(sp[1])), max(2, int(6 * sp[4] / 0.45)))
        if self.flash > 0:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 220, 140, int(70 * self.flash / 0.35)))
            s.blit(veil, (0, 0))
        title = self.font.render("LIBETHENITE LOOM", True, (232, 255, 214))
        s.blit(title, title.get_rect(center=(W // 2, 110)))
        sub = self.mid.render(self.banner, True, wc)
        s.blit(sub, sub.get_rect(center=(W // 2, 180)))
        score = self.font.render(f"SCORE {self.score}", True, (255, 214, 120))
        s.blit(score, score.get_rect(center=(W // 2, 1680)))
        lives = self.mid.render("REEDS " + "● " * self.lives, True, (255, 120, 140))
        s.blit(lives, lives.get_rect(center=(W // 2, 1748)))
        tag = self.small.render("x.com/ElbowOS", True, (186, 255, 214))
        s.blit(tag, tag.get_rect(center=(W // 2, 1840)))
        hint = self.small.render("A/D column   SPACE beat", True, (140, 180, 150))
        s.blit(hint, hint.get_rect(center=(W // 2, 1888)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(FPS) / 1000
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        self.col = max(0, self.col - 1)
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        self.col = min(COLS - 1, self.col + 1)
                    elif ev.key == pygame.K_SPACE:
                        self.try_beat()
                    elif ev.key == pygame.K_r:
                        self.reset()
            self.update(dt, auto=False)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def record(self):
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        n = FPS * SECS
        try:
            for _ in range(n):
                self.update(1 / FPS, auto=True)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, "score", self.score)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
