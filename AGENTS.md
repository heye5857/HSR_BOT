# HSR_BOT — Agent Guide

Windows-only Honkai: Star Rail automation bot. Uses screen capture + OpenCV template matching + Tesseract OCR.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Install Tesseract-OCR separately; set `TESSERACT_CMD` in `config.py:8`
- Set `GAME_PATH` in `config.py:5` to `StarRail.exe`
- All user parameters in `config.py` — click coordinates, OCR settings, ROIs, thresholds
- OCR language: `chi_tra` (Traditional Chinese), configurable at `config.py:9`
- Expected game resolution: **1920×1080**
- Admin privileges recommended (F8 key detection, window operations)

## Run

```powershell
python main.py
```

**F8** to stop, **F9** to pause (releases Alt), **F10** to resume. Bot detects stuck state after 60s (`STUCK_TIME` in `config.py:19`), warns once, then stops.

## Build executable

```powershell
python -m pip install pyinstaller
python build_exe.py
```

Output: `dist\HSR_BOT\HSR_BOT.exe` (requires admin, bundles `images/`, copies `config.py` alongside .exe for editing)

## Architecture

| File | Role |
|---|---|
| `main.py` | Entrypoint — `Bot` class state machine, F8 keyboard listener thread, main loop |
| `config.py` | Game path, OCR config, image template paths, state string constants, relic scoring rules |
| `vision.py` | `capture_screen()` (mss), `match()` / `find_center()` (OpenCV template match), `read_text()` / `get_stamina()` (pytesseract OCR), `parse_relic()` / `score_relic()` |
| `actions.py` | `pyautogui.click()` wrappers, hotkeys (Esc, Alt+F4), `press_alt()` / `release_alt()` |
| `images/` | PNG templates matched by filename key in `config.PATH` |

State machine flow: `capture screen → detect_state() → handler(state, screen)`. States defined as string constants in `config.py:21-49`.

Alt key is held during `action_action()` — see `press_alt()` / `release_alt()` in `actions.py:19-24`. The `leave_action()` releases alt, presses Esc, then re-holds alt.

Relic scoring rules live in `config.py:143-176` per relic set name, with `OCR_FIX` and `RELIC_OCR_FIX` lookup maps (`config.py:60-68`) for common OCR misreads.

## Logging

- `bot.log` in project root (rotating, 10MB, 5 backups) + `logs/` subdir
- Console output duplicates file log at INFO level
- Logger name `HSR_BOT`

## Dependencies

opencv-python, numpy, psutil, pyautogui, pytesseract, mss
