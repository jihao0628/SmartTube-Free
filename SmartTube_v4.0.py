# SmartTube Free v4.0 - 開源免費版本
# 基於 yt-dlp 的開源影片下載工具
import os
import json
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from yt_dlp import YoutubeDL

# === 基本設定 / Basic Settings ===
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "SmartTube")
os.makedirs(DEFAULT_DOWNLOAD_FOLDER, exist_ok=True)
APP_VERSION = "4.0"

# === 作者資訊 / Author Information ===
AUTHOR = "by jihao"
RELEASE_DATE = "2025.10.6"

# === 多語言支援 / Multi-language Support ===
LANGUAGES = {
    "zh_tw": {
        "language_name": "繁體中文",
        "title": "SmartTube",
        "status": "狀態",
        "ready": "就緒",
        "enter_url": "請輸入影片網址 (YouTube, Bilibili, Vimeo...)",
        "download_path": "下載路徑",
        "set_download_path": "📂 設定下載路徑",
        "download_video": "下載影片",
        "open_folder": "開啟下載資料夾",
        "error_title": "錯誤",
        "error_no_url": "請輸入影片網址！",
        "download_complete": "下載完成",
        "download_failed": "下載失敗",
        "extracting": "擷取中",
        "downloading": "下載中",
        "downloading_connecting": "下載中 (連線中...)",
        "complete_msg": "影片已下載至：",
        "choose_language": "選擇語言",
        "unlimited_downloads": "✅ 完全免費，無限下載",
        "open_source": "🔓 開源軟體",
        "author_info": "作者：jihao",
        "version_info": "版本：v4.0"
    },
    "zh_cn": {
        "language_name": "简体中文",
        "title": "SmartTube",
        "status": "状态",
        "ready": "就绪",
        "enter_url": "请输入视频网址 (YouTube, Bilibili, Vimeo...)",
        "download_path": "下载路径",
        "set_download_path": "📂 设置下载路径",
        "download_video": "下载视频",
        "open_folder": "打开下载文件夹",
        "error_title": "错误",
        "error_no_url": "请输入视频网址！",
        "download_complete": "下载完成",
        "download_failed": "下载失败",
        "extracting": "提取中",
        "downloading": "下载中",
        "downloading_connecting": "下载中 (连接中...)",
        "complete_msg": "视频已下载至：",
        "choose_language": "选择语言",
        "unlimited_downloads": "✅ 完全免费，无限下载",
        "open_source": "🔓 开源软件",
        "author_info": "作者：jihao",
        "version_info": "版本：v4.0"
    },
    "en": {
        "language_name": "English",
        "title": "SmartTube",
        "status": "Status",
        "ready": "Ready",
        "enter_url": "Enter video URL (YouTube, Bilibili, Vimeo...)",
        "download_path": "Download Path",
        "set_download_path": "📂 Set Download Path",
        "download_video": "Download Video",
        "open_folder": "Open Download Folder",
        "error_title": "Error",
        "error_no_url": "Please enter video URL!",
        "download_complete": "Download Complete",
        "download_failed": "Download Failed",
        "extracting": "Extracting",
        "downloading": "Downloading",
        "downloading_connecting": "Downloading (Connecting...)",
        "complete_msg": "Video downloaded to:",
        "choose_language": "Choose Language",
        "unlimited_downloads": "✅ Completely Free, Unlimited Downloads",
        "open_source": "🔓 Open Source Software",
        "author_info": "by jihao",
        "version_info": "Version: v4.0"
    }
}

# === 設定檔處理 / Settings File Handling ===
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".smarttube_free_settings.json")

def save_settings(data):
    """儲存設定"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except:
        pass

def load_settings():
    """載入設定"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# === 語言設定處理 / Language Setting Handling ===
def load_language_setting():
    """載入語言設定"""
    data = load_settings()
    return data.get("language", "en")  # 預設英文 / Default: English

def save_language_setting(lang_code):
    """儲存語言設定"""
    data = load_settings()
    data["language"] = lang_code
    save_settings(data)

# 當前語言 / Current language
CURRENT_LANG = load_language_setting()

