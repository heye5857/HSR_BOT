import ctypes
import time
import pyautogui
import config as cfg
from vision import click_image, TEMPLATES, match

ALT = 0x12
pyautogui.FAILSAFE = False


def close_game():

        print("關閉遊戲...")

        pyautogui.hotkey("alt", "f4")

        time.sleep(1)

def press_alt():
    ctypes.windll.user32.keybd_event(ALT, 0, 0, 0)


def release_alt():
    ctypes.windll.user32.keybd_event(ALT, 0, 2, 0)


def click(pos):
    pyautogui.click(pos[0], pos[1])


def login_action():
    click((960, 540))


def home_action():
    release_alt()
    time.sleep(0.2)
    pyautogui.press("esc")


def entrust_action():
    click_image("entrust")


def claim_entrust_action():
    click_image("claim entrust")


def successfully_claim_action():
    click(cfg.CLICK_CONFIRM)


def leave_action():
    release_alt()
    pyautogui.press("esc")
    time.sleep(0.2)
    press_alt()


def mail_action():
    click_image("has mail")


def claim_mail_action():
    click_image("claim mail")


def action_action():
    press_alt()
    click_image("action")


def task_action():
    click_image("task")


def reward_action():
    click_image("reward")


def crafting_action():
    click_image("crafting")


def cookie_action():
    click_image("cookie")


def enter_action():
    click_image("enter")


def claim_reward_action():
    click_image("claim reward_1")
    click_image("claim reward_2")


def prepare_action():
    click_image("prepare")


def start_action():
    click_image("challenge")


def reduce_action():
    click_image("reduce")


def claim_schedule_action():
    click_image("claim schedule")


def start_challenge_action_1():
    click_image("start_challenge_1")


def start_challenge_action_2():
    click_image("start_challenge_2")


def confirm_action():
    click_image("confirm", 0.95)


def select_action():
    click_image("device")


def locking_action():
    """使用座標直接鎖定，避免模板匹配。"""
    click(cfg.CLICK_LOCKING)


def discard_action():
    """使用座標直接丢棄，避免模板匹配。"""
    click(cfg.CLICK_DISCARD)


def next_action(screen):
    """使用座標直接點擊下一步，避免模板匹配。"""
    click(cfg.CLICK_NEXT)


def exit_stage_action():
    click_image("exit stage")


def pass_action():
    click_image("pass")

def has_pass_mission_reward_action():
    click_image("hasPassMissionReward")


def quick_claim_action():
    click_image("quick claim")


def has_pass_reward_action():
    click_image("hasPassReward", 0.8)


def quick_farm_action():
    click_image("quick farm")


def maximum_action():
    click_image("maximum")


def closure_action():
    click_image("closure")


def pass_page_action():
    click_image("pass page")


