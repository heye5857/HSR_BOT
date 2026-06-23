import cv2
import numpy as np
import mss
import re
import pyautogui
import pytesseract
from pytesseract import Output
from difflib import get_close_matches, SequenceMatcher

import config as cfg

pytesseract.pytesseract.tesseract_cmd = str(cfg.TESSERACT_CMD)

def normalize_stat(text):
    text = text.strip()
    for wrong, correct in cfg.OCR_FIX.items():
        text = text.replace(wrong, correct)

    # 進一步清洗：去除數字、百分比符號及其他非中英文字符，只保留屬性名稱
    text = re.sub(r"[-+]?\d*\.?\d+", "", text) # 移除數值
    text = text.replace("%", "") # 移除百分號
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z]+", "", text) # 只保留中英文字符
    text = text.strip() # 再次去除可能產生的多餘空白

    match = get_close_matches(
        text,
        cfg.VALID_STATS,
        n=1,
        cutoff=0.5
    )

    if match:
        return match[0]

    return text

def fuzzy_match_relic_name(text):
    cleaned = re.sub(r"[^\u4e00-\u9fff]", "", text or "")
    if not cleaned:
        return None

    for name in cfg.RELIC_RULES.keys():
        if name in cleaned:
            return name

    best_name = None
    best_ratio = 0.0
    for name in cfg.RELIC_RULES.keys():
        ratio = SequenceMatcher(None, cleaned, name).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_name = name

    if best_ratio >= 0.55:
        return best_name
    return None


def extract_relic_name_from_text(text):
    text = text.strip()
    for wrong, correct in cfg.RELIC_OCR_FIX.items():
        text = text.replace(wrong, correct)

    best = None
    for line in text.splitlines():
        line_clean = re.sub(r"[-+]?\d*\.?\d+%?", "", line)
        result = fuzzy_match_relic_name(line_clean)
        if result:
            return result
        if not best:
            best = result

    if best:
        return best

    cleaned = re.sub(r"[-+]?\d*\.?\d+%?", "", text)
    return fuzzy_match_relic_name(cleaned)


def normalize_relic_name(text):
    if not text:
        return text

    text = text.strip()
    for wrong, correct in cfg.RELIC_OCR_FIX.items():
        text = text.replace(wrong, correct)

    text = re.sub(r"[^\u4e00-\u9fff]", "", text)
    for name in cfg.RELIC_RULES.keys():
        if name in text:
            return name

    result = fuzzy_match_relic_name(text)
    if result:
        return result

    return text


def parse_relic_from_full_text(full_text):
    """高效率地從完整 OCR 文本中提取遺器信息。"""
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    name = None
    part = ""
    main_stat = ""
    sub_lines = []
    found_main = False

    for line in lines:
        # 優先找遺器名稱
        if not name:
            name_candidate = extract_relic_name_from_text(line)
            if name_candidate and name_candidate in cfg.RELIC_RULES:
                name = name_candidate
                continue

        # 尋找部位
        if not part:
            normalized_part = normalize_part(line)
            if normalized_part:
                part = normalized_part
                continue

        # 尋找主詞條（含有屬性名稱）
        if not found_main:
            stat_candidate = normalize_stat(line)
            if stat_candidate in cfg.VALID_STATS:
                main_stat = stat_candidate
                found_main = True
                continue

        # 其餘為副詞條
        if re.search(r"[-+]?\d*\.?\d+", line):
            sub_lines.append(line)

    return name, main_stat, part, sub_lines

# ===== 範本讀取 =====
TEMPLATES = {}
for name, template_path in cfg.PATH.items():
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"⚠ 無法讀取範本: {template_path}")
    TEMPLATES[name] = template