def t(key):
    """取得翻譯文字 / Get translated text"""
    return LANGUAGES[CURRENT_LANG].get(key, key)

# === 下載資料夾設定 / Download Folder Settings ===
def get_download_folder():
    """取得下載資料夾路徑"""
    data = load_settings()
    return data.get("download_path", DEFAULT_DOWNLOAD_FOLDER)

def set_download_folder(path):
    """設定下載資料夾路徑"""
    data = load_settings()
    data["download_path"] = path
    save_settings(data)

# === 動畫控制 / Animation Control ===
animating = False
anim_after_id = None
anim_pos = 0

def start_animation(progress_bar):
    """開始進度條動畫"""
    global animating, anim_after_id, anim_pos
    if animating:
        return
    animating = True
    anim_pos = 0
    def step():
        global animating, anim_after_id, anim_pos
        if not animating:
            return
        anim_pos += 0.03
        if anim_pos > 1:
            anim_pos = 0
        progress_bar.set(anim_pos)
        anim_after_id = app.after(100, step)
    anim_after_id = app.after(100, step)

def stop_animation(progress_bar):
    """停止進度條動畫"""
    global animating, anim_after_id
    animating = False
    if anim_after_id:
        app.after_cancel(anim_after_id)
    progress_bar.set(0)

# === 狀態顯示 / Status Display ===
def set_status_text(text):
    """設定狀態文字"""
    app.after(0, lambda: title_label.configure(text=f"🎬 {t('title')} v{APP_VERSION}\n{t('status')}：{text}"))

# === 進度處理 / Progress Handling ===
def compute_percent(d):
    """計算下載進度百分比"""
    downloaded = d.get("downloaded_bytes") or 0
    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
    if total:
        return downloaded / total
    frag_i, frag_c = d.get("fragment_index"), d.get("fragment_count")
    if frag_i and frag_c:
        return frag_i / frag_c
    p = d.get("_percent_str")
    if p:
        try:
            return float(p.strip('%')) / 100
        except:
            pass
    return None

def progress_hook(d, bar):
    """下載進度回調函數"""
    if d["status"] == "downloading":
        pct = compute_percent(d)
        if pct is not None:
            stop_animation(bar)
            app.after(0, lambda: bar.set(min(1, max(0, pct))))
            set_status_text(f"{t('downloading')} {pct*100:.1f}%")
        else:
            start_animation(bar)
            set_status_text(t('downloading_connecting'))
    elif d["status"] == "finished":
        stop_animation(bar)
        app.after(0, lambda: bar.set(1))
        set_status_text(t('download_complete'))

