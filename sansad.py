import os
import sys
import time
import random
from typing import Dict, List, Tuple, Optional

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


def print_terminal_startup_banner() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
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
    time.sleep(6.5)
    os.system('cls' if os.name == 'nt' else 'clear')


class AudioEngine:
    def __init__(self) -> None:
        self.muted: bool = False
        self.initialized: bool = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.initialized = True
            except Exception as e:
                print(f"[AudioEngine] Warning: {e}")

    def play_sfx(self, sfx_type: str) -> None:
        if not self.initialized or self.muted:
            return
        try:
            sample_rate = 22050
            duration = 0.15
            freq = 150 if sfx_type == "punch" else (90 if sfx_type == "kick" else (440 if sfx_type == "super" else 200))
            if sfx_type == "super":
                duration = 0.4
            
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                val = int(32767 * 0.5 * (1 - t / duration) * (1 if (int(t * freq * 2) % 2 == 0) else -1))
                buf.extend(val.to_bytes(2, byteorder='little', signed=True))
                buf.extend(val.to_bytes(2, byteorder='little', signed=True))
            
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.play()
        except Exception:
            pass

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        if self.initialized:
            if self.muted: pygame.mixer.pause()
            else: pygame.mixer.unpause()
        return self.muted


CHARACTERS: Dict[str, Dict[str, any]] = {
    "MitraMan": {
        "color": "#00ffff", "title": "The Holographic Reformer", "special_name": "Hologram Shield",
        "idle": [r"   __O__   ", r"  / /|\ \  ", r" |  | |  | ", r"   /   \   ", r"  /     \  "],
        "punching": [r"   __O===> ", r"  / /|     ", r" |  | |    ", r"   / \     ", r"  /   \    "],
        "kicking": [r"   __O__   ", r"  / /|\    ", r" |  |  |   ", r"   / \===> ", r"  /        "],
        "damaged": [r"   __X__   ", r"  \ \|/ /  ", r"   | | |   ", r"    / \    ", r"   /   \   "]
    },
    "Yatra Boy": {
        "color": "#55ff55", "title": "The Relentless Walker", "special_name": "Marathon Dash",
        "idle": [r"    _A_    ", r"     //|\\ ", r"   (o o)   ", r"   / _ \   ", r"  //   \\  "],
        "punching": [r"    _A_==> ", r"   //|\\   ", r"  (o o)    ", r"   / _ \   ", r"  //   \\  "],
        "kicking": [r"    _A_    ", r"   //|\\   ", r"  (o o)    ", r"   / _ \==>", r"  //       "],
        "damaged": [r"    _X_    ", r"   \\|//   ", r"   (x x)   ", r"    / \    ", r"   // \\   "]
    },
    "Deedee": {
        "color": "#ff00ff", "title": "The Streetfighter Monarch", "special_name": "Monarch Blitz",
        "idle": [r"    _O_    ", r"   \\|//   ", r"    (o_o)  ", r"    / | \  ", r"   /  |  \ "],
        "punching": [r"    _O_==> ", r"   \\|//   ", r"    (o_o)  ", r"    / | \  ", r"   /  |    "],
        "kicking": [r"    _O_    ", r"   \\|//   ", r"    (o_o)  ", r"    / |==> ", r"   /  |    "],
        "damaged": [r"    _X_    ", r"   //|\\   ", r"    (x_x)  ", r"    / | \  ", r"      |    "]
    },
    "Tariff Taau": {
        "color": "#ffff00", "title": "The Tax Enforcer", "special_name": "GST Levy Blast",
        "idle": [r"   _[_]_   ", r"  / [o] \  ", r" |  |_|  | ", r"  \  #  /  ", r"   /   \   "],
        "punching": [r"   _[_]_==>", r"  / [o] \  ", r" |  |_|    ", r"  \  #     ", r"   /       "],
        "kicking": [r"   _[_]_   ", r"  / [o] \  ", r" |  |_|  | ", r"  \  #==>  ", r"   /       "],
        "damaged": [r"   _[X]_   ", r"  / [x] \  ", r" |  |_|  | ", r"  \  #  /  ", r"   / \ \   "]
    },
    "Dozer Dada": {
        "color": "#ff8800", "title": "The Bulldozer Vanguard", "special_name": "Demolition Slam",
        "idle": [r"  [#####]  ", r"  | o o |  ", r" /| === |\ ", r"  |  |  |  ", r" /   |   \ "],
        "punching": [r"  [#####]==>", r"  | o o |  ", r" /| === |  ", r"  |  |     ", r" /   |     "],
        "kicking": [r"  [#####]  ", r"  | o o |  ", r" /| === |\ ", r"  |  |==>  ", r" /         "],
        "damaged": [r"  [#####]  ", r"  | x x |  ", r" /| === |\ ", r"  |  |  |  ", r" / \ / \ \ "]
    },
    "Toll Man": {
        "color": "#0088ff", "title": "The FASTag Guardian", "special_name": "FASTag Barrier",
        "idle": [r"   |===|   ", r"   (o.o)   ", r"  / /|\ \  ", r"   / | \   ", r"  /  |  \  "],
        "punching": [r"   |===|==>", r"   (o.o)   ", r"  / /|     ", r"   / |     ", r"  /  |     "],
        "kicking": [r"   |===|   ", r"   (o.o)   ", r"  / /|\ \  ", r"   / |==>  ", r"  /        "],
        "damaged": [r"   |===|   ", r"   (x.x)   ", r"  \ \|/ /  ", r"   / | \   ", r"  /  |  \  "]
    }
}