def capture_screen():
    """截取整個螢幕並回傳灰階影像。"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        # 確保輸出為 uint8 格式
        if gray.dtype != np.uint8:
            gray = gray.astype(np.uint8)
        return gray

def find_center(template_name, *, screen: np.ndarray = None, threshold: float = cfg.MATCH_THRESHOLD):
    """在螢幕上尋找圖片範本中心座標，優先取最靠近左上角的位置。"""
    if screen is None:
        screen = capture_screen()
    template = TEMPLATES.get(template_name)

    if template is None:
        print("⚠ 模板讀取失敗:", template_name)
        return None

    # 確保影像格式一致
    if screen.dtype != np.uint8:
        screen = screen.astype(np.uint8)
    if template.dtype != np.uint8:
        template = template.astype(np.uint8)

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
    
    h, w = template.shape
    return (nearest[0] + w // 2, nearest[1] + h // 2)

def click_image(template_name, *, screen: np.ndarray = None, threshold: float = cfg.MATCH_THRESHOLD):
    """點擊範本所在位置，找不到回傳 False。"""
    if screen is None:
        pos = find_center(template_name, threshold=threshold)  
    else:
        pos = find_center(template_name, screen=screen, threshold=threshold)
    
    if pos:
        pyautogui.click(pos[0], pos[1])
        return True

    print("⚠ 找不到圖片:", template_name)
    return False

def match(screen, template, threshold=cfg.MATCH_THRESHOLD):
    if template is None:
        return False

    # 確保影像格式一致
    if screen.dtype != np.uint8:
        screen = screen.astype(np.uint8)
    if template.dtype != np.uint8:
        template = template.astype(np.uint8)

    # 檢查模板尺寸是否超過螢幕尺寸，防止 OpenCV 報錯
    h_s, w_s = screen.shape[:2]
    h_t, w_t = template.shape[:2]
    if h_t > h_s or w_t > w_s:
        # print(f"⚠ 警告: 模板尺寸 ({w_t}x{h_t}) 超過螢幕尺寸 ({w_s}x{h_s})，請檢查 DPI 縮放設定")
        return False

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    return np.max(res) >= threshold

def detect_state(screen):
    for name, template in TEMPLATES.items():
        if template is None:
            continue
        if match(screen, template):
            return name.upper().replace(" ", "_")
    return cfg.UNKNOWN

def preprocess(roi):
    """高速版會像進行二值化。"""
    # 重新設定大小時使用更快的插值方法
    roi = cv2.resize(roi, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    _, roi = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY)
    return roi

def read_text_filtered(roi, char_whitelist, language="chi_tra"):
    """讀取文字並只保留白名單中的字符。"""
    roi = preprocess(roi)
    text = pytesseract.image_to_string(
        roi,
        lang=language,
        config=cfg.OCR_CONFIG,
    )
    text = text.strip()
    filtered = "".join(c for c in text if c in char_whitelist or c.isspace())
    return filtered.strip()


def read_text_for_relic_name(roi):
    """專用於遺器名稱辨識，限制字符到已知遺器名稱範圍。"""
    text = read_text_filtered(roi, cfg.RELIC_NAME_CHARS)
    for wrong, correct in cfg.RELIC_OCR_FIX.items():
        text = text.replace(wrong, correct)
    return text


def read_text_for_stat(roi):
    """專用於屬性名稱辨識，限制字符到已知屬性。"""
    text = read_text_filtered(roi, cfg.STAT_NAME_CHARS)
    for wrong, correct in cfg.OCR_FIX.items():
        text = text.replace(wrong, correct)
    return text


def read_text_for_part(roi):
    """專用於部位名稱辨識，限制字符到已知部位。"""
    text = read_text_filtered(roi, cfg.PART_NAME_CHARS)
    return text


def read_text_for_number(roi):
    """專用於數值辨識，限制字符到數字、小數點和百分號。"""
    text = read_text_filtered(roi, cfg.NUMBER_CHARS)
    return text


def read_text(roi):
    roi = preprocess(roi)
    text = pytesseract.image_to_string(
        roi,
        lang=cfg.OCR_LANG,
        config=cfg.OCR_CONFIG,
    )
    return text.strip()

def get_stamina():
    roi = capture_screen()[50:80, 1470:1575]
    text = read_text(roi)
    text = text.replace("O", "0").replace("o", "0")
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

def normalize_part(text):
    text = text.strip()
    for part_name in ["頭部", "手部", "軀幹", "腳部"]:
        if part_name in text:
            return part_name
    text = re.sub(r"[^\u4e00-\u9fff]", "", text)
    if text in {"頭部", "手部", "軀幹", "腳部"}:
        return text
    return ""


def parse_relic(screen):
    """核心断單一次 OCR 並分解綐果。"""
    # 先取得完整遺器區域
    relic_roi = screen[405:630, 550:1480]  # 包含名稱、主詞條、副詞條、部位
    
    result = {
        "name": "",
        "main_stat": "",
        "sub_stats": [],
        "part": "",
    }
    
    # 從預處理後的 ROI 一次成控 OCR
    relic_roi_processed = preprocess(relic_roi)
    full_text = pytesseract.image_to_string(
        relic_roi_processed,
        lang=cfg.OCR_LANG,
        config=cfg.OCR_CONFIG,
    ).strip()
    print(f"遺器完整文字: {full_text}")
    
    fallback_name, fallback_main, fallback_part, fallback_sub_lines = parse_relic_from_full_text(full_text)

    # 断定遺器名稱，准確度高的情況下東报程
    name_candidate = fallback_name or ""
    if name_candidate in cfg.RELIC_RULES:
        result["name"] = name_candidate
    else:
        result["name"] = name_candidate

    result["main_stat"] = fallback_main or ""
    result["part"] = fallback_part or ""
    
    # 解析副詞條
    for line in fallback_sub_lines:
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