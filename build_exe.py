#!/usr/bin/env python3
"""
PyInstaller 打包腳本 - 針對 HSR_BOT 優化
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def main():
    # 專案根目錄
    project_root = Path(__file__).parent.absolute()
    main_py = project_root / "main.py"
    icon_path = project_root / "icon.ico"
    
    print("=" * 70)
    print("🚀 開始打包 HSR_BOT...")
    print("=" * 70)
    print(f"📍 專案目錄: {project_root}")

    # 檢查必要檔案
    if not main_py.exists():
        print(f"❌ 找不到入口文件: {main_py}")
        sys.exit(1)

    # 清理舊的建置目錄
    for folder in ['build', 'dist']:
        path = project_root / folder
        if path.exists():
            print(f"🧹 清理 {folder} 目錄...")
            try:
                shutil.rmtree(path)
            except Exception as e:
                print(f"⚠️ 無法完全清理 {folder}: {e}")

    # 定義要包含的資料路徑
    image_dir = project_root / "images"
    config_py = project_root / "config.py"
    
    # 建構 PyInstaller 指令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",          # 使用目錄模式
        "--windowed",        # 隱藏控制台視窗
        "--name=HSR_BOT",
        "--uac-admin",       # 要求系統管理員權限
        
        # --- 關鍵依賴處理 ---
        "--collect-all", "cv2",
        "--collect-all", "mss",
        "--collect-all", "pyautogui",
        "--collect-all", "pytesseract",
        
        # 額外隱藏匯入
        "--hidden-import", "psutil",
    ]

    # 添加資料夾與檔案
    if image_dir.exists():
        cmd.append(f"--add-data={image_dir}{os.pathsep}images")
    if config_py.exists():
        cmd.append(f"--add-data={config_py}{os.pathsep}.")
    
    if icon_path.exists():
        print(f"🎨 套用圖標: {icon_path}")
        cmd.append(f"--icon={icon_path}")
    else:
        print(f"⚠️ 找不到 icon.ico，將使用系統預設圖標")

    # 最後加入入口文件
    cmd.append(str(main_py))

    print("\n📦 執行打包指令:")
    print(" ".join(cmd))
    print("=" * 70 + "\n")
    
    try:
        # 確保在目前的虛擬環境中執行 pyinstaller
        # 如果系統中有多個 python/pyinstaller，直接調用可能會出錯
        # 這裡假設使用者已經在虛擬環境中執行此腳本，或者 pyinstaller 在 PATH 中
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包過程中出錯: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n❌ 找不到 PyInstaller。請在虛擬環境中執行以下指令安裝：")
        print(f"   {sys.executable} -m pip install pyinstaller")
        sys.exit(1)

    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("✅ 打包完成！")
        print("=" * 70)
        exe_path = project_root / "dist" / "HSR_BOT" / "HSR_BOT.exe"
        print(f"📦 執行檔位置: {exe_path}")
        print("\n💡 重要提示：")
        print("   1. 此程式需要「系統管理員權限」才能正常操作遊戲視窗。")
        print("   2. 請確保電腦已安裝 Tesseract-OCR，並在 config.py 中正確設定路徑。")
        print("   3. 圖片資源已封裝進執行檔中。")
        print("   4. config.py 已複製到執行檔目錄，可直接編輯修改設定。")
    else:
        print("\n❌ 打包失敗！")
        sys.exit(1)

if __name__ == "__main__":
    main()
