import atexit
import os
import tempfile
import cv2
import numpy as np
import mss
import re
import pyautogui
import pytesseract
from pytesseract import Output
from difflib import get_close_matches

import config as cfg

pytesseract.pytesseract.tesseract_cmd = str(cfg.TESSERACT_CMD)

_sct = mss.mss()

# Write whitelist to a temp config file to avoid Windows cmdline encoding issues
_chars_config = None
if cfg.OCR_CHARS:
    _chars_config = tempfile.NamedTemporaryFile(
        mode='w', suffix='.config', delete=False, encoding='utf-8'
    )
    _chars_config.write(f"tessedit_char_whitelist {cfg.OCR_CHARS}\n")
    _chars_config.close()
    atexit.register(lambda p=os.path.abspath(_chars_config.name): os.unlink(p))

def normalize_stat(text):
    text = text.strip()
    for wrong, correct in cfg.OCR_FIX.items():
        text = text.replace(wrong, correct)

    text = re.sub(r"\s+", "", text)

    match = get_close_matches(
        text,
        cfg.VALID_STATS,
        n=1,
        cutoff=0.5
    )

    if match:
        return match[0]

    return text


def normalize_relic_name(text):
    text = text.strip()
    for wrong, correct in cfg.RELIC_OCR_FIX.items():
        text = text.replace(wrong, correct)

    text = re.sub(r"\s+", "", text)

    relic_names = list(cfg.RELIC_RULES.keys())
    match = get_close_matches(
        text,
        relic_names,
        n=1,
        cutoff=0.5
    )

    if match:
        return match[0]

    return text

# ===== 範本讀取 =====
TEMPLATES = {}
for name, template_path in cfg.PATH.items():
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"⚠ 無法讀取範本: {template_path}")
    TEMPLATES[name] = template


def capture_screen():
    """截取整個螢幕並回傳灰階影像。"""
    monitor = _sct.monitors[1]
    img = np.array(_sct.grab(monitor))
    return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)


_PATH_TO_NAME = {v: k for k, v in cfg.PATH.items()}

def _load_template(template_path):
    template_name = _PATH_TO_NAME.get(template_path)
    if template_name and template_name in TEMPLATES:
        return TEMPLATES[template_name]
    return cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)


def find_center(template_path, threshold=cfg.MATCH_THRESHOLD, screen=None):
    """在螢幕上尋找圖片範本中心座標，優先取最靠近左上角的位置。"""
    if screen is None:
        screen = capture_screen()
    template = _load_template(template_path)

    if template is None:
        print("⚠ 模板讀取失敗:", template_path)
        return None

    h_t, w_t = template.shape
    h_s, w_s = screen.shape[:2]
    if h_t > h_s or w_t > w_s:
        return None

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) == 0:
        return None

    # 找最靠近左上角的位置
    points = list(zip(*loc[::-1]))
    min_y = min(pt[1] for pt in points)
    nearby_y_threshold = 10  # y 差異在 10 pixels 內視為同行
    
    # 從 y 座標在容差範圍內的點中，選最左邊的 (x 最小)
    nearest = min((pt for pt in points if pt[1] <= min_y + nearby_y_threshold), 
                  key=lambda p: p[0])
    
    return (nearest[0] + w_t // 2, nearest[1] + h_t // 2)


def click_image(template_path, threshold=cfg.MATCH_THRESHOLD, screen=None):
    """點擊範本所在位置，找不到回傳 False。"""
    pos = find_center(template_path, threshold, screen)
    if pos:
        pyautogui.click(pos[0], pos[1])
        return True

    print("⚠ 找不到圖片:", template_path)
    return False


def match(screen, template, threshold=cfg.MATCH_THRESHOLD):
    if template is None:
        return False

    # 檢查模板尺寸是否超過螢幕尺寸，防止 OpenCV 報錯
    h_s, w_s = screen.shape[:2]
    h_t, w_t = template.shape[:2]
    if h_t > h_s or w_t > w_s:
        print(f"⚠ 警告: 模板尺寸 ({w_t}x{h_t}) 超過螢幕尺寸 ({w_s}x{h_s})，請檢查 DPI 縮放設定")
        return False

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    return np.max(res) >= threshold


def detect_state(screen, hint=None):
    if hint:
        hint_key = hint.lower().replace("_", " ")
        if hint_key in TEMPLATES and match(screen, TEMPLATES[hint_key]):
            return hint
    for name, template in TEMPLATES.items():
        if template is None:
            continue
        if match(screen, template):
            return name.upper().replace(" ", "_")
    return cfg.UNKNOWN


def preprocess(roi):
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    _, roi = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY)
    return roi


