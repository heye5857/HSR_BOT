# HSR_BOT

HSR_BOT 是一個針對《崩壞：星穹鐵道》的自動化機器人，採用螢幕圖像辨識與按鍵模擬來完成委託、郵件領取、日常任務、通行證領取與簡易遺物評分等流程。

## 主要功能

- 自動啟動遊戲（若尚未運行）
- 自動處理登入與主選單操作
- 自動完成委託與郵件領取
- 自動操作日常任務與戰鬥進程
- 自動辨識與評分遺物
- 支援 F8 停止 Bot

## 專案結構

- `main.py`：Bot 入口與主要控制流程
- `config.py`：遊戲路徑、OCR 設定與圖像資源路徑配置
- `actions.py`：遊戲操作對應動作（點擊、按鍵、離開等）
- `vision.py`：螢幕截圖、範本匹配、OCR 讀取與遺物評分
- `build_exe.py`：PyInstaller 打包腳本
- `requirements.txt`：Python 依賴套件
- `images/`：圖像範本資源
- `logs/`：運行日誌儲存目錄

## 使用說明

### 1. 環境準備

1. 建議使用 Python 虛擬環境，例如：
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. 安裝 Python 依賴套件：
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. 安裝 Tesseract-OCR
   - 下載並安裝 Tesseract-OCR
   - 在 `config.py` 中確認 `TESSERACT_CMD` 路徑正確指向 `tesseract.exe`

### 2. 設定 `config.py`

- `GAME_PATH`：設定遊戲執行檔 `StarRail.exe` 的實際路徑
- `TESSERACT_CMD`：設定 Tesseract 可執行檔的路徑
- `OCR_LANG`：指定 OCR 語言，預設為 `chi_tra`
- `IMAGE_DIR`：請保留 `images/` 資料夾內的圖像資源

### 3. 執行 Bot

在啟用虛擬環境後執行：

```powershell
python main.py
```

> 建議以系統管理員權限執行，否則可能無法正常監聽 F8 或操控遊戲視窗。

### 4. 停止 Bot

- 按 `F8` 即可請求停止
- Bot 會在下次檢測到停止請求時結束運行

## 打包成執行檔

若要生成可執行檔，請先安裝 `PyInstaller`：

```powershell
python -m pip install pyinstaller
```

然後執行：

```powershell
python build_exe.py
```

打包完成後，可在 `dist\HSR_BOT\HSR_BOT.exe` 找到產生的執行檔。

## 注意事項

- 請確認遊戲已安裝，且 `config.py` 中的 `GAME_PATH` 路徑正確。
- OCR 效果依螢幕解析度、顯示設定與遊戲介面而異，若有辨識問題請檢查螢幕解析度與 DPI 設定。
- `images/` 資料夾內的範本圖需與遊戲畫面一致，若遊戲版本或介面更新，可能需要更新範本圖像。
- 若出現 `找不到圖片` 或 `OCR 文字` 失敗情況，請先確認遊戲畫面處於預期畫面。

## 依賴套件

- `opencv-python`
- `numpy`
- `psutil`
- `pyautogui`
- `pytesseract`
- `mss`

## 授權與版權

此專案僅供個人自動化與學習使用。請遵守遊戲開發商的使用條款與規定。