ROSTER_KEYS = list(CHARACTERS.keys())
CAMPAIGN_LEVELS = {
    1: {"name": "Lok Sabha Floor", "cpu_boost": 1.0, "ai_speed": 0.12},
    2: {"name": "Rajya Sabha Gallery", "cpu_boost": 1.2, "ai_speed": 0.10},
    3: {"name": "Central Hall Debates", "cpu_boost": 1.4, "ai_speed": 0.08},
    4: {"name": "Supreme Court Steps", "cpu_boost": 1.6, "ai_speed": 0.07},
    5: {"name": "The Parliament Dome", "cpu_boost": 1.8, "ai_speed": 0.06},
    6: {"name": "Secret Parliamentary Bunker (BOSS)", "cpu_boost": 2.2, "ai_speed": 0.04},
}



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
        status = " (MAX SHAKTI!)" if shakti >= 100 else ""
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
                "created for entertainment purposes only \n"
                "Any resemblance to real persons, living or dead, is purely coincidental.\n\n"
                "Press [ ENTER ] to Select Game Mode",
                id="splash_text"
            ),
            classes="center_box"
        )

    def action_start_game(self) -> None:
        self.app.push_screen(ModeSelectScreen())


class ModeSelectScreen(Screen):
    BINDINGS = [
        Binding("1", "mode_campaign", "Campaign Mode"),
        Binding("2", "mode_vs", "2-Player Versus"),
        Binding("3", "mode_survival", "Endless Survival"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("SELECT GAME MODE", id="splash_title"),
            Static(
                "\n[1] Press 1: Arcade Campaign Mode (6 Progressive Stages)\n"
                "[2] Press 2: Local 2-Player Versus (P1 vs P2 on same keyboard)\n"
                "[3] Press 3: Endless Survival Wave Mode\n",
                id="splash_text"
            ),
            classes="center_box"
        )

    def action_mode_campaign(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="campaign", level=1))

    def action_mode_vs(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="vs", level=1))

    def action_mode_survival(self) -> None:
        self.app.push_screen(RosterMenuScreen(mode="survival", level=1))


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
        title = f"SELECT {'P1' if self.mode == 'vs' and not self.p1_choice else 'NETA'} — Mode: {self.mode.upper()}"
        yield Container(
            Label(title, id="roster_header"),
            Horizontal(
                Static("", id="char_preview_box"),
                Vertical(
                    Label("", id="char_name_label"),
                    Label("", id="char_title_label"),
                    Label("", id="char_special_label"),
                    classes="roster_info"
                ),
                id="roster_flex"
            ),
            Label("Arrows to Browse, Press ENTER to Confirm", id="roster_footer"),
            id="roster_container"
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
        self.query_one("#char_special_label", Label).update(f"⚡ Special: {data['special_name']}")

    def action_select_char(self) -> None:
        chosen = ROSTER_KEYS[self.selected_idx]
        if self.mode == "vs" and not self.p1_choice:
            self.p1_choice = chosen
            self.query_one("#roster_header", Label).update("SELECT PLAYER 2 NETA")
        else:
            p1 = self.p1_choice if self.mode == "vs" else chosen
            p2 = chosen if self.mode == "vs" else (random.choice([c for c in ROSTER_KEYS if c != p1]))
            self.app.push_screen(BattleArenaScreen(p1, p2, self.mode, self.level))


class BattleArenaScreen(Screen):
    BINDINGS = [
        Binding("a", "p1_left", "P1 Left", show=False),
        Binding("d", "p1_right", "P1 Right", show=False),
        Binding("j", "p1_punch", "P1 Punch [J]", show=True),
        Binding("k", "p1_kick", "P1 Kick [K]", show=True),
        Binding("i", "p1_special", "P1 Special [I]", show=True),
        Binding("l", "p1_super", "P1 Super [L]", show=True),
        Binding("left", "p2_left", "P2 Left", show=False),
        Binding("right", "p2_right", "P2 Right", show=False),
        Binding("n", "p2_punch", "P2 Punch [N]", show=True),
        Binding("m", "p2_kick", "P2 Kick [M]", show=True),
        Binding("t", "toggle_audio", "Mute [T]", show=True),
    ]

    def __init__(self, p1_char: str, p2_char: str, mode: str, level: int) -> None:
        super().__init__()
        self.p1_name = p1_char
        self.p2_name = p2_char
        self.mode = mode
        self.level = level
        
        stage_data = CAMPAIGN_LEVELS.get(level, CAMPAIGN_LEVELS[6])
        self.stage_name = stage_data["name"]
        self.cpu_boost = stage_data["cpu_boost"]
        self.ai_speed = stage_data["ai_speed"]
        
        self.p1_x = 20
        self.p2_x = 70
        self.p1_hp = 100
        self.p2_hp = 100
        self.p1_shakti = 0
        self.p2_shakti = 0
        
        self.p1_state = "idle"
        self.p2_state = "idle"
        self.podium_hp = 30
        self.game_over = False
        self.session_hits = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Vertical(
                    Label(f"{self.p1_name} (1P)", id="p1_title_lbl"),
                    HealthBar(id="p1_hp_bar"),
                    ShaktiGauge(id="p1_shakti_bar"),
                    classes="hud_panel"
                ),
                Vertical(
                    Label(f"🏟️ {self.stage_name}\nPodium HP: {self.podium_hp}", id="stage_lbl"),
                    classes="hud_center"
                ),
                Vertical(
                    Label(f"{self.p2_name} ({'2P' if self.mode == 'vs' else 'CPU'})", id="p2_title_lbl"),
                    HealthBar(id="p2_hp_bar"),
                    ShaktiGauge(id="p2_shakti_bar"),
                    classes="hud_panel"
                ),
                id="hud_container"
            ),
            Static("", id="arena_canvas"),
            Static("Sansad-Showdown Arena Active!", id="battle_log"),
            Static(
                "1P: [A/D] Move | [J] Punch | [K] Kick | [I] Special | [L] Super\n"
                + ("2P: [Left/Right] Move | [N] Punch | [M] Kick" if self.mode == "vs" else "CPU Active AI FSM"),
                id="control_instructions"
            ),
            id="arena_main"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#p1_title_lbl", Label).styles.color = CHARACTERS[self.p1_name]["color"]
        self.query_one("#p2_title_lbl", Label).styles.color = CHARACTERS[self.p2_name]["color"]
        self.query_one("#p1_hp_bar", HealthBar).update_health(self.p1_hp)
        self.query_one("#p2_hp_bar", HealthBar).update_health(self.p2_hp)
        self.query_one("#p1_shakti_bar", ShaktiGauge).update_shakti(self.p1_shakti)
        self.query_one("#p2_shakti_bar", ShaktiGauge).update_shakti(self.p2_shakti)
        self.render_arena()
        
        if self.mode != "vs":
            self.set_interval(self.ai_speed, self.cpu_ai_tick)

    def render_arena(self) -> None:
        if self.game_over:
            return
        p1_art = CHARACTERS[self.p1_name][self.p1_state]
        p2_art = CHARACTERS[self.p2_name][self.p2_state]

        term_width = 80
        p1_pos = int((self.p1_x / 100.0) * (term_width - 15))
        p2_pos = int((self.p2_x / 100.0) * (term_width - 15))
        if p1_pos >= p2_pos:
            p1_pos = max(0, p2_pos - 12)

        rows = []
        for r in range(5):
            line_buf = [" "] * term_width
            for idx, char in enumerate(p1_art[r]):
                pos = p1_pos + idx
                if 0 <= pos < term_width: line_buf[pos] = char
            for idx, char in enumerate(p2_art[r]):
                pos = p2_pos + idx
                if 0 <= pos < term_width: line_buf[pos] = char
            
            if r >= 3 and self.podium_hp > 0:
                line_buf[40] = "🏛️"
            
            rows.append("".join(line_buf))

        rows.append("=" * term_width)
        self.query_one("#arena_canvas", Static).update("\n".join(rows))

    def action_p1_left(self) -> None:
        if self.game_over: return
        self.p1_x = max(0, self.p1_x - 4)
        if self.p1_x >= self.p2_x - 8: self.p1_x = self.p2_x - 8
        self.render_arena()

    def action_p1_right(self) -> None:
        if self.game_over: return
        self.p1_x = min(100, self.p1_x + 4)
        if self.p1_x >= self.p2_x - 8: self.p1_x = self.p2_x - 8
        self.render_arena()

    def action_p2_left(self) -> None:
        if self.game_over or self.mode != "vs": return
        self.p2_x = max(0, self.p2_x - 4)
        if self.p2_x <= self.p1_x + 8: self.p2_x = self.p1_x + 8
        self.render_arena()

    def action_p2_right(self) -> None:
        if self.game_over or self.mode != "vs": return
        self.p2_x = min(100, self.p2_x + 4)
        if self.p2_x <= self.p1_x + 8: self.p2_x = self.p1_x + 8
        self.render_arena()

    def action_p1_punch(self) -> None:
        if self.game_over: return
        self.app.audio.play_sfx("punch")
        self.p1_state = "punching"
        self.session_hits += 1
        
        if abs(self.p2_x - self.p1_x) <= 15:
            self.p2_hp = max(0, self.p2_hp - 8)
            self.p1_shakti = min(100, self.p1_shakti + 10)
            self.p2_state = "damaged"
            self.query_one("#battle_log", Static).update(f"💥 {self.p1_name} connects a punch!")
        else:
            self.query_one("#battle_log", Static).update(f"{self.p1_name} punches thin air!")
        
        self.update_hud()
        self.render_arena()
        self.set_timer(0.2, self.reset_states)

    def action_p1_kick(self) -> None:
        if self.game_over: return
        self.app.audio.play_sfx("kick")
        self.p1_state = "kicking"
        self.session_hits += 1
        
        if abs(self.p2_x - self.p1_x) <= 15:
            self.p2_hp = max(0, self.p2_hp - 12)
            self.p1_shakti = min(100, self.p1_shakti + 15)
            self.p2_state = "damaged"
            self.query_one("#battle_log", Static).update(f"💥 {self.p1_name} lands a sweeping kick!")
        else:
            self.query_one("#battle_log", Static).update(f"{self.p1_name}'s kick misses!")
        
        self.update_hud()
        self.render_arena()
        self.set_timer(0.2, self.reset_states)

    def action_p1_special(self) -> None:
        if self.game_over: return
        self.app.audio.play_sfx("super")
        self.p1_state = "punching"
        special_name = CHARACTERS[self.p1_name]["special_name"]
        
        if abs(self.p2_x - self.p1_x) <= 25:
            self.p2_hp = max(0, self.p2_hp - 22)
            self.p1_shakti = min(100, self.p1_shakti + 25)
            self.p2_state = "damaged"
            self.query_one("#battle_log", Static).update(f"⚡ {self.p1_name} unleashes {special_name} for 22 DMG!")
        else:
            self.query_one("#battle_log", Static).update(f"{special_name} fired into open space!")
        
        if self.podium_hp > 0:
            self.podium_hp = max(0, self.podium_hp - 15)
            self.query_one("#stage_lbl", Label).update(f"🏟️ {self.stage_name}\nPodium HP: {self.podium_hp}")

        self.update_hud()
        self.render_arena()
        self.set_timer(0.3, self.reset_states)

    def action_p1_super(self) -> None:
        if self.game_over: return
        if self.p1_shakti >= 100:
            self.app.audio.play_sfx("super")
            self.p1_state = "punching"
            self.p2_hp = max(0, self.p2_hp - 45)
            self.p1_shakti = 0
            self.p2_state = "damaged"
            self.query_one("#battle_log", Static).update(f"🔥 MAX SHAKTI ULTIMATE STRIKE DEALS 45 DMG!")
            self.update_hud()
            self.render_arena()
            self.set_timer(0.3, self.reset_states)
            self.check_win_condition()
        else:
            self.query_one("#battle_log", Static).update("Shakti not full! Requires 100%.")

    def action_p2_punch(self) -> None:
        if self.game_over or self.mode != "vs": return
        self.app.audio.play_sfx("punch")
        self.p2_state = "punching"
        if abs(self.p1_x - self.p2_x) <= 15:
            self.p1_hp = max(0, self.p1_hp - 8)
            self.p2_shakti = min(100, self.p2_shakti + 10)
            self.p1_state = "damaged"
            self.query_one("#battle_log", Static).update(f"💥 {self.p2_name} (2P) punches 1P!")
        self.update_hud()
        self.render_arena()
        self.set_timer(0.2, self.reset_states)

    def action_p2_kick(self) -> None:
        if self.game_over or self.mode != "vs": return
        self.app.audio.play_sfx("kick")
        self.p2_state = "kicking"
        if abs(self.p1_x - self.p2_x) <= 15:
            self.p1_hp = max(0, self.p1_hp - 12)
            self.p2_shakti = min(100, self.p2_shakti + 15)
            self.p1_state = "damaged"
            self.query_one("#battle_log", Static).update(f"💥 {self.p2_name} (2P) kicks 1P!")
        self.update_hud()
        self.render_arena()
        self.set_timer(0.2, self.reset_states)

    def action_toggle_audio(self) -> None:
        muted = self.app.audio.toggle_mute()
        self.query_one("#battle_log", Static).update("Audio Muted." if muted else "Audio Resumed.")

    def update_hud(self) -> None:
        self.query_one("#p1_hp_bar", HealthBar).update_health(self.p1_hp)
        self.query_one("#p2_hp_bar", HealthBar).update_health(self.p2_hp)
        self.query_one("#p1_shakti_bar", ShaktiGauge).update_shakti(self.p1_shakti)
        self.query_one("#p2_shakti_bar", ShaktiGauge).update_shakti(self.p2_shakti)
        self.check_win_condition()

    def reset_states(self) -> None:
        self.p1_state = "idle"
        self.p2_state = "idle"
        self.render_arena()

    def cpu_ai_tick(self) -> None:
        if self.game_over or self.mode == "vs": return
        dist = abs(self.p2_x - self.p1_x)
        if dist > 12:
            self.p2_x = max(self.p1_x + 8, self.p2_x - 3)
            self.p2_state = "idle"
        elif dist < 6:
            self.p2_x = min(90, self.p2_x + 3)
            self.p2_state = "idle"
        else:
            choice = random.random()
            dmg = int(10 * self.cpu_boost)
            if choice < 0.6:
                self.p2_state = "punching"
                self.app.audio.play_sfx("punch")
                self.p1_hp = max(0, self.p1_hp - dmg)
                self.p1_state = "damaged"
                self.query_one("#battle_log", Static).update(f"⚠️ CPU {self.p2_name} strikes for {dmg} DMG!")
            elif choice < 0.9:
                self.p2_state = "kicking"
                self.app.audio.play_sfx("kick")
                self.p1_hp = max(0, self.p1_hp - int(dmg * 1.2))
                self.p1_state = "damaged"
                self.query_one("#battle_log", Static).update(f"⚠️ CPU {self.p2_name} lands heavy kick!")
            else:
                if self.p2_shakti >= 100:
                    self.p2_state = "punching"
                    self.app.audio.play_sfx("super")
                    self.p1_hp = max(0, self.p1_hp - 35)
                    self.p2_shakti = 0
                    self.query_one("#battle_log", Static).update("💥 CPU ULTIMATE SHAKTI STRIKE!")
            self.update_hud()
            self.set_timer(0.2, self.reset_states)
        self.render_arena()

    def check_win_condition(self) -> None:
        if self.p1_hp <= 0 and not self.game_over:
            self.game_over = True
            self.query_one("#battle_log", Static).update("💀 DEFEAT! You lost the parliamentary majority.")
            self.set_timer(2.0, lambda: self.app.push_screen(PostMatchScreen(won=False, level=self.level, mode=self.mode, hits=self.session_hits)))
        elif self.p2_hp <= 0 and not self.game_over:
            self.game_over = True
            jumla = random.choice([
                "Chai bhaiya demanded compensation for broken cups.",
                "A stray cow halted the match to eat a manifesto.",
                "Opposition walked out in protest after the knockout."
            ])
            self.query_one("#battle_log", Static).update(f"🏆 YOU WIN! {jumla}")
            self.set_timer(2.0, lambda: self.app.push_screen(PostMatchScreen(won=True, level=self.level, mode=self.mode, hits=self.session_hits)))


