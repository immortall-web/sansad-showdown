
from __future__ import annotations
import os
import sys
import time
import random
from typing import Dict, List, Optional, Set

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static
from textual.binding import Binding
from textual import events


# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------

def print_terminal_startup_banner() -> None:
    """Clear the terminal and show a short loading banner."""
    os.system("cls" if os.name == "nt" else "clear")
    banner = r"""
  __             __        __                     
/__`  /\  |\ | /__`  /\  |  \                    
.__/ /~~\ | \| .__/ /~~\ |__/                    
                                                 
          __        __        __   __            
         /__` |__| /  \ |  | |  \ /  \ |  | |\ | 
         .__/ |  | \__/ |/\| |__/ \__/ |/\| | \| 
                                                 
    """
    print(f"\033[1;36m{banner}\033[0m")
    print("\033[1;33m  ========================================================\033[0m")
    print("\033[1;32m   SANSAD-SHOWDOWN : PARLIAMENTARY FIGHTER \033[0m")
    print("\033[1;36m   GITHUB : https://github.com/sansad-showdown\033[0m")
    print("\033[1;36m   INSTAGRAM : https://instagram.com/pkmn.abhi\033[0m")
    print("\033[1;33m  ========================================================\033[0m")
    print("\n\033[1;35m[*] Game loading...\033[0m")
    time.sleep(5.5)
    os.system("cls" if os.name == "nt" else "clear")


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

class AudioEngine:
    """Simple procedural SFX engine using Pygame mixer (optional)."""

    def __init__(self) -> None:
        self.muted: bool = False
        self.initialized: bool = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.initialized = True
            except Exception as exc:
                print(f"[AudioEngine] Warning: {exc}")

    def play_sfx(self, sfx_type: str) -> None:
        if not self.initialized or self.muted:
            return
        try:
            sample_rate = 22050
            duration = 0.12
            if sfx_type == "punch":
                freq = 160
            elif sfx_type == "kick":
                freq = 90
            elif sfx_type == "super":
                freq = 440
                duration = 0.35
            elif sfx_type == "jump":
                freq = 320
                duration = 0.1
            else:
                freq = 200

            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                amplitude = 0.45 * (1.0 - t / duration)
                square = 1 if (int(t * freq * 2) % 2 == 0) else -1
                val = int(32767 * amplitude * square)
                buf.extend(val.to_bytes(2, byteorder="little", signed=True))
                buf.extend(val.to_bytes(2, byteorder="little", signed=True))

            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.play()
        except Exception:
            pass

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        if self.initialized:
            if self.muted:
                pygame.mixer.pause()
            else:
                pygame.mixer.unpause()
        return self.muted


