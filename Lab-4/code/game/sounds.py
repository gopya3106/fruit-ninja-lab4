import array
import math
import random

import pygame


class SoundManager:
    """Builds the game's sound effects in code (no audio files needed).

    If no audio device is available, every play_* call quietly does nothing
    so the game still runs.
    """

    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.rate, _, self.channels = pygame.mixer.get_init()
            self.slice_sound = self._make_slice()
            self.bomb_sound = self._make_bomb()
            self.game_over_sound = self._make_game_over()
            self.enabled = True
        except pygame.error:
            print("Sound unavailable - continuing without audio.")

    # ---- helpers -------------------------------------------------------
    def _to_sound(self, samples):
        data = array.array("h")
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            for _ in range(self.channels):
                data.append(v)
        return pygame.mixer.Sound(buffer=data.tobytes())

    # ---- the three effects ---------------------------------------------
    def _make_slice(self):
        """Quick 'swish': falling pitch plus a little noise."""
        n = int(self.rate * 0.16)
        samples = []
        phase = 0.0
        for i in range(n):
            t = i / n
            freq = 1400 - 900 * t
            phase += 2 * math.pi * freq / self.rate
            env = (1 - t) ** 2
            samples.append(0.35 * env * (math.sin(phase) + 0.6 * random.uniform(-1, 1)))
        return self._to_sound(samples)

    def _make_bomb(self):
        """Low explosion rumble: noise plus a deep tone, fading out."""
        n = int(self.rate * 0.6)
        samples = []
        for i in range(n):
            t = i / n
            env = math.exp(-5 * t)
            rumble = math.sin(2 * math.pi * 70 * (i / self.rate))
            samples.append(0.6 * env * (0.7 * random.uniform(-1, 1) + 0.6 * rumble))
        return self._to_sound(samples)

    def _make_game_over(self):
        """Four descending notes."""
        samples = []
        for freq in (392, 330, 262, 196):
            n = int(self.rate * 0.28)
            for i in range(n):
                t = i / n
                env = (1 - t) ** 1.5
                samples.append(0.4 * env * math.sin(2 * math.pi * freq * i / self.rate))
        return self._to_sound(samples)

    # ---- public API ----------------------------------------------------
    def play_slice(self):
        if self.enabled:
            self.slice_sound.play()

    def play_bomb(self):
        if self.enabled:
            self.bomb_sound.play()

    def play_game_over(self):
        if self.enabled:
            self.game_over_sound.play()
