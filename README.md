# HSR_BOT

HSR_BOT 是專為《崩壞：星穹鐵道》設計的自動化機器人，透過螢幕截圖、影像辨識與 OCR 文字識別來模擬操作，自動完成遊戲中的常見流程。

## 主要功能

- 自動啟動遊戲（若尚未運行）
- 自動處理登入、主選單與日常流程
- 自動完成委託與郵件領取
- 自動執行日常任務與通行證獎勵領取
- 自動辨識遺物畫面並進行簡易評分
- 支援 `F8` 停止、`F9` 暫停、`F10` 繼續 Bot
- 運行日誌輸出至 `bot.log` 與 `logs/` 資料夾

## 專案結構

- `main.py`：Bot 入口與主要控制流程
- `config.py`：遊戲執行路徑、OCR 設定、範本資源路徑與狀態定義
- `actions.py`：遊戲操作對應函式（點擊、熱鍵、返回、恢復等）
- `vision.py`：螢幕截圖、模板匹配、OCR 文字讀取、遺物解析與評分
- `build_exe.py`：PyInstaller 打包腳本
- `requirements.txt`：Python 依賴套件清單
- `images/`：遊戲畫面模板資源
- `logs/`：運行日誌目錄

## 環境需求

- Python 3.10 或更新版本
- Windows 系統
- Tesseract-OCR 已安裝且可執行
- 建議以系統管理員權限執行 Bot，以提升鍵盤偵測與視窗操作穩定性

## 快速安裝

### 1. 建立虛擬環境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安裝 Python 依賴

```powershell
python -m pip install -r requirements.txt
```

### 3. 安裝 Tesseract-OCR

1. 下載並安裝 Tesseract-OCR。
2. 在 `config.py` 中確認 `TESSERACT_CMD` 指向 `tesseract.exe`。

### 4. 設定 `config.py`

- `GAME_PATH`：設定遊戲執行檔 `StarRail.exe` 的實際路徑
- `TESSERACT_CMD`：設定 Tesseract 執行檔的路徑
- `OCR_LANG`：OCR 語言，預設為 `chi_tra`
- `MATCH_THRESHOLD`：影像匹配置信度閾值
- `STUCK_TIME`：判斷卡住的秒數
- `IMAGE_DIR`：保留 `images/` 中的模板圖像

## 執行 Bot

```powershell
python main.py
```

> 若要提高穩定性，建議以系統管理員權限執行。

## 快捷鍵

- `F8` — 停止 Bot
- `F9` — 暫停 Bot（放開 Alt）
- `F10` — 繼續 Bot

## 打包成可執行檔

若要生成可執行檔，請先安裝 `PyInstaller`：

```powershell
python -m pip install pyinstaller
```

然後執行：

```powershell
python build_exe.py
```

完成後，可在 `dist\HSR_BOT\HSR_BOT.exe` 找到執行檔。

## 注意事項

- 請確認 `config.py` 中的 `GAME_PATH` 正確指向 StarRail 遊戲執行檔。
- OCR 識別效果受螢幕解析度、DPI、遊戲語言與畫面顯示設定影響。
- 若出現 `找不到圖片` 或 OCR 辨識失敗，請確認遊戲畫面為預期畫面，並檢查 `images/` 模板是否與遊戲畫面一致。
- 專案僅供個人學習與自動化測試使用，請遵守遊戲開發商的使用條款。

## 依賴套件

- `opencv-python`
- `numpy`
- `psutil`
- `pyautogui`
- `pytesseract`
- `mss`
