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

        time.sleep(2)

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
    click_image(cfg.PATH["entrust"])


def claim_entrust_action():
    click_image(cfg.PATH["claim entrust"])


def successfully_claim_action():
    click((960, 850))


def leave_action():
    release_alt()
    pyautogui.press("esc")
    time.sleep(0.5)
    press_alt()


def mail_action():
    click_image(cfg.PATH["has mail"])


def claim_mail_action():
    click_image(cfg.PATH["claim mail"])


def action_action():
    press_alt()
    click_image(cfg.PATH["action"])


def task_action():
    click_image(cfg.PATH["task"])


def reward_action():
    click_image(cfg.PATH["reward"])


def crafting_action():
    click_image(cfg.PATH["crafting"])


def cookie_action():
    click_image(cfg.PATH["cookie"])


def enter_action():
    click_image(cfg.PATH["enter"])


def claim_reward_action():
    click_image(cfg.PATH["claim reward_1"])
    click_image(cfg.PATH["claim reward_2"])


def prepare_action():
    click_image(cfg.PATH["prepare"])


def start_action():
    click_image(cfg.PATH["challenge"])


def reduce_action():
    click_image(cfg.PATH["reduce"])


def claim_schedule_action():
    click_image(cfg.PATH["claim schedule"])


def start_challenge_action_1():
    click_image(cfg.PATH["start_challenge_1"])


def start_challenge_action_2():
    click_image(cfg.PATH["start_challenge_2"])


def confirm_action():
    click_image(cfg.PATH["confirm"], 0.95)


def select_action():
    click_image(cfg.PATH["device"])


def locking_action():
    click_image(cfg.PATH["locking"])


def discard_action():
    click_image(cfg.PATH["discard"])


def next_action(screen):
    if match(screen, TEMPLATES["next_1"]):
        click_image(cfg.PATH["next_1"])
        return

    if match(screen, TEMPLATES["next_2"]):
        click_image(cfg.PATH["next_2"])
        return


def exit_stage_action():
    click_image(cfg.PATH["exit stage"])


def pass_action():
    click_image(cfg.PATH["pass"])

def has_pass_mission_reward_action():
    click_image(cfg.PATH["hasPassMissionReward"])


def quick_claim_action():
    click_image(cfg.PATH["quick claim"])


def has_pass_reward_action():
    click_image(cfg.PATH["hasPassReward"], 0.8)


def quick_farm_action():
    click_image(cfg.PATH["quick farm"])


def maximum_action():
    click_image(cfg.PATH["maximum"])


def closure_action():
    click_image(cfg.PATH["closure"])


def pass_page_action():
    click_image(cfg.PATH["pass page"])


def recover():
    print("⚠ 修復中（回主畫面）")
    for _ in range(4):
        pyautogui.press("esc")
        time.sleep(1)