# Developer Agent Guide: HSR_BOT

A lightweight automated bot for *Honkai: Star Rail* using image template-matching and OCR screen automation on Windows.

---

## ⚠️ Critical Environment Gotchas (Agents Will Fail Without These)

1. **Missing Dependencies in `requirements.txt`**:
   * `requirements.txt` only lists `opencv-python` and `numpy`.
   * **Crucial:** You must also install the actual imported dependencies:
     ```powershell
     pip install psutil pyautogui pytesseract mss
     ```
2. **Administrator Privileges Required**:
   * The terminal/process running `main.py` **must run as Administrator**. Otherwise, `pyautogui` keyboard/mouse events cannot inject actions into the elevated game window, and global `F8` keyboard monitoring via `GetAsyncKeyState` will fail.
3. **Screen Resolution & DPI Constraint**:
   * Game/desktop resolution **must be exactly 1920x1080**.
   * Hardcoded regions (ROIs) for OCR matching in `vision.py` (stamina, relics) and pixel-based templates in `images/` will fail if DPI scaling is not 100% or resolution differs.
4. **Tesseract-OCR Location**:
   * `TESSERACT_CMD` path is hardcoded in `config.py` as `C:\Program Files\Tesseract-OCR\tesseract.exe`. Ensure Tesseract is installed at this location on the host machine.
5. **Game Path Configuration**:
   * `GAME_PATH` in `config.py` defaults to `E:\Epic Games\HonkaiStarRail\games\Star Rail Games\StarRail.exe`. You must update this path to launch the game correctly on other machines.

---

## 🛠️ Developer Commands

* **Run Bot**:
  ```powershell
  python main.py
  ```
* **Stop Bot**: Press `F8` on the keyboard (monitored globally via a dedicated thread using `user32.GetAsyncKeyState`).
* **Build Executable (PyInstaller)**:
  ```powershell
  python build_exe.py
  ```
  *(Generates standalone package in `dist\HSR_BOT\HSR_BOT.exe` requiring elevated Administrator privileges automatically via UAC).*

---

## 🧩 Key Architecture & State Mapping Conventions

### State Engine Lifecycle
`main.py` continuously takes screenshots via `mss` -> uses `vision.detect_state()` to match against template keys in `config.py:PATH` -> executes matching callback handler in `Bot().handlers`.

### Convention for Adding a New State
If adding a new screen/state to the bot, you **must** strictly follow this exact naming conversion to avoid breaking the automated state router:
1. Save your template image to `images/my_new_state.png`.
2. Add the path to `config.py:PATH` with a **lowercase key containing spaces**:
   ```python
   "my new state": str(IMAGE_DIR / "my_new_state.png"),
   ```
3. Define the uppercase state constant in `config.py`:
   ```python
   MY_NEW_STATE = "MY_NEW_STATE"
   ```
4. Map the state to its handler inside `main.py:Bot().__init__()`:
   ```python
   cfg.MY_NEW_STATE: self.handle_my_new_state,
   ```
*(This is required because `vision.detect_state()` maps template keys using `.upper().replace(" ", "_")` to lookup handlers).*

---

## 🛡️ Recovery & Safety Controls

* **Stuck Detection**: If a state remains unchanged for `STUCK_TIME` (60 seconds) in `main.py:check_stuck()`, the bot is considered stuck and will immediately stop execution.
* **Battle State Immunity**: The stuck timer is bypassed during the `BATTLE` state to prevent timeouts during long fights.

---

## 🔍 Relic Scoring Nuances

* OCR parser looks for relic stats in specific screen ROIs (`vision.py:parse_relic`).
* Relic names and stats are matched using `difflib.get_close_matches` against predefined rules in `config.py:RELIC_RULES`.
* **Important**: Typo corrections or new relic additions must update both the rules dictionary and the OCR lookup fix configurations in `config.py:RELIC_OCR_FIX` (e.g., `"功動閃耀的魔法少女"`).