CHARACTERS: Dict[str, Dict] = {
    "MitraMan": {
        "color": "#00ffff",
        "title": "The Holographic Reformer",
        "special_name": "Hologram Shield",
        "idle": [
            r"   __O__   ",
            r"  / /|\ \  ",
            r" |  | |  | ",
            r"   /   \   ",
            r"  /     \  ",
        ],
        "punching": [
            r"   __O===> ",
            r"  / /|     ",
            r" |  | |    ",
            r"   / \     ",
            r"  /   \    ",
        ],
        "kicking": [
            r"   __O__   ",
            r"  / /|\    ",
            r" |  |  |   ",
            r"   / \===> ",
            r"  /        ",
        ],
        "damaged": [
            r"   __X__   ",
            r"  \ \|/ /  ",
            r"   | | |   ",
            r"    / \    ",
            r"   /   \   ",
        ],
        "jumping": [
            r"   __O__   ",
            r"  / /|\ \  ",
            r" |  | |  | ",
            r"   /   \   ",
            r"  ^     ^  ",
        ],
    },
    "Yatra Boy": {
        "color": "#55ff55",
        "title": "The Relentless Walker",
        "special_name": "Marathon Dash",
        "idle": [
            r"    _A_    ",
            r"     //|\\ ",
            r"   (o o)   ",
            r"   / _ \   ",
            r"  //   \\  ",
        ],
        "punching": [
            r"    _A_==> ",
            r"   //|\\   ",
            r"  (o o)    ",
            r"   / _ \   ",
            r"  //   \\  ",
        ],
        "kicking": [
            r"    _A_    ",
            r"   //|\\   ",
            r"  (o o)    ",
            r"   / _ \==>",
            r"  //       ",
        ],
        "damaged": [
            r"    _X_    ",
            r"   \\|//   ",
            r"   (x x)   ",
            r"    / \    ",
            r"   // \\   ",
        ],
        "jumping": [
            r"    _A_    ",
            r"     //|\\ ",
            r"   (o o)   ",
            r"   / _ \   ",
            r"  ^     ^  ",
        ],
    },
    "Deedee": {
        "color": "#ff00ff",
        "title": "The Streetfighter Monarch",
        "special_name": "Monarch Blitz",
        "idle": [
            r"    _O_    ",
            r"   \\|//   ",
            r"    (o_o)  ",
            r"    / | \  ",
            r"   /  |  \ ",
        ],
        "punching": [
            r"    _O_==> ",
            r"   \\|//   ",
            r"    (o_o)  ",
            r"    / | \  ",
            r"   /  |    ",
        ],
        "kicking": [
            r"    _O_    ",
            r"   \\|//   ",
            r"    (o_o)  ",
            r"    / |==> ",
            r"   /  |    ",
        ],
        "damaged": [
            r"    _X_    ",
            r"   //|\\   ",
            r"    (x_x)  ",
            r"    / | \  ",
            r"      |    ",
        ],
        "jumping": [
            r"    _O_    ",
            r"   \\|//   ",
            r"    (o_o)  ",
            r"    / | \  ",
            r"   ^  |  ^ ",
        ],
    },
    "Tariff Taau": {
        "color": "#ffff00",
        "title": "The Tax Enforcer",
        "special_name": "GST Levy Blast",
        "idle": [
            r"   _[_]_   ",
            r"  / [o] \  ",
            r" |  |_|  | ",
            r"  \  #  /  ",
            r"   /   \   ",
        ],
        "punching": [
            r"   _[_]_==>",
            r"  / [o] \  ",
            r" |  |_|    ",
            r"  \  #     ",
            r"   /       ",
        ],
        "kicking": [
            r"   _[_]_   ",
            r"  / [o] \  ",
            r" |  |_|  | ",
            r"  \  #==>  ",
            r"   /       ",
        ],
        "damaged": [
            r"   _[X]_   ",
            r"  / [x] \  ",
            r" |  |_|  | ",
            r"  \  #  /  ",
            r"   / \ \   ",
        ],
        "jumping": [
            r"   _[_]_   ",
            r"  / [o] \  ",
            r" |  |_|  | ",
            r"  \  #  /  ",
            r"   ^   ^   ",
        ],
    },
    "Dozer Dada": {
        "color": "#ff8800",
        "title": "The Bulldozer Vanguard",
        "special_name": "Demolition Slam",
        "idle": [
            r"  [#####]  ",
            r"  | o o |  ",
            r" /| === |\ ",
            r"  |  |  |  ",
            r" /   |   \ ",
        ],
        "punching": [
            r"  [#####]==>",
            r"  | o o |  ",
            r" /| === |  ",
            r"  |  |     ",
            r" /   |     ",
        ],
        "kicking": [
            r"  [#####]  ",
            r"  | o o |  ",
            r" /| === |\ ",
            r"  |  |==>  ",
            r" /         ",
        ],
        "damaged": [
            r"  [#####]  ",
            r"  | x x |  ",
            r" /| === |\ ",
            r"  |  |  |  ",
            r" / \ / \ \ ",
        ],
        "jumping": [
            r"  [#####]  ",
            r"  | o o |  ",
            r" /| === |\ ",
            r"  |  |  |  ",
            r" ^   |   ^ ",
        ],
    },
    "Toll Man": {
        "color": "#0088ff",
        "title": "The FASTag Guardian",
        "special_name": "FASTag Barrier",
        "idle": [
            r"   |===|   ",
            r"   (o.o)   ",
            r"  / /|\ \  ",
            r"   / | \   ",
            r"  /  |  \  ",
        ],
        "punching": [
            r"   |===|==>",
            r"   (o.o)   ",
            r"  / /|     ",
            r"   / |     ",
            r"  /  |     ",
        ],
        "kicking": [
            r"   |===|   ",
            r"   (o.o)   ",
            r"  / /|\ \  ",
            r"   / |==>  ",
            r"  /        ",
        ],
        "damaged": [
            r"   |===|   ",
            r"   (x.x)   ",
            r"  \ \|/ /  ",
            r"   / | \   ",
            r"  /  |  \  ",
        ],
        "jumping": [
            r"   |===|   ",
            r"   (o.o)   ",
            r"  / /|\ \  ",
            r"   / | \   ",
            r"  ^  |  ^  ",
        ],
    },
}

ROSTER_KEYS: List[str] = list(CHARACTERS.keys())

CAMPAIGN_LEVELS: Dict[int, Dict] = {
    1: {"name": "Lok Sabha Floor", "cpu_boost": 1.0, "ai_speed": 0.11},
    2: {"name": "Rajya Sabha Gallery", "cpu_boost": 1.2, "ai_speed": 0.09},
    3: {"name": "Central Hall Debates", "cpu_boost": 1.4, "ai_speed": 0.08},
    4: {"name": "Supreme Court Steps", "cpu_boost": 1.6, "ai_speed": 0.07},
    5: {"name": "The Parliament Dome", "cpu_boost": 1.8, "ai_speed": 0.06},
    6: {"name": "Secret Parliamentary Bunker (BOSS)", "cpu_boost": 2.2, "ai_speed": 0.045},
}

MAX_CAMPAIGN_LEVEL = max(CAMPAIGN_LEVELS.keys())

# Movement constants
MOVE_STEP = 6
JUMP_HEIGHT = 3
JUMP_DURATION = 0.45
MIN_DISTANCE = 10
ARENA_WIDTH = 100


KEY_MAP_TEXT = """\
╔══════════════════════════════════════════════════════════════╗
║                    KEY MAPPING / CONTROLS                    ║
╠══════════════════════════════════════════════════════════════╣
║  PLAYER 1                                                    ║
║    Move Left / Right ..........  A  /  D                     ║
║    Jump .......................  W                           ║
║    Punch ......................  J                           ║
║    Kick .......................  K                           ║
║    Special Ability ............  I                           ║
║    Max Shakti Ultimate ........  L   (needs 100% Shakti)     ║
╠══════════════════════════════════════════════════════════════╣
║  PLAYER 2  (Versus mode only)                                ║
║    Move Left / Right ..........  ←  /  →                     ║
║    Jump .......................  ↑                           ║
║    Punch ......................  N                           ║
║    Kick .......................  M                           ║
║    Special Ability ............  ,  (comma)                  ║
║    Max Shakti Ultimate ........  .  (period)                 ║
╠══════════════════════════════════════════════════════════════╣
║  SYSTEM                                                      ║
║    Mute / Unmute Audio ........  T                           ║
║    Quit Match .................  Esc                         ║
╚══════════════════════════════════════════════════════════════╝"""