class PostMatchScreen(Screen):
    def __init__(self, won: bool, level: int, mode: str, hits: int) -> None:
        super().__init__()
        self.won = won
        self.level = level
        self.mode = mode
        self.hits = hits

    def compose(self) -> ComposeResult:
        title = "👑 STAGE CLEARED!" if self.won else "💀 PARLIAMENTARY DEFEAT!"
        subtext = f"Total Hits Landed: {self.hits} | Stage: {self.level}"
        options = "[1] Press 1: Next Stage / Rematch" if self.won else "[1] Press 1: Retry Level"
        
        yield Container(
            Label(title, id="splash_title"),
            Label(subtext, id="splash_subtitle"),
            Static(
                f"\n{options}\n"
                "[2] Press 2: Change Neta / Mode Menu\n"
                "[3] Press 3: Quit Game\n",
                id="splash_text"
            ),
            classes="center_box"
        )

    def on_key(self, event) -> None:
        if event.key == "1":
            next_lvl = self.level + 1 if self.won and self.mode == "campaign" else self.level
            self.app.push_screen(RosterMenuScreen(mode=self.mode, level=next_lvl))
        elif event.key == "2":
            self.app.push_screen(SplashDisclaimerScreen())
        elif event.key == "3":
            self.app.exit()


class SansadApp(App):
    CSS = """
    Screen { background: #090912; color: #f0f0f5; }
    .center_box { align: center middle; padding: 2 4; border: solid #ffaa00; background: #121222; width: 80%; height: 85%; }
    #splash_title { text-style: bold; color: #ffcc00; content-align: center middle; margin-bottom: 1; }
    #splash_subtitle { color: #55ff55; text-style: bold; content-align: center middle; margin-top: 1; }
    #splash_text { text-style: bold; color: #00ffff; content-align: center middle; height: 12; padding-top: 1; }
    #roster_container { align: center middle; width: 100%; height: 100%; padding: 2; }
    #roster_header { text-style: bold; color: #ffaa00; content-align: center middle; margin-bottom: 2; }
    #roster_flex { layout: horizontal; align: center middle; height: 18; }
    #char_preview_box { width: 35; height: 15; border-top: solid #00ffff; background: #0d0d1a; padding: 1 4; }
    .roster_info { width: 40; padding: 2; }
    #char_name_label { text-style: bold; content-align: center middle; margin-bottom: 1; }
    #char_title_label { color: #aaaaaa; content-align: center middle; }
    #char_special_label { color: #55ff55; content-align: center middle; margin-top: 1; }
    #roster_footer { color: #8888aa; content-align: center middle; margin-top: 2; }
    #arena_main { padding: 1 2; }
    #hud_container { height: 6; background: #111122; border: solid #444466; margin-bottom: 1; }
    .hud_panel { width: 38%; padding: 0 1; }
    .hud_center { width: 24%; content-align: center middle; }
    #stage_lbl { text-style: bold; color: #ffaa00; content-align: center middle; }
    #arena_canvas { height: 12; background: #050510; border: double #ff5555; content-align: center middle; color: #00ffcc; margin-bottom: 1; }
    #battle_log { height: 3; background: #161628; border: solid #00aaaa; content-align: center middle; color: #ffff55; margin-bottom: 1; }
    #control_instructions { height: 3; background: #1a1a2e; border: solid #8888aa; content-align: center middle; color: #00ffcc; text-style: bold; }
    """

    def on_mount(self) -> None:
        self.audio = AudioEngine()
        self.push_screen(SplashDisclaimerScreen())


if __name__ == "__main__":
    print_terminal_startup_banner()
    app = SansadApp()
    app.run()