# === 下載執行 / Download Execution ===
def download_video(url, bar):
    """下載影片主函數"""
    try:
        set_status_text(t('extracting'))
        folder = path_entry.get().strip() or get_download_folder()
        set_download_folder(folder)
        ydl_opts = {
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "progress_hooks": [lambda d: progress_hook(d, bar)],
            "merge_output_format": "mp4",
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        stop_animation(bar)
        set_status_text(t('download_complete'))
        messagebox.showinfo(t('download_complete'), f"{t('complete_msg')}\n{folder}")
    except Exception as e:
        stop_animation(bar)
        set_status_text(t('download_failed'))
        messagebox.showerror(t('error_title'), f"{t('download_failed')}：{e}")

# === 語言切換功能 / Language Switch Function ===
def switch_language(choice):
    """切換語言"""
    global CURRENT_LANG
    for lang_code, lang_data in LANGUAGES.items():
        if lang_data["language_name"] == choice:
            CURRENT_LANG = lang_code
            save_language_setting(lang_code)
            break
    update_ui_language()

def update_ui_language():
    """更新所有UI元素的文字"""
    # 更新標題
    app.title(f"{t('title')} v{APP_VERSION} - {AUTHOR}")
    
    # 更新主標題標籤
    title_text = f"🎬 {t('title')} v{APP_VERSION}\n{t('status')}：{t('ready')}\n{t('unlimited_downloads')}"
    title_label.configure(text=title_text)
    
    # 更新其他UI元素
    url_entry.configure(placeholder_text=t('enter_url'))
    path_label.configure(text=f"{t('download_path')}：")
    set_folder_btn.configure(text=t('set_download_path'))
    download_btn.configure(text=t('download_video'))
    open_folder_btn.configure(text=t('open_folder'))
    
    # 更新語言選擇框
    language_optionmenu.configure(values=[LANGUAGES[lang]["language_name"] for lang in LANGUAGES])
    
    # 更新作者資訊標籤
    author_label.configure(text=f"{AUTHOR} | {RELEASE_DATE}")
    
    # 更新狀態
    set_status_text(t('ready'))

# === UI ===
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("520x580")  # 增加高度以容納作者資訊
app.title(f"{t('title')} v{APP_VERSION} - {AUTHOR}")

# 語言選擇框架
lang_frame = ctk.CTkFrame(app)
lang_frame.pack(pady=10)

ctk.CTkLabel(lang_frame, text="🌐 Language:").pack(side="left", padx=5)

# 創建下拉式選單
language_optionmenu = ctk.CTkOptionMenu(
    lang_frame, 
    values=[LANGUAGES[lang]["language_name"] for lang in LANGUAGES],
    command=switch_language,
    width=120
)
current_language_name = LANGUAGES[CURRENT_LANG]["language_name"]
language_optionmenu.set(current_language_name)
language_optionmenu.pack(side="left", padx=5)

# 標題標籤
title_label = ctk.CTkLabel(
    app, 
    text=f"🎬 {t('title')} v{APP_VERSION}\n{t('status')}：{t('ready')}\n{t('unlimited_downloads')}", 
    font=("Microsoft JhengHei", 18, "bold")
)
title_label.pack(pady=15)

# URL 輸入框
url_entry = ctk.CTkEntry(app, width=400, placeholder_text=t('enter_url'))
url_entry.pack(pady=10)

# 進度條
progress = ctk.CTkProgressBar(app, width=400)
progress.set(0)
progress.pack(pady=10)

# 下載路徑設定區
path_frame = ctk.CTkFrame(app)
path_frame.pack(pady=10)

path_label = ctk.CTkLabel(path_frame, text=f"{t('download_path')}：", font=("Microsoft JhengHei", 12))
path_label.pack(side="left", padx=5)

path_entry = ctk.CTkEntry(path_frame, width=280)
path_entry.insert(0, get_download_folder())
path_entry.pack(side="left", padx=5)

def choose_folder():
    """選擇下載資料夾"""
    folder = filedialog.askdirectory(title=t('set_download_path'))
    if folder:
        path_entry.delete(0, "end")
        path_entry.insert(0, folder)
        set_download_folder(folder)

set_folder_btn = ctk.CTkButton(
    path_frame, 
    text=t('set_download_path'), 
    command=choose_folder, 
    width=120
)
set_folder_btn.pack(side="left", padx=5)

# 下載按鈕
def start_download():
    """開始下載"""
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning(t('error_title'), t('error_no_url'))
        return
    threading.Thread(target=download_video, args=(url, progress), daemon=True).start()

download_btn = ctk.CTkButton(
    app, 
    text=t('download_video'), 
    command=start_download,
    height=35,
    font=("Microsoft JhengHei", 14, "bold")
)
download_btn.pack(pady=10)

# 開啟資料夾按鈕
def open_folder():
    """開啟下載資料夾"""
    os.startfile(path_entry.get().strip() or get_download_folder())

open_folder_btn = ctk.CTkButton(
    app, 
    text=t('open_folder'), 
    command=open_folder
)
open_folder_btn.pack(pady=5)

# 開源資訊標籤
opensource_label = ctk.CTkLabel(
    app, 
    text=t('open_source'),
    font=("Microsoft JhengHei", 10),
    text_color="green"
)
opensource_label.pack(pady=5)

# 作者資訊標籤
author_label = ctk.CTkLabel(
    app,
    text=f"{AUTHOR} | {RELEASE_DATE}",
    font=("Microsoft JhengHei", 10),
    text_color="gray"
)
author_label.pack(pady=5)

# 初始化UI
update_ui_language()

app.mainloop()