def read_text(roi, chars=False):
    roi = preprocess(roi)
    config = cfg.OCR_CONFIG
    if chars and _chars_config:
        config = f"{config} {_chars_config.name}"
    text = pytesseract.image_to_string(
        roi,
        lang=cfg.OCR_LANG,
        config=config,
    )
    return text.strip()


def get_stamina(screen=None):
    if screen is None:
        screen = capture_screen()
    roi = screen[50:80, 1470:1575]
    text = pytesseract.image_to_string(
        preprocess(roi),
        lang=cfg.OCR_LANG,
        config=cfg.OCR_CHARS_DIGITS,
    )
    print("OCR文字:", text)

    digits = re.findall(r"\d+", text)
    if not digits:
        print("⚠ 體力辨識失敗")
        return None

    stamina = int(digits[0])
    print("剩餘體力:", stamina)
    return stamina


def click_task_button(keyword):

    screen = capture_screen()

    data = pytesseract.image_to_data(
        screen,
        lang="chi_tra",
        output_type=Output.DICT
    )

    for i in range(len(data["text"])):

        text = data["text"][i]

        if keyword in text:

            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]

            print("找到任務:", text)

            # =========================
            # 計算按鈕位置
            # =========================

            button_x = x + w // 2

            button_y = y + 335

            pyautogui.click(button_x, button_y)

            return True
        
    print("⚠ 找不到任務:", keyword)    

    return False


def parse_sub_stat(line):
    line = line.strip()
    if not line:
        return None

    line = line.replace("O", "0").replace("o", "0")
    number_matches = re.findall(r"[-+]?\d*\.?\d+", line)
    if not number_matches:
        return None

    value_text = number_matches[-1]
    is_percent = "%" in line
    try:
        value = float(value_text)
    except ValueError:
        return None

    name = line
    name = re.sub(re.escape(value_text) + r"$", "", name)
    name = name.replace("%", "").replace("+", "")
    name = re.sub(r"\(.*?\)", "", name).strip()
    name = re.sub(r"[^\u4e00-\u9fffA-Za-z]+", "", name)
    name = normalize_stat(name)

    return {
        "name": name,
        "value": value,
        "is_percent": is_percent,
    }


def parse_relic(screen):
    result = {
        "name": read_text(screen[600:630, 790:1020], chars=True),
        "main_stat": normalize_stat(read_text(screen[405:440, 830:980], chars=True).strip()),
        "sub_stats": [],
        "part": read_text(screen[720:750, 550:600], chars=True),
    }

    sub_text = read_text(screen[450:590, 835:1480], chars=True)
    for line in sub_text.splitlines():
        parsed = parse_sub_stat(line)
        if parsed:
            result["sub_stats"].append(parsed)

    return result


def score_relic(data):
    relic_name = normalize_relic_name(data.get("name", "").strip())
    part = data.get("part", "").strip()
    main = data.get("main_stat", "")
    subs = data.get("sub_stats", [])

    rule = cfg.RELIC_RULES.get(relic_name)
    if rule is None:
        print("⚠ 未知遺器:", relic_name)
        return "未知遺器"

    main = normalize_stat(main.strip())
    score = 0
    if part in {"頭部", "手部"}:
        score += 40
    elif part == "軀幹":
        for stat_name, stat_score in rule.get("body_main_scores", {}).items():
            if stat_name in main:
                score += stat_score
                print("✔ 軀幹主詞條:", stat_name, "+", stat_score)
    elif part == "腳部":
        for stat_name, stat_score in rule.get("feet_main_scores", {}).items():
            if stat_name in main:
                score += stat_score
                print("✔ 腳部主詞條:", stat_name, "+", stat_score)

    good_sub = rule.get("good_sub_scores", {})
    for stat in subs:
        stat_name = stat["name"]
        if stat_name not in good_sub:
            continue
        if stat_name == "攻擊力" and not stat["is_percent"]:
            score += good_sub[stat_name]
        elif stat_name != "攻擊力":
            score += good_sub[stat_name]

    return score


def show_roi(screen):
    debug = cv2.cvtColor(screen, cv2.COLOR_GRAY2BGR)
    regions = [
        (790, 600, 1020, 630),
        (830, 405, 980, 440),
        (835, 450, 1480, 590),
        (550, 720, 600, 750),
    ]
    for x1, y1, x2, y2 in regions:
        cv2.rectangle(debug, (x1, y1), (x2, y2), (255, 255, 255), 2)

    cv2.imshow("ROI", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