KEY_MAP_SHORT_1P = (
    "1P: [A/D] Move  [W] Jump  [J] Punch  [K] Kick  [I] Special  [L] Super"
)
KEY_MAP_SHORT_2P = (
    "2P: [←/→] Move  [↑] Jump  [N] Punch  [M] Kick  [,] Special  [.] Super"
)
KEY_MAP_SHORT_SYS = "[T] Mute   [Esc] Quit Match"



class HealthBar(Static):
    def update_health(self, hp: int) -> None:
        hp = max(0, min(100, hp))
        filled = int(hp / 5)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty
        self.update(f"HP: [{bar}] {hp}%")


class ShaktiGauge(Static):
    def update_shakti(self, shakti: int) -> None:
        shakti = max(0, min(100, shakti))
        filled = int(shakti / 10)
        empty = 10 - filled
        bar = "▓" * filled + "░" * empty
        status = " (MAX!)" if shakti >= 100 else ""
        self.update(f"SHAKTI: [{bar}] {shakti}%{status}")



class SplashDisclaimerScreen(Screen):
    BINDINGS = [Binding("enter", "start_game", "Proceed")]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("SANSAD-SHOWDOWN", id="splash_title"),
            Label("⚖️ SATIRE & TERMS ⚖️", id="splash_subtitle"),
            Static(
                "Welcome to Sansad-Showdown!\n"
                "⚠️ TERMS & CONDITIONS / SATIRE DISCLAIMER:\n"
                "All characters, names, and events in this game are entirely fictitious parodies\n"
                "created for entertainment purposes only.\n"
                "Any resemblance to real persons, living or dead, is purely coincidental.\n\n"
                "Press [ [ENTER] ] to Select Game Mode",
                id="splash_text",
            ),
            classes="center_box",
        )

    def action_start_game(self) -> None:
        self.app.push_screen(ModeSelectScreen())


class ModeSelectScreen(Screen):
    BINDINGS = [
        Binding("1", "mode_campaign", "Campaign Mode"),
        Binding("2", "mode_vs", "2-Player Versus"),
        Binding("3", "mode_survival", "Endless Survival"),
        Binding("c", "show_controls", "Controls"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("SELECT GAME MODE", id="splash_title"),
            Static(
                "\n[1] Press 1: Arcade Campaign Mode (6 Progressive Stages)\n"
                "[2] Press 2: Local 2-Player Versus (P1 vs P2 on same keyboard)\n"
                "[3] Press 3: Endless Survival Wave Mode\n"
                "[C] Press C: View Key Mapping / Controls\n",
                id="splash_text",
            ),
            classes="center_box",
        )

    def action_mode_campaign(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="campaign", level=1))

    def action_mode_vs(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="vs", level=1))

    def action_mode_survival(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="survival", level=1))

    def action_show_controls(self) -> None:
        self.app.push_screen(ControlsScreen())


