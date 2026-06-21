import sys
from pathlib import Path

# 遊戲啟動設定
GAME_PATH = Path(r"E:\Epic Games\HonkaiStarRail\games\Star Rail Games\StarRail.exe")

# OCR 設定
TESSERACT_CMD = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
OCR_LANG = "chi_tra"
OCR_CONFIG = "--psm 6"

# 點擊座標
CLICK_CENTER = (960, 540)
CLICK_CONFIRM = (960, 700)

# 偵測與比對設定
MATCH_THRESHOLD = 0.85
STUCK_TIME = 60

# 狀態定義
LOGIN_1 = "LOGIN_1"
LOGIN_2 = "LOGIN_2"
HOME = "HOME"
MAIN_MENU = "MAIN_MENU"
CLAIM_ENTRUST = "CLAIM_ENTRUST"
SUCCESSFULLY_CLAIM = "SUCCESSFULLY_CLAIM"
ENTRUSTED = "ENTRUSTED"
CLAIM_MAIL = "CLAIM_MAIL"
DELETE = "DELETE"
REWARD_PAGE = "REWARD_PAGE"
TASK_PAGE = "TASK_PAGE"
PREPARE = "PREPARE"
PREPARED = "PREPARED"
INSUFFICIENT_PHYSICAL_STRENGTH = "INSUFFICIENT_PHYSICAL_STRENGTH"
CONFIRM = "CONFIRM"
CHALLENGE_SUCCESSFUL = "CHALLENGE_SUCCESSFUL"
BATTLE = "BATTLE"
STATE = "STATE"
START_CHALLENGE_1 = "START_CHALLENGE_1"
START_CHALLENGE_2 = "START_CHALLENGE_2"
SELECTED_1 = "SELECTED_1"
SELECTED_2 = "SELECTED_2"
SELECT_END = "SELECT_END"
PASS_PAGE = "PASS_PAGE"
PASS_MISSION_PAGE = "PASS_MISSION_PAGE"
QUICK_COLLECTION = "QUICK_COLLECTION"
CRAFTING_PAGE = "CRAFTING_PAGE"
CONFIRM_CRAFT = "CONFIRM_CRAFT"
UNKNOWN = "UNKNOWN"

VALID_STATS = [
    "暴擊率",
    "暴擊傷害",
    "攻擊力",
    "速度",
    "生命值",
    "防禦力",
]

OCR_FIX = {
    "暴荐率": "暴擊率",
    "暴聞傷害": "暴擊傷害",
}

RELIC_OCR_FIX = {
    "功動閃耀的魔法少女": "功動閃耀的魔法少女",
    "應天水這的卜者": "應天涉遠的卜者",
}

# 圖片資源路徑
if getattr(sys, 'frozen', False):
    # PyInstaller 打包後的路徑
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

IMAGE_DIR = BASE_DIR / "images"

