import time
import psutil
import subprocess
import logging
import logging.handlers
import sys
import threading
import ctypes
from pathlib import Path

import actions
import config as cfg
import vision

# 日誌設定
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

log_file = BASE_DIR / "bot.log"
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# 創建 logger
logger = logging.getLogger('HSR_BOT')
logger.setLevel(logging.DEBUG)

# 日誌格式
log_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 文件處理器 - 使用輪轉日誌（每個日誌最大 10MB，保留 5 個文件）
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# 控制台處理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# 保存原始 print 函數，支持日誌記錄
_original_print = print
def print(*args, **kwargs):
    message = " ".join(map(str, args))
    logger.info(message)
    # 同時輸出到控制台（可選）
    # _original_print(message)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_game_running():
    try:
        for process in psutil.process_iter(["name"]):
            if process.info["name"] and "StarRail" in process.info["name"]:
                logger.debug(f"檢測到遊戲進程: {process.info['name']}")
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logger.warning("掃描進程時發生錯誤")
    return False

class Bot:
    def __init__(self):
        self.prev_state = None
        self.last_change_time = time.time()
        self.stuck_count = 0

        self.has_seen_home = False
        self.entrusted = False
        self.mail_handled = False
        self.daily_tasks = None
        self.stamina = None
        self.selected = False
        self.has_battled = False
        self.no_pass_reward = False
        self.has_claimed_pass = False
        self.should_stop_at_home = False
        self.stop_running = False
        self.isCrafted = False
        self.stop_requested = False

        self.handlers = {
            cfg.LOGIN_1: self.handle_login,
            cfg.LOGIN_2: self.handle_login,
            cfg.HOME: self.handle_home,
            cfg.MAIN_MENU: self.handle_main_menu,
            cfg.CLAIM_ENTRUST: self.handle_claim_entrust,
            cfg.SUCCESSFULLY_CLAIM: self.handle_successfully_claim,
            cfg.ENTRUSTED: self.handle_entrusted,
            cfg.CLAIM_MAIL: self.handle_claim_mail,
            cfg.DELETE: self.handle_delete,
            cfg.REWARD_PAGE: self.handle_reward_page,
            cfg.TASK_PAGE: self.handle_task_page,
            cfg.PREPARE: self.handle_prepare,
            cfg.PREPARED: self.handle_prepared,
            cfg.INSUFFICIENT_PHYSICAL_STRENGTH: self.handle_insufficient_physical_strength,
            cfg.CONFIRM: self.handle_confirm,
            cfg.CHALLENGE_SUCCESSFUL: self.handle_challenge_successful,
            cfg.START_CHALLENGE_1: self.handle_start_challenge_1,
            cfg.START_CHALLENGE_2: self.handle_start_challenge_2,
            cfg.STATE: self.handle_state_page,
            cfg.SELECTED_1: self.handle_selected,
            cfg.SELECTED_2: self.handle_selected,
            cfg.SELECT_END: self.handle_select_end,
            cfg.PASS_PAGE: self.handle_pass_page,
            cfg.PASS_MISSION_PAGE: self.handle_pass_mission_page,
            cfg.QUICK_COLLECTION: self.handle_quick_collection,
            cfg.CRAFTING_PAGE: self.handle_crafting_page,
            cfg.CONFIRM_CRAFT: self.handle_confirm_craft,
        }

    def start_game(self):
        if not is_game_running():
            if cfg.GAME_PATH.exists():
                logger.info(f"啟動遊戲中... 路徑: {cfg.GAME_PATH}")
                try:
                    subprocess.Popen(str(cfg.GAME_PATH))
                    logger.info("遊戲進程已啟動，等待 15 秒...")
                    time.sleep(15)
                    logger.info("遊戲啟動完成")
                except Exception as e:
                    logger.error(f"啟動遊戲失敗: {e}")
            else:
                logger.error(f"找不到遊戲執行檔: {cfg.GAME_PATH}，請檢查 config.py 中的 GAME_PATH")
        else:
            logger.info("遊戲已在運行中")

    def reset_stuck_timer(self):
        self.last_change_time = time.time()
        self.stuck_count = 0

    def check_stuck(self, state):
        if state == cfg.BATTLE:
            return None

        if time.time() - self.last_change_time > cfg.STUCK_TIME:
            self.stuck_count += 1
            logger.warning(f"檢測到卡住: 計數 {self.stuck_count}，當前狀態: {state}")
            if self.stuck_count >= 2:
                logger.error("檢測到卡住且無法恢復")
                return "stop"

        return None

    def listen_keyboard(self):
        logger.info("鍵盤監聽已啟動 (按 F8 停止 Bot)...")
        # 使用 ctypes 獲取 GetAsyncKeyState，更穩定且不依賴 pywin32 的包裝
        user32 = ctypes.windll.user32
        VK_F8 = 0x77
        
        while not self.stop_running:
            try:
                # 偵測 F8 (高位為 1 表示按下)
                if user32.GetAsyncKeyState(VK_F8) & 0x8000:
                    logger.warning("=" * 30)
                    logger.warning("偵測到 F8 按下，正在停止 Bot...")
                    logger.warning("=" * 30)
                    self.stop_requested = True
                    self.stop_running = True
                    break
            except Exception as e:
                logger.error(f"鍵盤監聽錯誤: {e}")
                break
            time.sleep(0.1)

    def run(self):
        logger.info("=" * 50)
        logger.info("Bot 啟動準備...")
        
        # 檢查管理員權限
        if not is_admin():
            logger.warning("!" * 50)
            logger.warning("警告: 未以系統管理員權限執行！")
            logger.warning("這可能會導致無法監聽 F8 鍵或無法操作遊戲視窗。")
            logger.warning("!" * 50)
        
        # 提前啟動鍵盤監聽執行緒，確保在啟動遊戲期間也能響應 F8
        listener_thread = threading.Thread(target=self.listen_keyboard, daemon=True)
        listener_thread.start()
        
        self.start_game()
        logger.info("Bot 開始運行")

        cycle_count = 0
        while True:
            if self.stop_requested or self.stop_running:
                logger.warning("Bot 已停止運行")
                actions.release_alt()
                break

            # 檢查遊戲是否仍在運行
            if not is_game_running():
                logger.error("檢測到遊戲已關閉，Bot 停止運行")
                actions.release_alt()
                break

            # 判斷是否停止運行
            if self.has_seen_home and self.has_claimed_pass and self.stamina is not None and self.stamina < 40: 
                if self.daily_tasks is True:
                    logger.info("任務完成且體力不足，正在關閉遊戲...")
                    actions.close_game()
                    break
                elif self.isCrafted is False:
                    continue

                self.should_stop_at_home = True

            cycle_count += 1
            screen = vision.capture_screen()
            state = vision.detect_state(screen)
            
            if state != self.prev_state:
                self.reset_stuck_timer()
                self.prev_state = state
                logger.info(f"[第 {cycle_count} 循環] 狀態變更為: {state}")
            else:
                logger.debug(f"[第 {cycle_count} 循環] 當前狀態: {state}")

            stuck_status = self.check_stuck(state)
            if stuck_status == "stop":
                logger.error("檢測到卡住且無法恢復，停止運行")
                actions.release_alt()
                break

            handler = self.handlers.get(state, self.handle_unknown_state)
            handler(screen)

            if self.stop_running:
                actions.release_alt()
                break

    def handle_login(self, screen):
        logger.info("檢測到登入界面，執行登入操作...")
        actions.login_action()
        time.sleep(3)

    def handle_home(self, screen):
        if self.should_stop_at_home:
            if self.daily_tasks is True:
                logger.info("任務已完成，Bot 停止運行")
            elif self.daily_tasks is False:
                logger.info("體力不足且已執行完相關操作，停止運行")
            self.stop_running = True
            return
        if self.has_seen_home is False:
            logger.info("首次到達主界面，執行主界面操作...")
            actions.home_action()
            time.sleep(0.5)

        elif self.daily_tasks is None or (self.has_battled and self.daily_tasks is False):
            self.has_battled = False
            logger.debug("執行任務操作...")
            actions.action_action()
            time.sleep(0.5)

        elif not self.has_claimed_pass:
            logger.info("執行通行證領取...")
            actions.pass_action()
            time.sleep(0.5)

    def handle_main_menu(self, screen):
        logger.info("進入主選單")
        self.has_seen_home = True

        if not self.entrusted:
            self.entrusted = True
            logger.info("執行委託操作...")
            actions.entrust_action()
            time.sleep(1)
            return

        if not self.mail_handled:
            if vision.match(screen, vision.TEMPLATES["has mail"], 0.90):
                self.mail_handled = True
                logger.info("檢測到郵件，執行領取操作...")
                actions.mail_action()
                time.sleep(1)
                return

            if vision.match(screen, vision.TEMPLATES["mail"], 0.90):
                self.mail_handled = True
                actions.leave_action()
                time.sleep(1)

    def handle_claim_entrust(self, screen):
        actions.claim_entrust_action()
        time.sleep(0.5)

    def handle_successfully_claim(self, screen):
        actions.successfully_claim_action()
        time.sleep(0.5)

    def handle_entrusted(self, screen):
        actions.leave_action()
        time.sleep(0.5)

    def handle_claim_mail(self, screen):
        actions.claim_mail_action()
        time.sleep(0.5)

    def handle_delete(self, screen):
        actions.leave_action()
        time.sleep(1)
        actions.leave_action()
        time.sleep(1)

    def handle_reward_page(self, screen):
        if vision.match(screen, vision.TEMPLATES["schedule"], 0.95):
            self.daily_tasks = False
            while not self.stop_requested:
                screen = vision.capture_screen()
                reward_1 = vision.match(screen, vision.TEMPLATES["claim reward_1"], 0.95)
                reward_2 = vision.match(screen, vision.TEMPLATES["claim reward_2"], 0.95)
                if not reward_1 and not reward_2:
                    break
                actions.claim_reward_action()
                time.sleep(1)
            
            if self.stop_requested:
                return

            if vision.match(screen, vision.TEMPLATES["claim schedule"]):
                actions.claim_schedule_action()
                time.sleep(0.5)
                return
        if vision.match(screen, vision.TEMPLATES["finish"]):
            self.daily_tasks = True
        if self.stamina is None or self.stamina >= 40:
            actions.task_action()
            time.sleep(0.5)
            return
        if self.daily_tasks is True:
            actions.leave_action()
            time.sleep(0.5)
        elif self.stamina is not None and self.stamina < 40 and self.isCrafted is False:
            vision.click_task_button("萬")
            time.sleep(0.5)

    def handle_task_page(self, screen):
        stamina = vision.get_stamina()
        self.stamina = stamina
        if stamina >= 40:
            self.has_battled = False
        if stamina >= 30 and vision.match(screen, vision.TEMPLATES["quick farm"], 0.95):
            actions.quick_farm_action()
            time.sleep(0.5)
            return
        if self.daily_tasks is False and (stamina is not None and stamina >= 40) or (stamina is not None and stamina >= 40):
            actions.enter_action()
            time.sleep(0.5)
        elif self.daily_tasks is None or (self.daily_tasks is False and self.isCrafted is False):
            actions.reward_action()
            time.sleep(0.5)
        else:
            actions.leave_action()
            time.sleep(0.5)

    def handle_crafting_page(self, screen):
        if self.isCrafted:
            actions.leave_action()
            time.sleep(0.5)
            return
        actions.cookie_action()
        time.sleep(0.5)
        actions.crafting_action()
        time.sleep(0.5)

    def handle_confirm_craft(self, screen):
        actions.confirm_action()
        time.sleep(1)
        self.isCrafted = True

    def handle_prepare(self, screen):
        if self.has_battled or (self.stamina is None or self.stamina < 40):
            actions.leave_action()
            time.sleep(0.5)
            return
        actions.prepare_action()
        time.sleep(0.5)

    def handle_prepared(self, screen):
        actions.start_action()
        time.sleep(0.5)

    def handle_insufficient_physical_strength(self, screen):
        actions.leave_action()
        time.sleep(0.5)
        actions.reduce_action()
        time.sleep(0.5)
        actions.start_action()
        time.sleep(0.5)
        
    def handle_start_challenge_1(self, screen):
        actions.start_challenge_action_1()
        time.sleep(0.5)

    def handle_start_challenge_2(self, screen):
        actions.start_challenge_action_2()
        time.sleep(0.5)

    def handle_confirm(self, screen):
        actions.confirm_action()
        time.sleep(1)

    def handle_challenge_successful(self, screen):
        self.has_battled = True
        if self.selected:
            actions.exit_stage_action()
            time.sleep(2)
        else:
            if vision.match(screen, vision.TEMPLATES["device"]):
                actions.select_action()
                time.sleep(1)

    def handle_state_page(self, screen):
        if vision.match(screen, vision.TEMPLATES["suitable"]):
            actions.locking_action()
            time.sleep(1)
            actions.next_action()
            time.sleep(1)
            return

        relic = vision.parse_relic(screen)
        print(relic)
        score = vision.score_relic(relic)
        print("遺物評分:", score)
        if score == "未知遺器":
            actions.next_action()
            time.sleep(1)
            return
        elif score >= 50:
            actions.locking_action()
        else:
            actions.discard_action()
        time.sleep(1)
        actions.next_action()
        time.sleep(1)

    def handle_selected(self, screen):
        actions.next_action()
        time.sleep(1)

    def handle_select_end(self, screen):
        self.selected = True
        actions.leave_action()
        time.sleep(0.5)

    def handle_pass_page(self, screen):
        if not self.no_pass_reward and vision.match(screen, vision.TEMPLATES["hasPassMissionReward"], 0.95):    
            actions.has_pass_mission_reward_action()
            time.sleep(0.5)
            return
        if not vision.match(screen, vision.TEMPLATES["hasPassMissionReward"], 0.95):
            actions.quick_claim_action()
            time.sleep(0.5)
        # if not vision.match(screen, vision.TEMPLATES["hasPassReward"], 0.8):
            actions.leave_action()
            self.has_claimed_pass = True
            time.sleep(0.5)

    def handle_pass_mission_page(self, screen):
        if vision.match(screen, vision.TEMPLATES["quick claim"]):
            actions.quick_claim_action()
            time.sleep(0.5)
        else:
            print("沒有快速領取，檢測是否有通行證任務獎勵")
            print(vision.match(screen, vision.TEMPLATES["hasPassReward"], 0.8))
            self.no_pass_reward = True
            if vision.match(screen, vision.TEMPLATES["hasPassReward"], 0.8):
                actions.has_pass_reward_action()
                time.sleep(0.5)
                return
            actions.leave_action()
            time.sleep(0.5)

    def handle_quick_collection(self, screen):
        if vision.match(screen, vision.TEMPLATES["closure"]):
            actions.closure_action()
            time.sleep(0.5)
            return
        actions.maximum_action()
        time.sleep(0.5)
        actions.confirm_action()
        time.sleep(0.5)

    def handle_unknown_state(self, screen):
        logger.warning("檢測到未知狀態，嘗試等待或手動操作")
        time.sleep(1)

if __name__ == "__main__":
    try:
        logger.info(f"Bot 程序啟動，執行文件: {sys.argv[0]}")
        logger.info(f"工作目錄: {BASE_DIR}")
        Bot().run()
    except KeyboardInterrupt:
        logger.warning("收到中斷信號，正在關閉...")
    except Exception as e:
        logger.critical(f"程序發生未預期的錯誤: {e}", exc_info=True)
    finally:
        logger.info("=" * 50)
        logger.info("Bot 程序已結束")