class ControlsScreen(Screen):
    """Full key-mapping screen shown to the player."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "go_back", "Back"),
        Binding("c", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("KEY MAPPING / CONTROLS", id="splash_title"),
            Static(KEY_MAP_TEXT, id="controls_map"),
            Label("Press ENTER or ESC to go back", id="roster_footer"),
            classes="center_box",
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()


class RosterMenuScreen(Screen):
    BINDINGS = [
        Binding("left", "prev_char", "Previous"),
        Binding("right", "next_char", "Next"),
        Binding("enter", "select_char", "Select"),
    ]

    def __init__(self, mode: str, level: int = 1) -> None:
        super().__init__()
        self.mode = mode
        self.level = level
        self.selected_idx = 0
        self.p1_choice: Optional[str] = None

    def compose(self) -> ComposeResult:
        title = (
            f"SELECT {'P1' if self.mode == 'vs' and not self.p1_choice else 'NETA'}"
            f" — Mode: {self.mode.upper()}"
        )
        yield Container(
            Label(title, id="roster_header"),
            Horizontal(
                Static("", id="char_preview_box"),
                Vertical(
                    Label("", id="char_name_label"),
                    Label("", id="char_title_label"),
                    Label("", id="char_special_label"),
                    classes="roster_info",
                ),
                id="roster_flex",
            ),
            Label("← → to Browse   |   ENTER to Confirm", id="roster_footer"),
            id="roster_container",
        )

    def on_mount(self) -> None:
        self.update_display()

    def action_prev_char(self) -> None:
        self.selected_idx = (self.selected_idx - 1) % len(ROSTER_KEYS)
        self.update_display()

    def action_next_char(self) -> None:
        self.selected_idx = (self.selected_idx + 1) % len(ROSTER_KEYS)
        self.update_display()

    def update_display(self) -> None:
        name = ROSTER_KEYS[self.selected_idx]
        data = CHARACTERS[name]
        self.query_one("#char_preview_box", Static).update("\n".join(data["idle"]))
        name_lbl = self.query_one("#char_name_label", Label)
        name_lbl.update(f"▶ {name} ◀")
        name_lbl.styles.color = data["color"]
        self.query_one("#char_title_label", Label).update(data["title"])
        self.query_one("#char_special_label", Label).update(
            f"⚡ Special: {data['special_name']}"
        )

    def action_select_char(self) -> None:
        chosen = ROSTER_KEYS[self.selected_idx]
        if self.mode == "vs" and self.p1_choice is None:
            self.p1_choice = chosen
            self.query_one("#roster_header", Label).update("SELECT PLAYER 2 NETA")
            self.update_display()
        else:
            p1 = self.p1_choice if self.mode == "vs" else chosen
            if self.mode == "vs":
                p2 = chosen
            else:
                candidates = [c for c in ROSTER_KEYS if c != p1]
                p2 = random.choice(candidates) if candidates else p1
            self.app.push_screen(BattleArenaScreen(p1, p2, self.mode, self.level))


# ---------------------------------------------------------------------------
# Battle Arena — fixed movement + jump
# ---------------------------------------------------------------------------

class BattleArenaScreen(Screen):
    """Main fight screen with reliable keyboard movement."""

    # Keep bindings for the footer help text, but primary input is on_key
    BINDINGS = [
        Binding("t", "toggle_audio", "Mute [T]", show=True),
        Binding("escape", "forfeit", "Quit Match", show=True),
    ]

    def __init__(
        self, p1_char: str, p2_char: str, mode: str, level: int
    ) -> None:
        super().__init__()
        self.p1_name = p1_char
        self.p2_name = p2_char
        self.mode = mode
        self.level = max(1, min(level, MAX_CAMPAIGN_LEVEL))

        stage_data = CAMPAIGN_LEVELS.get(self.level, CAMPAIGN_LEVELS[MAX_CAMPAIGN_LEVEL])
        self.stage_name = stage_data["name"]
        self.cpu_boost = float(stage_data["cpu_boost"])
        self.ai_speed = float(stage_data["ai_speed"])

        # Positions (0 – 100)
        self.p1_x: float = 18.0
        self.p2_x: float = 72.0
        self.p1_y: int = 0          # 0 = ground, >0 = airborne
        self.p2_y: int = 0

        self.p1_hp = 100
        self.p2_hp = 100
        self.p1_shakti = 0
        self.p2_shakti = 0

        self.p1_state = "idle"
        self.p2_state = "idle"
        self.p1_facing = 1          # 1 = right, -1 = left
        self.p2_facing = -1

        self.podium_hp = 30
        self.game_over = False
        self.session_hits = 0
        self.survival_wave = 1 if mode == "survival" else 0

        # Jump state
        self.p1_jumping = False
        self.p2_jumping = False

        # Held keys for continuous movement (only movement keys)
        self._held: Set[str] = set()

        # Timer handles so we can stop them cleanly
        self._ai_timer = None
        self._move_timer = None

    def compose(self) -> ComposeResult:
        p2_label = "2P" if self.mode == "vs" else "CPU"
        yield Header()
        yield Container(
            Horizontal(
                Vertical(
                    Label(f"{self.p1_name} (1P)", id="p1_title_lbl"),
                    HealthBar(id="p1_hp_bar"),
                    ShaktiGauge(id="p1_shakti_bar"),
                    classes="hud_panel",
                ),
                Vertical(
                    Label(
                        f"🏟️ {self.stage_name}\nPodium HP: {self.podium_hp}",
                        id="stage_lbl",
                    ),
                    classes="hud_center",
                ),
                Vertical(
                    Label(f"{self.p2_name} ({p2_label})", id="p2_title_lbl"),
                    HealthBar(id="p2_hp_bar"),
                    ShaktiGauge(id="p2_shakti_bar"),
                    classes="hud_panel",
                ),
                id="hud_container",
            ),
            Static("", id="arena_canvas"),
            Static("Fight!", id="battle_log"),
            Static(self._controls_text(), id="control_instructions"),
            id="arena_main",
        )
        yield Footer()

    def _controls_text(self) -> str:
        """Always show key mapping to the player during battle."""
        if self.mode == "vs":
            return (
                f"{KEY_MAP_SHORT_1P}\n"
                f"{KEY_MAP_SHORT_2P}   |  {KEY_MAP_SHORT_SYS}"
            )
        return (
            f"{KEY_MAP_SHORT_1P}   |  {KEY_MAP_SHORT_SYS}\n"
            "CPU is active — fight!"
        )

    def on_mount(self) -> None:
        self.query_one("#p1_title_lbl", Label).styles.color = CHARACTERS[self.p1_name]["color"]
        self.query_one("#p2_title_lbl", Label).styles.color = CHARACTERS[self.p2_name]["color"]
        self.query_one("#p1_hp_bar", HealthBar).update_health(self.p1_hp)
        self.query_one("#p2_hp_bar", HealthBar).update_health(self.p2_hp)
        self.query_one("#p1_shakti_bar", ShaktiGauge).update_shakti(self.p1_shakti)
        self.query_one("#p2_shakti_bar", ShaktiGauge).update_shakti(self.p2_shakti)
        self.render_arena()

        # Continuous movement poll (makes held keys feel responsive)
        self._move_timer = self.set_interval(0.05, self._movement_tick)

        if self.mode != "vs":
            self._ai_timer = self.set_interval(self.ai_speed, self.cpu_ai_tick)

    # ------------------------------------------------------------------
    # Reliable key handling (primary input path)
    # ------------------------------------------------------------------

    def on_key(self, event: events.Key) -> None:
        if self.game_over:
            return

        key = event.key.lower()

        # Only track movement keys as held (prevents attack spam from hold)
        move_keys = {"a", "d", "left", "right"}
        if key in move_keys:
            self._held.add(key)

        # ---- Player 1 ----
        if key == "a":
            self._move_p1(-MOVE_STEP)
        elif key == "d":
            self._move_p1(+MOVE_STEP)
        elif key == "w":
            self._jump_p1()
        elif key == "j":
            self._p1_punch()
        elif key == "k":
            self._p1_kick()
        elif key == "i":
            self._p1_special()
        elif key == "l":
            self._p1_super()

        # ---- Player 2 (versus only) ----
        elif self.mode == "vs":
            if key == "left":
                self._move_p2(-MOVE_STEP)
            elif key == "right":
                self._move_p2(+MOVE_STEP)
            elif key == "up":
                self._jump_p2()
            elif key == "n":
                self._p2_punch()
            elif key == "m":
                self._p2_kick()
            elif key in (",", "comma"):
                self._p2_special()
            elif key in (".", "period", "full_stop"):
                self._p2_super()

        # Always re-render after any action
        self.render_arena()

    def on_key_up(self, event: events.Key) -> None:
        """Clear held movement keys when released (best-effort; not all terminals send key-up)."""
        key = event.key.lower()
        self._held.discard(key)

    def _movement_tick(self) -> None:
        """Called frequently so held keys keep moving the character."""
        if self.game_over:
            self._held.clear()
            return
        if not self._held:
            return
        moved = False
        if "a" in self._held:
            self._move_p1(-MOVE_STEP)
            moved = True
        if "d" in self._held:
            self._move_p1(+MOVE_STEP)
            moved = True
        if self.mode == "vs":
            if "left" in self._held:
                self._move_p2(-MOVE_STEP)
                moved = True
            if "right" in self._held:
                self._move_p2(+MOVE_STEP)
                moved = True
        if moved:
            self.render_arena()

    # ------------------------------------------------------------------
    # Movement primitives
    # ------------------------------------------------------------------

    def _move_p1(self, delta: float) -> None:
        if self.game_over:
            return
        new_x = self.p1_x + delta
        new_x = max(0.0, min(ARENA_WIDTH - MIN_DISTANCE, new_x))

        # Keep minimum distance from P2
        if new_x > self.p2_x - MIN_DISTANCE:
            new_x = self.p2_x - MIN_DISTANCE

        self.p1_x = new_x
        self.p1_facing = 1 if delta > 0 else -1

        if self.p1_state not in ("punching", "kicking", "jumping", "damaged"):
            self.p1_state = "idle"

    def _move_p2(self, delta: float) -> None:
        if self.game_over or self.mode != "vs":
            return
        new_x = self.p2_x + delta
        new_x = max(MIN_DISTANCE, min(float(ARENA_WIDTH), new_x))

        if new_x < self.p1_x + MIN_DISTANCE:
            new_x = self.p1_x + MIN_DISTANCE

        self.p2_x = new_x
        self.p2_facing = 1 if delta > 0 else -1

        if self.p2_state not in ("punching", "kicking", "jumping", "damaged"):
            self.p2_state = "idle"

    def _jump_p1(self) -> None:
        if self.game_over or self.p1_jumping:
            return
        self.p1_jumping = True
        self.p1_y = JUMP_HEIGHT
        self.p1_state = "jumping"
        self.app.audio.play_sfx("jump")
        self.set_timer(JUMP_DURATION, self._land_p1)

    def _land_p1(self) -> None:
        self.p1_y = 0
        self.p1_jumping = False
        if self.p1_state == "jumping":
            self.p1_state = "idle"
        self.render_arena()

    def _jump_p2(self) -> None:
        if self.game_over or self.mode != "vs" or self.p2_jumping:
            return
        self.p2_jumping = True
        self.p2_y = JUMP_HEIGHT
        self.p2_state = "jumping"
        self.app.audio.play_sfx("jump")
        self.set_timer(JUMP_DURATION, self._land_p2)

    def _land_p2(self) -> None:
        self.p2_y = 0
        self.p2_jumping = False
        if self.p2_state == "jumping":
            self.p2_state = "idle"
        self.render_arena()

    # ------------------------------------------------------------------
    # Rendering (with vertical offset for jump)
    # ------------------------------------------------------------------

    def render_arena(self) -> None:
        if self.game_over:
            return

        p1_art = CHARACTERS[self.p1_name].get(
            self.p1_state, CHARACTERS[self.p1_name]["idle"]
        )
        p2_art = CHARACTERS[self.p2_name].get(
            self.p2_state, CHARACTERS[self.p2_name]["idle"]
        )

        term_width = 80
        usable = term_width - 12

        p1_pos = int((self.p1_x / ARENA_WIDTH) * usable)
        p2_pos = int((self.p2_x / ARENA_WIDTH) * usable)

        # Safety clamp so they never visually overlap
        if p1_pos >= p2_pos - 11:
            p1_pos = max(0, p2_pos - 12)

        # Build 7 rows so jump has room (rows 0-1 are sky)
        rows: List[List[str]] = [[" "] * term_width for _ in range(7)]

        def blit(art: List[str], col: int, row_offset: int) -> None:
            for r, line in enumerate(art):
                target_row = 2 + r - row_offset   # ground art starts at row 2
                if 0 <= target_row < 7:
                    for c, ch in enumerate(line):
                        pos = col + c
                        if 0 <= pos < term_width and ch != " ":
                            rows[target_row][pos] = ch

        blit(p1_art, p1_pos, self.p1_y)
        blit(p2_art, p2_pos, self.p2_y)

        # Podium hazard in the middle on the ground
        if self.podium_hp > 0:
            mid = term_width // 2
            if 0 <= mid < term_width:
                rows[5][mid] = "🏛️"
                rows[6][mid] = "█"

        # Floor line
        floor = ["="] * term_width
        canvas = "\n".join("".join(r) for r in rows) + "\n" + "".join(floor)

        try:
            widget = self.query_one("#arena_canvas", Static)
            widget.update(canvas)
            widget.refresh()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Combat helpers
    # ------------------------------------------------------------------

    def _in_range(self, ax: float, dx: float, reach: int = 16) -> bool:
        return abs(dx - ax) <= reach

    def _apply_damage(self, target: str, amount: int, log_msg: str) -> None:
        if target == "p2":
            self.p2_hp = max(0, self.p2_hp - amount)
            self.p2_state = "damaged"
            self.p1_shakti = min(100, self.p1_shakti + max(6, amount // 2))
            # small knockback
            self.p2_x = min(ARENA_WIDTH, self.p2_x + 3)
        else:
            self.p1_hp = max(0, self.p1_hp - amount)
            self.p1_state = "damaged"
            self.p2_shakti = min(100, self.p2_shakti + max(6, amount // 2))
            self.p1_x = max(0, self.p1_x - 3)
        self.query_one("#battle_log", Static).update(log_msg)

    def _damage_podium(self, amount: int = 12) -> None:
        if self.podium_hp > 0:
            self.podium_hp = max(0, self.podium_hp - amount)
            self.query_one("#stage_lbl", Label).update(
                f"🏟️ {self.stage_name}\nPodium HP: {self.podium_hp}"
            )

    def update_hud(self) -> None:
        self.query_one("#p1_hp_bar", HealthBar).update_health(self.p1_hp)
        self.query_one("#p2_hp_bar", HealthBar).update_health(self.p2_hp)
        self.query_one("#p1_shakti_bar", ShaktiGauge).update_shakti(self.p1_shakti)
        self.query_one("#p2_shakti_bar", ShaktiGauge).update_shakti(self.p2_shakti)
        self.check_win_condition()

    def reset_states(self) -> None:
        if self.game_over:
            return
        if self.p1_y == 0 and self.p1_state != "jumping":
            self.p1_state = "idle"
        if self.p2_y == 0 and self.p2_state != "jumping":
            self.p2_state = "idle"
        self.render_arena()

    # ------------------------------------------------------------------
    # Player 1 combat
    # ------------------------------------------------------------------

    def _p1_punch(self) -> None:
        if self.game_over:
            return
        self.app.audio.play_sfx("punch")
        self.p1_state = "punching"
        self.session_hits += 1
        if self._in_range(self.p1_x, self.p2_x, 16):
            self._apply_damage("p2", 8, f"💥 {self.p1_name} punches!")
        else:
            self.query_one("#battle_log", Static).update(f"{self.p1_name} swings and misses!")
        self.update_hud()
        self.set_timer(0.22, self.reset_states)

    def _p1_kick(self) -> None:
        if self.game_over:
            return
        self.app.audio.play_sfx("kick")
        self.p1_state = "kicking"
        self.session_hits += 1
        if self._in_range(self.p1_x, self.p2_x, 17):
            self._apply_damage("p2", 12, f"💥 {self.p1_name} lands a kick!")
        else:
            self.query_one("#battle_log", Static).update(f"{self.p1_name}'s kick misses!")
        self.update_hud()
        self.set_timer(0.25, self.reset_states)

    def _p1_special(self) -> None:
        if self.game_over:
            return
        self.app.audio.play_sfx("super")
        self.p1_state = "punching"
        name = CHARACTERS[self.p1_name]["special_name"]
        if self._in_range(self.p1_x, self.p2_x, 26):
            self._apply_damage("p2", 22, f"⚡ {self.p1_name} uses {name}!")
        else:
            self.query_one("#battle_log", Static).update(f"{name} misses!")
        self._damage_podium(14)
        self.update_hud()
        self.set_timer(0.3, self.reset_states)

    def _p1_super(self) -> None:
        if self.game_over:
            return
        if self.p1_shakti < 100:
            self.query_one("#battle_log", Static).update("Shakti not full! Need 100%.")
            return
        self.app.audio.play_sfx("super")
        self.p1_state = "punching"
        self.p2_hp = max(0, self.p2_hp - 45)
        self.p1_shakti = 0
        self.p2_state = "damaged"
        self.p2_x = min(ARENA_WIDTH, self.p2_x + 6)
        self.query_one("#battle_log", Static).update("🔥 MAX SHAKTI ULTIMATE! 45 DMG!")
        self.update_hud()
        self.set_timer(0.35, self.reset_states)
        self.check_win_condition()

    # ------------------------------------------------------------------
    # Player 2 combat
    # ------------------------------------------------------------------

    def _p2_punch(self) -> None:
        if self.game_over or self.mode != "vs":
            return
        self.app.audio.play_sfx("punch")
        self.p2_state = "punching"
        if self._in_range(self.p2_x, self.p1_x, 16):
            self._apply_damage("p1", 8, f"💥 {self.p2_name} (2P) punches!")
        self.update_hud()
        self.set_timer(0.22, self.reset_states)

    def _p2_kick(self) -> None:
        if self.game_over or self.mode != "vs":
            return
        self.app.audio.play_sfx("kick")
        self.p2_state = "kicking"
        if self._in_range(self.p2_x, self.p1_x, 17):
            self._apply_damage("p1", 12, f"💥 {self.p2_name} (2P) kicks!")
        self.update_hud()
        self.set_timer(0.25, self.reset_states)

    def _p2_special(self) -> None:
        if self.game_over or self.mode != "vs":
            return
        self.app.audio.play_sfx("super")
        self.p2_state = "punching"
        name = CHARACTERS[self.p2_name]["special_name"]
        if self._in_range(self.p2_x, self.p1_x, 26):
            self._apply_damage("p1", 22, f"⚡ {self.p2_name} (2P) uses {name}!")
        else:
            self.query_one("#battle_log", Static).update(f"{name} (2P) misses!")
        self._damage_podium(14)
        self.update_hud()
        self.set_timer(0.3, self.reset_states)

    def _p2_super(self) -> None:
        if self.game_over or self.mode != "vs":
            return
        if self.p2_shakti < 100:
            self.query_one("#battle_log", Static).update("2P Shakti not full!")
            return
        self.app.audio.play_sfx("super")
        self.p2_state = "punching"
        self.p1_hp = max(0, self.p1_hp - 45)
        self.p2_shakti = 0
        self.p1_state = "damaged"
        self.p1_x = max(0, self.p1_x - 6)
        self.query_one("#battle_log", Static).update("🔥 2P MAX SHAKTI ULTIMATE!")
        self.update_hud()
        self.set_timer(0.35, self.reset_states)
        self.check_win_condition()

    def action_toggle_audio(self) -> None:
        muted = self.app.audio.toggle_mute()
        self.query_one("#battle_log", Static).update(
            "Audio Muted." if muted else "Audio Resumed."
        )

    def action_forfeit(self) -> None:
        self.app.push_screen(SplashDisclaimerScreen())

    # ------------------------------------------------------------------
    # CPU AI
    # ------------------------------------------------------------------

    def cpu_ai_tick(self) -> None:
        if self.game_over or self.mode == "vs":
            return

        dist = self.p2_x - self.p1_x

        if dist > 18:
            self.p2_x = max(self.p1_x + MIN_DISTANCE, self.p2_x - 5)
            self.p2_facing = -1
        elif dist < 9:
            self.p2_x = min(ARENA_WIDTH, self.p2_x + 4)
            self.p2_facing = 1
        else:
            choice = random.random()
            base = int(9 * self.cpu_boost)

            if choice < 0.50:
                self.p2_state = "punching"
                self.app.audio.play_sfx("punch")
                self.p1_hp = max(0, self.p1_hp - base)
                self.p1_state = "damaged"
                self.p1_x = max(0, self.p1_x - 2)
                self.p2_shakti = min(100, self.p2_shakti + 7)
                self.query_one("#battle_log", Static).update(
                    f"⚠️ CPU {self.p2_name} hits for {base}!"
                )
            elif choice < 0.80:
                self.p2_state = "kicking"
                self.app.audio.play_sfx("kick")
                dmg = int(base * 1.3)
                self.p1_hp = max(0, self.p1_hp - dmg)
                self.p1_state = "damaged"
                self.p2_shakti = min(100, self.p2_shakti + 11)
                self.query_one("#battle_log", Static).update(
                    f"⚠️ CPU {self.p2_name} kicks hard!"
                )
            else:
                if self.p2_shakti >= 100:
                    self.p2_state = "punching"
                    self.app.audio.play_sfx("super")
                    self.p1_hp = max(0, self.p1_hp - 35)
                    self.p2_shakti = 0
                    self.p1_state = "damaged"
                    self.query_one("#battle_log", Static).update("💥 CPU ULTIMATE!")
                else:
                    self.p2_state = "punching"
                    self.app.audio.play_sfx("super")
                    dmg = int(16 * self.cpu_boost)
                    self.p1_hp = max(0, self.p1_hp - dmg)
                    self.p1_state = "damaged"
                    self.p2_shakti = min(100, self.p2_shakti + 12)
                    sp = CHARACTERS[self.p2_name]["special_name"]
                    self.query_one("#battle_log", Static).update(f"⚡ CPU uses {sp}!")

            self.update_hud()
            self.set_timer(0.22, self.reset_states)

        self.render_arena()

    # ------------------------------------------------------------------
    # Win / Survival
    # ------------------------------------------------------------------

    def _stop_timers(self) -> None:
        """Stop repeating timers to avoid stacked AI / movement loops."""
        self._held.clear()
        if self._ai_timer is not None:
            try:
                self._ai_timer.stop()
            except Exception:
                pass
            self._ai_timer = None
        if self._move_timer is not None:
            try:
                self._move_timer.stop()
            except Exception:
                pass
            self._move_timer = None

    def check_win_condition(self) -> None:
        if self.game_over:
            return

        if self.p1_hp <= 0:
            self.game_over = True
            self._held.clear()
            self.query_one("#battle_log", Static).update(
                "💀 DEFEAT! You lost the parliamentary majority."
            )
            self.set_timer(
                1.8,
                lambda: self.app.push_screen(
                    PostMatchScreen(
                        won=False,
                        level=self.level,
                        mode=self.mode,
                        hits=self.session_hits,
                        wave=self.survival_wave,
                    )
                ),
            )
        elif self.p2_hp <= 0:
            self.game_over = True
            self._held.clear()
            jumla = random.choice([
                "Chai bhaiya demanded compensation for broken cups.",
                "A stray cow ate a manifesto mid-fight.",
                "Opposition walked out after the knockout.",
                "Exit polls were, as usual, completely wrong.",
            ])
            self.query_one("#battle_log", Static).update(f"🏆 YOU WIN! {jumla}")

            if self.mode == "survival":
                self.set_timer(1.4, self._next_survival_wave)
            else:
                self.set_timer(
                    1.8,
                    lambda: self.app.push_screen(
                        PostMatchScreen(
                            won=True,
                            level=self.level,
                            mode=self.mode,
                            hits=self.session_hits,
                            wave=self.survival_wave,
                        )
                    ),
                )

    def _next_survival_wave(self) -> None:
        self.survival_wave += 1
        self.game_over = False
        self.p2_hp = 100
        self.p2_shakti = 0
        self.p2_x = 75.0
        self.p2_y = 0
        self.p2_jumping = False
        self.p2_state = "idle"
        self.cpu_boost = min(3.0, 1.0 + self.survival_wave * 0.18)
        self.ai_speed = max(0.04, 0.11 - self.survival_wave * 0.007)

        candidates = [c for c in ROSTER_KEYS if c != self.p1_name]
        self.p2_name = random.choice(candidates) if candidates else self.p1_name

        self.query_one("#p2_title_lbl", Label).update(f"{self.p2_name} (CPU)")
        self.query_one("#p2_title_lbl", Label).styles.color = CHARACTERS[self.p2_name]["color"]
        self.query_one("#stage_lbl", Label).update(
            f"🏟️ Survival Wave {self.survival_wave}\nPodium HP: {self.podium_hp}"
        )
        self.query_one("#battle_log", Static).update(
            f"🌊 Wave {self.survival_wave}! New challenger: {self.p2_name}"
        )
        self.update_hud()
        self.render_arena()

        # Restart AI timer cleanly (stop old one first to avoid stacking)
        if self._ai_timer is not None:
            try:
                self._ai_timer.stop()
            except Exception:
                pass
        self._ai_timer = self.set_interval(self.ai_speed, self.cpu_ai_tick)

        # Ensure movement timer is still running
        if self._move_timer is None:
            self._move_timer = self.set_interval(0.05, self._movement_tick)


class PostMatchScreen(Screen):
    def __init__(
        self,
        won: bool,
        level: int,
        mode: str,
        hits: int,
        wave: int = 0,
    ) -> None:
        super().__init__()
        self.won = won
        self.level = level
        self.mode = mode
        self.hits = hits
        self.wave = wave

    def compose(self) -> ComposeResult:
        if self.mode == "survival":
            title = (
                f"🌊 SURVIVED {self.wave} WAVE(S)!"
                if self.won
                else f"💀 FELL AT WAVE {self.wave}"
            )
            subtext = f"Total Hits: {self.hits}"
            option1 = "[1] Press 1: Try Survival Again"
        else:
            title = "👑 STAGE CLEARED!" if self.won else "💀 PARLIAMENTARY DEFEAT!"
            subtext = f"Total Hits: {self.hits}  |  Stage: {self.level}"
            if self.won and self.mode == "campaign" and self.level < MAX_CAMPAIGN_LEVEL:
                option1 = "[1] Press 1: Next Stage"
            else:
                option1 = "[1] Press 1: Rematch / Retry"

        yield Container(
            Label(title, id="splash_title"),
            Label(subtext, id="splash_subtitle"),
            Static(
                f"\n{option1}\n"
                "[2] Press 2: Change Neta / Mode Menu\n"
                "[3] Press 3: Quit Game\n",
                id="splash_text",
            ),
            classes="center_box",
        )

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "1":
            if self.mode == "campaign" and self.won:
                next_lvl = min(self.level + 1, MAX_CAMPAIGN_LEVEL)
            else:
                next_lvl = self.level
            self.app.push_screen(RosterMenuScreen(mode=self.mode, level=next_lvl))
        elif key == "2":
            self.app.push_screen(SplashDisclaimerScreen())
        elif key == "3":
            self.app.exit()


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

class SansadApp(App):
    """Main application — loads styles from sansad.css next to this file."""

    CSS_PATH = "sansad.css"

    def on_mount(self) -> None:
        self.audio = AudioEngine()
        self.push_screen(SplashDisclaimerScreen())


if __name__ == "__main__":
    # Ensure we run from the directory that contains Sansad.py + sansad.css
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print_terminal_startup_banner()
    app = SansadApp()
    app.run()