PATH = {
    "login_1": str(IMAGE_DIR / "login_1.png"),
    "login_2": str(IMAGE_DIR / "login_2.png"),
    "home": str(IMAGE_DIR / "home.png"),
    "main menu": str(IMAGE_DIR / "main menu.png"),
    "entrust": str(IMAGE_DIR / "entrust.png"),
    "claim entrust": str(IMAGE_DIR / "claim entrust.png"),
    "entrusted": str(IMAGE_DIR / "entrusted.png"),
    "has mail": str(IMAGE_DIR / "has mail.png"),
    "mail": str(IMAGE_DIR / "mail.png"),
    "claim mail": str(IMAGE_DIR / "claim mail.png"),
    "delete": str(IMAGE_DIR / "delete.png"),
    "successfully claim": str(IMAGE_DIR / "successfully claim.png"),
    "action": str(IMAGE_DIR / "action.png"),
    "task page": str(IMAGE_DIR / "task page.png"),
    "reward page": str(IMAGE_DIR / "reward page.png"),
    "crafting page": str(IMAGE_DIR / "crafting page.png"),
    "task": str(IMAGE_DIR / "task.png"),
    "solve task": str(IMAGE_DIR / "solve task.png"),
    "reward": str(IMAGE_DIR / "reward.png"),
    "crafting": str(IMAGE_DIR / "crafting.png"),
    "cookie": str(IMAGE_DIR / "cookie.png"),
    "confirm craft": str(IMAGE_DIR / "confirm craft.png"),
    "schedule": str(IMAGE_DIR / "schedule.png"),
    "claim reward_1": str(IMAGE_DIR / "claim reward_1.png"),
    "claim reward_2": str(IMAGE_DIR / "claim reward_2.png"),
    "claim schedule": str(IMAGE_DIR / "claim schedule.png"),
    "enter": str(IMAGE_DIR / "enter.png"),
    "prepare": str(IMAGE_DIR / "prepare.png"),
    "Insufficient physical strength": str(IMAGE_DIR / "Insufficient physical strength.png"),
    "quick collection": str(IMAGE_DIR / "quick collection.png"),
    "cancel": str(IMAGE_DIR / "cancel.png"),
    "prepared": str(IMAGE_DIR / "prepared.png"),
    "challenge": str(IMAGE_DIR / "challenge.png"),
    "start_challenge_1": str(IMAGE_DIR / "start_challenge_1.png"),
    "start_challenge_2": str(IMAGE_DIR / "start_challenge_2.png"),
    "maximum": str(IMAGE_DIR / "maximum.png"),
    "confirm": str(IMAGE_DIR / "confirm.png"),
    "reduce": str(IMAGE_DIR / "reduce.png"),
    "battle": str(IMAGE_DIR / "battle.png"),
    "challenge successful": str(IMAGE_DIR / "challenge successful.png"),
    "state": str(IMAGE_DIR / "state.png"),
    "locking": str(IMAGE_DIR / "locking.png"),
    "discard": str(IMAGE_DIR / "discard.png"),
    "selected_1": str(IMAGE_DIR / "selected_1.png"),
    "selected_2": str(IMAGE_DIR / "selected_2.png"),
    "select end": str(IMAGE_DIR / "select end.png"),
    "suitable": str(IMAGE_DIR / "suitable.png"),
    "next_1": str(IMAGE_DIR / "next_1.png"),
    "next_2": str(IMAGE_DIR / "next_2.png"),
    "exit stage": str(IMAGE_DIR / "exit stage.png"),
    "finish": str(IMAGE_DIR / "finish.png"),
    "pass": str(IMAGE_DIR / "pass.png"),
    "pass page": str(IMAGE_DIR / "pass page.png"),
    "hasPassMissionReward": str(IMAGE_DIR / "hasPassMissionReward.png"),
    "pass mission page": str(IMAGE_DIR / "PassMissionPage.png"),
    "quick farm": str(IMAGE_DIR / "quick farm.png"),
    "quick claim": str(IMAGE_DIR / "quick claim.png"),
    "hasPassReward": str(IMAGE_DIR / "hasPassReward.png"),
    "device": str(IMAGE_DIR / "device.png"),
    "closure": str(IMAGE_DIR / "closure.png"),
}

# 遺器評分規則
RELIC_RULES = {
    "功動閃耀的魔法少女": {
        "body_main_scores": {
            "暴擊率": 40,
            "暴擊傷害": 40,
            "攻擊力": 20,
        },
        "feet_main_scores": {
            "速度": 40,
            "攻擊力": 35,
        },
        "good_sub_scores": {
            "暴擊率": 15,
            "暴擊傷害": 15,
            "速度": 12,
            "攻擊力": 8,
        },
    },
    "應天涉遠的卜者": {
        "body_main_scores": {
            "暴擊率": 40,
            "暴擊傷害": 40,
        },
        "feet_main_scores": {
            "速度": 40,
        },
        "good_sub_scores": {
            "暴擊率": 15,
            "暴擊傷害": 15,
            "速度": 15,
            "攻擊力": 8,
        },
    },
}
