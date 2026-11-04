# 🏛️ Sansad Showdown
### *The Political Arcade Fighter (Terminal Edition)*

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Textual%20TUI-purple.svg)](https://textual.textualize.io/)
[![License: Satire](https://img.shields.io/badge/license-Satire%20%2F%20Parody-orange.svg)](https://fightkaro.com)
[![Status](https://img.shields.io/badge/status-Production%20Ready-success.svg)](https://fightkaro.com/sansad-showdown)

---

> **Sansad Showdown** is a high-octane political arcade fighting game brought directly to your command line. Built using Python, **Textual**, and **Pygame**, this terminal user interface (TUI) edition delivers ASCII character animations, distinct special abilities, destructible stage hazards, a 6-stage progressive campaign, and local 2-player support.

---

## ⚖️ Official Satire & Terms Disclaimer

> **⚠️ NOTICE:** All characters, names, titles, and events depicted in this software are entirely fictitious parodies created exclusively for entertainment and satirical purposes. This project is the terminal adaptation of the original concept by **[FightKaro.com](https://fightkaro.com)**. Any resemblance or similarity to real-world persons, living or deceased, is strictly coincidental.

---

## 🎮 Game Modes

* **1. Arcade Campaign Mode:** Battle your way through 6 progressive stages—scaling from the *Lok Sabha Floor* to the *Secret Parliamentary Bunker (BOSS)* with escalating AI difficulty.
* **2. Local 2-Player Versus Mode:** Challenge a friend head-to-head on the same keyboard in real-time.
* **3. Endless Survival Wave Mode:** Test your mechanical precision against continuous waves of opponents.

---

## 🕹️ Control Reference

### Player 1 (1P)
| Action | Keybinding |
| :--- | :--- |
| **Move Left / Right** | `A` / `D` |
| **Punch** | `J` |
| **Kick** | `K` |
| **Special Ability** | `I` |
| **Max Shakti Ultimate** | `L` *(Unlocks at 100% Shakti Gauge)* |

### Player 2 (2P - Versus Mode)
| Action | Keybinding |
| :--- | :--- |
| **Move Left / Right** | `Left Arrow` / `Right Arrow` |
| **Punch** | `N` |
| **Kick** | `M` |

### System Commands
* **Toggle Audio Mute:** `T`

---

## ⚙️ Installation & Quickstart

### Prerequisites
Ensure you have Python 3.8 or higher installed on your local machine.

### 1.Clone the repository 
```
git clone https://github.com/immortall-web/sansad-showdown
```
### 2. Install Dependencies
```bash
pip install textual pygame
```
### 3. Go to Directory
```bash
 cd sansad-showdown
```
### 4. Run the Game
```bash
python3 Sansad.py
```
###  Project Architecture 

TUI Framework: Textual (Async event-driven terminal user interface and reactive CSS layout engine).

Audio Layer: Pygame Mixer (Thread-safe procedural sound effect synthesizer).

Architecture: Component-driven screen management, finite state machine (FSM) AI for CPU opponents, and real-time ANSI canvas rendering.

### 📜 Credits & Acknowledgments

Original Concept & Universe: Inspired by and adapted from the satirical political fighter universe created by FightKaro.com.

Terminal Engineering & Implementation: Developed as the official terminal-based TUI port utilizing modern asynchronous Python patterns, with architectural collaboration and code refinement by Gemini.
