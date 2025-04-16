# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import sys
import pickle
import time
import shutil
import logging
import json
import webbrowser
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set, Any
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from threading import Thread
import requests
from io import BytesIO
from PIL import Image, ImageTk

try:
    import google_auth_oauthlib.flow
    import google.auth.transport.requests
    import googleapiclient.discovery
    import googleapiclient.errors
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("Ошибка: Необходимые библиотеки Google API не найдены.")
    print("Пожалуйста, установите их:")
    print("pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# --- Логирование ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)
stats = defaultdict(int)

# --- Файлы настроек и состояния ---
STATE_FILE = Path("processing_state.json")
SETTINGS_FILE = Path("settings.json")
TOKEN_PICKLE_FILE = Path("token.pickle")
UPLOADED_LOG_FILE = Path("uploaded_videos.log")
CLIENT_SECRETS_FILE = Path("client_secrets.json")
BASE_DIR = Path.cwd()

# --- Константы YouTube API ---
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/userinfo.profile"]
VIDEO_UPLOAD_QUOTA_COST = 1600  # Стоимость загрузки одного видео (единиц)

class VideoMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Merger and YouTube Uploader")
        self.root.geometry("800x950")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        style = ttk.Style("darkly")
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("TCombobox", font=("Helvetica", 10))
        style.configure("TCheckbutton", font=("Helvetica", 10))
        style.configure("custom.TButton", borderwidth=0, background="#2b2b2b", relief="flat")
        style.map("custom.TButton", background=[("active", "#2b2b2b")])

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.ffmpeg_path = tk.StringVar(value="ffmpeg")
        self.output_format = tk.StringVar(value="avi")
        self.delete_sources = tk.BooleanVar(value=False)
        self.move_after_upload = tk.BooleanVar(value=True)
        self.delete_after_upload = tk.BooleanVar(value=False)
        self.upload_to_youtube_enabled = tk.BooleanVar(value=True)
        self.uploaded_folder_name = tk.StringVar(value="UPLOADED_TO_YOUTUBE")
        self.video_title_prefix = tk.StringVar(value="Архив Запись ")
        self.video_description = tk.StringVar(value="Автоматически объединенная и загруженная запись.")
        self.video_tags = tk.StringVar(value="архив,автозагрузка,запись")
        self.category_id = tk.StringVar(value="22")
        self.privacy_status = tk.StringVar(value="private")

        self.youtube_service = None
        self.analytics_service = None
        self.account_name = tk.StringVar(value="Не авторизован")
        self.account_image = None
        self.progress = None
        self.doughnut_image = None
        self.qr_image = None

        self.load_settings()
        self.create_gui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.input_folder.set(settings.get("input_folder", ""))
                self.output_folder.set(settings.get("output_folder", ""))
                self.ffmpeg_path.set(settings.get("ffmpeg_path", "ffmpeg"))
                self.output_format.set(settings.get("output_format", "avi"))
                self.delete_sources.set(settings.get("delete_sources", False))
                self.move_after_upload.set(settings.get("move_after_upload", True))
                self.delete_after_upload.set(settings.get("delete_after_upload", False))
                self.upload_to_youtube_enabled.set(settings.get("upload_to_youtube_enabled", True))
                self.uploaded_folder_name.set(settings.get("uploaded_folder_name", "UPLOADED_TO_YOUTUBE"))
                self.video_title_prefix.set(settings.get("video_title_prefix", "Архив Запись "))
                self.video_description.set(settings.get("video_description", "Автоматически объединенная и загруженная запись."))
                self.video_tags.set(settings.get("video_tags", "архив,автозагрузка,запись"))
                self.category_id.set(settings.get("category_id", "22"))
                self.privacy_status.set(settings.get("privacy_status", "private"))
                log.info("Настройки успешно загружены из settings.json")
            except Exception as e:
                log.error(f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        settings = {
            "input_folder": self.input_folder.get(),
            "output_folder": self.output_folder.get(),
            "ffmpeg_path": self.ffmpeg_path.get(),
            "output_format": self.output_format.get(),
            "delete_sources": self.delete_sources.get(),
            "move_after_upload": self.move_after_upload.get(),
            "delete_after_upload": self.delete_after_upload.get(),
            "upload_to_youtube_enabled": self.upload_to_youtube_enabled.get(),
            "uploaded_folder_name": self.uploaded_folder_name.get(),
            "video_title_prefix": self.video_title_prefix.get(),
            "video_description": self.video_description.get(),
            "video_tags": self.video_tags.get(),
            "category_id": self.category_id.get(),
            "privacy_status": self.privacy_status.get()
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            log.info("Настройки успешно сохранены в settings.json")
        except Exception as e:
            log.error(f"Ошибка сохранения настроек: {e}")

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

    def open_donation_link(self):
        webbrowser.open("https://www.donationalerts.com/r/dr_klmn")

    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding="15", bootstyle="dark")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=0)

        file_frame = ttk.LabelFrame(main_frame, text="Настройки файлов", padding=10, bootstyle="primary")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Папка с исходниками:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.input_folder, bootstyle="secondary").grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(file_frame, text="Выбрать", command=self.select_input_folder, bootstyle="outline-secondary").grid(row=0, column=2, padx=5)

        ttk.Label(file_frame, text="Папка для объединенных:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_folder, bootstyle="secondary").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(file_frame, text="Выбрать", command=self.select_output_folder, bootstyle="outline-secondary").grid(row=1, column=2, padx=5)

        ttk.Label(file_frame, text="Путь к FFmpeg:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.ffmpeg_path, bootstyle="secondary").grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(file_frame, text="Выбрать", command=self.select_ffmpeg, bootstyle="outline-secondary").grid(row=2, column=2, padx=5)

        ttk.Label(file_frame, text="Формат видео:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Combobox(file_frame, textvariable=self.output_format, 
                    values=["avi", "mp4", "mkv"], state="readonly", bootstyle="secondary").grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        options_frame = ttk.LabelFrame(main_frame, text="Опции обработки", padding=10, bootstyle="primary")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        options_frame.columnconfigure(1, weight=1)

        ttk.Checkbutton(options_frame, text="Удалять исходники после объединения", 
                       variable=self.delete_sources, bootstyle="round-toggle").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Загружать в YouTube", 
                       variable=self.upload_to_youtube_enabled, bootstyle="round-toggle").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Перемещать после загрузки", 
                       variable=self.move_after_upload, bootstyle="round-toggle").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Удалять объединенные после загрузки", 
                       variable=self.delete_after_upload, bootstyle="round-toggle").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(options_frame, text="Папка для загруженных:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(options_frame, textvariable=self.uploaded_folder_name, bootstyle="secondary").grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        youtube_frame = ttk.LabelFrame(main_frame, text="Настройки YouTube", padding=10, bootstyle="primary")
        youtube_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        youtube_frame.columnconfigure(1, weight=1)

        self.avatar_label = ttk.Label(youtube_frame)
        self.avatar_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(youtube_frame, textvariable=self.account_name, font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(youtube_frame, text="Сменить аккаунт", command=self.change_account, bootstyle="info").grid(row=0, column=2, padx=5)

        ttk.Label(youtube_frame, text="Префикс заголовка:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(youtube_frame, textvariable=self.video_title_prefix, bootstyle="secondary").grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Label(youtube_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(youtube_frame, textvariable=self.video_description, bootstyle="secondary").grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Label(youtube_frame, text="Теги (через запятую):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(youtube_frame, textvariable=self.video_tags, bootstyle="secondary").grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Label(youtube_frame, text="Категория ID:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(youtube_frame, textvariable=self.category_id, bootstyle="secondary").grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Label(youtube_frame, text="Приватность:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Combobox(youtube_frame, textvariable=self.privacy_status, 
                    values=["private", "public", "unlisted"], state="readonly", bootstyle="secondary").grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding=10, bootstyle="primary")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=0)
        log_frame.rowconfigure(1, weight=1)

        self.progress = ttk.Progressbar(log_frame, maximum=100, mode='determinate', bootstyle="success")
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=7, font=("Helvetica", 10), bg="#2b2b2b", fg="#ffffff", insertbackground="white")
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Кнопка "Запустить обработку" (слева, без фона) и кнопка с Doughnut.png (справа) в одной строке
        button_frame = ttk.Frame(main_frame, bootstyle="")
        button_frame.grid(row=4, column=0, columnspan=3, pady=15, sticky=(tk.W, tk.E))

        # Кнопка "Запустить обработку" (слева)
        ttk.Button(button_frame, text="Запустить обработку", command=self.start_processing, bootstyle="success").grid(row=0, column=0, sticky=tk.SW, padx=(0, 10))

        # Кнопка с Doughnut.png (справа)
        try:
            doughnut_img = Image.open("Doughnut.png").resize((25, 25), Image.LANCZOS)
            if doughnut_img.mode != "RGBA":
                doughnut_img = doughnut_img.convert("RGBA")
            self.doughnut_image = ImageTk.PhotoImage(doughnut_img)
            doughnut_button = ttk.Button(button_frame, image=self.doughnut_image, command=self.open_donation_link, style="custom.TButton")
            doughnut_button.grid(row=0, column=1, sticky=tk.SE, padx=(10, 0))
        except Exception as e:
            log.error(f"Не удалось загрузить Doughnut.png: {e}")

        # Устанавливаем вес столбцов для равномерного распределения
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        handler = TextHandler(self.log_text, self.root)
        log.addHandler(handler)

    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def select_ffmpeg(self):
        path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if path:
            self.ffmpeg_path.set(path)

    def start_processing(self):
        if not self.input_folder.get() or not self.output_folder.get():
            ttk.messagebox.show_error("Ошибка", "Выберите папки для исходников и вывода!", parent=self.root)
            return
        Thread(target=self.main_processing, daemon=True).start()

    def download_ffmpeg_if_missing(self) -> Optional[Path]:
        """Download the latest FFmpeg from GyanD/codexffmpeg if not found."""
        local_ffmpeg = BASE_DIR / "ffmpeg.exe"
        if local_ffmpeg.exists():
            log.info("FFmpeg найден локально.")
            return local_ffmpeg

        log.info("FFmpeg не найден, пытаюсь скачать последнюю версию с GitHub (GyanD/codexffmpeg)...")
        if platform.architecture()[0] != '64bit':
            log.error("Критическая ошибка: Авто-скачивание настроено только для 64-bit Windows.")
            return None

        api_url = "https://api.github.com/repos/GyanD/codexffmpeg/releases/latest"
        headers_api = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python-FFmpeg-Downloader/4.0'}
        log.info(f"Запрос к GitHub API: {api_url}")

        try:
            response = requests.get(api_url, headers=headers_api, timeout=30)
            response.raise_for_status()
            release_data = response.json()
            tag_name = release_data.get('tag_name')
            assets = release_data.get('assets', [])
            if not tag_name or not assets:
                raise ValueError("Нет данных tag_name или assets в ответе API")

            ffmpeg_version = tag_name
            expected_filename = f"ffmpeg-{ffmpeg_version}-essentials_build.7z"
            log.info(f"Последняя версия: {ffmpeg_version}. Ожидаемый файл: {expected_filename}")

            actual_download_url = None
            for asset in assets:
                if asset.get('name') == expected_filename:
                    actual_download_url = asset.get('browser_download_url')
                    log.info(f"Найден URL: {actual_download_url}")
                    break
            if not actual_download_url:
                log.error(f"Ошибка: Ассет '{expected_filename}' не найден.")
                return None

            temp_archive_path = BASE_DIR / expected_filename
            log.info(f"Скачивание {expected_filename}...")
            response_dl = requests.get(actual_download_url, stream=True, timeout=240, headers=headers_api)
            response_dl.raise_for_status()
            total_size = int(response_dl.headers.get('content-length', 0))

            self.update_progress(0)  # Сброс прогресса перед скачиванием
            with open(temp_archive_path, 'wb') as f:
                for chunk in response_dl.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        progress = min(100, int((f.tell() / total_size) * 100))
                        self.update_progress(progress)

            log.info("Скачивание завершено.")
            self.update_progress(0)  # Сброс прогресса после скачивания
            log.info(f"Распаковка ffmpeg.exe с помощью 7z.exe...")

            top_level_dir = expected_filename.replace('.7z', '')
            ffmpeg_path_in_archive = f'{top_level_dir}/bin/ffmpeg.exe'

            if local_ffmpeg.exists():
                try:
                    local_ffmpeg.unlink()
                except OSError as e:
                    log.warning(f"Предупреждение: не удалить {local_ffmpeg.name}: {e}")

            command_7z = ['7z', 'x', str(temp_archive_path), f'-o{str(BASE_DIR)}', '-y', ffmpeg_path_in_archive]
            log.info(f" - Выполнение команды: {' '.join(command_7z)}")

            result_7z = subprocess.run(command_7z, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=120)
            if result_7z.returncode == 0:
                log.info(" - 7z.exe успешно завершен.")
                extracted_ffmpeg = BASE_DIR / ffmpeg_path_in_archive
                if extracted_ffmpeg.is_file():
                    shutil.move(str(extracted_ffmpeg), str(local_ffmpeg))
                    log.info(f" - ffmpeg.exe перемещен в корень: {local_ffmpeg}")
                    # Удаляем пустые папки
                    bin_dir = BASE_DIR / top_level_dir / "bin"
                    if bin_dir.exists() and not any(bin_dir.iterdir()):
                        shutil.rmtree(bin_dir, ignore_errors=True)
                        log.info(f" - Пустая папка {bin_dir} удалена")
                    top_dir = BASE_DIR / top_level_dir
                    if top_dir.exists() and not any(top_dir.iterdir()):
                        shutil.rmtree(top_dir, ignore_errors=True)
                        log.info(f" - Пустая папка {top_dir} удалена")
                else:
                    log.error(" - ОШИБКА: ffmpeg.exe не найден после распаковки!")
                    return None
            else:
                log.error(f" - ОШИБКА: 7z.exe завершился с кодом {result_7z.returncode}.")
                if result_7z.stderr:
                    log.error(f"   - 7z stderr:\n{result_7z.stderr}")
                return None

            try:
                time.sleep(0.5)
                temp_archive_path.unlink()
                log.info(f"Временный файл {expected_filename} удален.")
            except OSError as e:
                log.warning(f"Предупреждение: Не удалось удалить {expected_filename}: {e}")

            if local_ffmpeg.is_file():
                log.info(f"FFmpeg успешно скачан и распакован: {local_ffmpeg}")
                return local_ffmpeg
            else:
                log.error("Ошибка: Не удалось успешно извлечь ffmpeg.exe.")
                return None

        except requests.RequestException as e:
            log.error(f"Ошибка при скачивании: {e}")
            return None
        except Exception as e:
            log.error(f"Неизвестная ошибка при скачивании FFmpeg: {e}")
            return None

    def check_ffmpeg(self, ffmpeg_path: Path) -> bool:
        try:
            subprocess.run([str(ffmpeg_path), "-version"], capture_output=True, check=True)
            log.info(f"FFmpeg доступен: {ffmpeg_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            log.error(f"FFmpeg не найден или не работает: {ffmpeg_path}")
            new_ffmpeg_path = self.download_ffmpeg_if_missing()
            if new_ffmpeg_path:
                self.ffmpeg_path.set(str(new_ffmpeg_path))
                try:
                    subprocess.run([str(new_ffmpeg_path), "-version"], capture_output=True, check=True)
                    log.info(f"FFmpeg успешно установлен: {new_ffmpeg_path}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    log.error(f"Скачанный FFmpeg не работает: {new_ffmpeg_path}")
                    return False
            return False

    def get_creation_date(self, file_path: Path) -> Optional[datetime.date]:
        try:
            stat = file_path.stat()
            if platform.system() == "Windows":
                timestamp = stat.st_ctime
            else:
                timestamp = getattr(stat, 'st_birthtime', stat.st_mtime)
            return datetime.fromtimestamp(timestamp).date()
        except Exception as e:
            log.warning(f"Не удалось получить дату для {file_path}: {e}")
            return None

    def get_authenticated_service(self) -> Optional[Any]:
        creds = None
        if TOKEN_PICKLE_FILE.exists():
            try:
                with open(TOKEN_PICKLE_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                log.warning(f"Не удалось загрузить token.pickle: {e}, пересоздаю")
                creds = None

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                log.info("Токен успешно обновлен")
            except Exception as e:
                log.error(f"Не удалось обновить токен: {e}, переавторизация требуется")
                creds = None

        if not creds or not creds.valid:
            if not CLIENT_SECRETS_FILE.exists():
                log.error("Файл client_secrets.json не найден!")
                return None
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)
            log.info("Новая авторизация выполнена и сохранена")

        return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)

    def get_analytics_service(self) -> Optional[Any]:
        creds = None
        if TOKEN_PICKLE_FILE.exists():
            try:
                with open(TOKEN_PICKLE_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                log.warning(f"Не удалось загрузить token.pickle для аналитики: {e}")
                return None
        return googleapiclient.discovery.build("youtubeAnalytics", "v2", credentials=creds)

    def get_quota_info(self) -> Tuple[int, int]:
        """Fetch current quota usage and limit from YouTube Analytics API."""
        if not self.analytics_service:
            self.analytics_service = self.get_analytics_service()
            if not self.analytics_service:
                log.error("Не удалось инициализировать YouTube Analytics сервис.")
                return 0, 10000  # Default to 10,000 units if analytics fails

        today = datetime.utcnow().strftime('%Y-%m-%d')
        try:
            response = self.analytics_service.reports().query(
                ids="channel==MINE",
                startDate=today,
                endDate=today,
                metrics="quotaUsed",
                dimensions=None
            ).execute()
            rows = response.get('rows', [[0]])
            quota_used = int(rows[0][0])  # Quota used today in units
            quota_limit = 10000  # Default limit, adjust if API provides this in future
            remaining = max(0, quota_limit - quota_used)
            log.info(f"Квота YouTube: Использовано {quota_used} единиц, Осталось {remaining} единиц, Лимит {quota_limit} единиц")
            return quota_used, quota_limit
        except googleapiclient.errors.HttpError as e:
            log.error(f"Ошибка получения квоты: {e}")
            return 0, 10000  # Fallback to default

    def load_youtube_account(self):
        self.youtube_service = self.get_authenticated_service()
        if self.youtube_service:
            try:
                creds = None
                if TOKEN_PICKLE_FILE.exists():
                    with open(TOKEN_PICKLE_FILE, 'rb') as token:
                        creds = pickle.load(token)
                
                people_service = googleapiclient.discovery.build('people', 'v1', credentials=creds)
                profile = people_service.people().get(resourceName='people/me', personFields='names,photos').execute()
                self.account_name.set(profile['names'][0]['displayName'])
                
                photo_url = profile['photos'][0]['url']
                response = requests.get(photo_url)
                img_data = BytesIO(response.content)
                img = Image.open(img_data).resize((50, 50), Image.LANCZOS)
                self.account_image = ImageTk.PhotoImage(img)
                self.avatar_label.configure(image=self.account_image)
            except googleapiclient.errors.HttpError as e:
                log.error(f"Ошибка загрузки информации об аккаунте: {e}")
                self.account_name.set("Не удалось загрузить имя (проверьте scopes)")
                if "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in str(e):
                    log.warning("Недостаточно прав доступа. Удалите token.pickle и перезапустите приложение для повторной авторизации.")
            except Exception as e:
                log.error(f"Прочая ошибка загрузки информации об аккаунте: {e}")
                self.account_name.set("Не удалось загрузить имя")

    def change_account(self):
        if TOKEN_PICKLE_FILE.exists():
            TOKEN_PICKLE_FILE.unlink()
        self.load_youtube_account()

    def save_state(self, state: Dict[str, Any]):
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, default=str)
        except Exception as e:
            log.error(f"Ошибка сохранения состояния: {e}")

    def load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Ошибка загрузки состояния: {e}")
        return {'processed_dates': [], 'pending_uploads': []}

    def create_info_file(self, output_filepath: Path, source_file_paths: List[Path], youtube_url: str = None):
        info_file = output_filepath.with_suffix('.txt')
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Объединенный файл: {output_filepath.name}\n")
                f.write(f"Дата создания: {datetime.fromtimestamp(output_filepath.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Размер: {output_filepath.stat().st_size / (1024 * 1024):.2f} MB\n\n")
                f.write("Фрагменты:\n")
                for i, src_path in enumerate(source_file_paths, 1):
                    size_mb = src_path.stat().st_size / (1024 * 1024) if src_path.exists() else 0
                    ctime = datetime.fromtimestamp(src_path.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S') if src_path.exists() else "Удален"
                    f.write(f"{i}. {src_path.name}\n")
                    f.write(f"   Размер: {size_mb:.2f} MB\n")
                    f.write(f"   Дата создания: {ctime}\n\n")
                if youtube_url:
                    f.write(f"YouTube URL: {youtube_url}\n")
            log.info(f"Создан файл: {info_file}")
        except Exception as e:
            log.error(f"Ошибка создания файла {info_file}: {e}")

    def update_progress(self, value: int):
        self.root.after(0, lambda: self.progress.configure(value=value))
        self.root.after(0, lambda: self.progress.update())

    def upload_to_youtube(self, file_path: Path, date_str: str) -> Optional[str]:
        if not self.youtube_service:
            log.warning("YouTube сервис недоступен, загрузка невозможна")
            return None

        quota_used, quota_limit = self.get_quota_info()
        remaining_uploads = max(0, (quota_limit - quota_used) // VIDEO_UPLOAD_QUOTA_COST)
        if remaining_uploads <= 0:
            log.error("Достигнут лимит загрузок на сегодня. Процесс остановлен.")
            ttk.messagebox.show_error("Ошибка", "Достигнут лимит загрузок на YouTube!", parent=self.root)
            return None

        log.info(f"Начинаю загрузку файла: {file_path.name} ({file_path.stat().st_size / (1024 * 1024):.2f} MB)")
        body = {
            'snippet': {
                'title': f"{self.video_title_prefix.get()}{date_str}",
                'description': self.video_description.get(),
                'tags': self.video_tags.get().split(','),
                'categoryId': self.category_id.get()
            },
            'status': {
                'privacyStatus': self.privacy_status.get(),
                'selfDeclaredMadeForKids': False
            }
        }
        media = MediaFileUpload(str(file_path), chunksize=5*1024*1024, resumable=True, mimetype='video/*')
        request = self.youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        last_progress = -1
        try:
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress != last_progress:
                        self.update_progress(progress)
                        last_progress = progress
                        time.sleep(0.1)
            if response:
                video_id = response.get('id')
                url = f"https://www.youtube.com/watch?v={video_id}"
                stats["uploaded_videos"] += 1
                log.info(f"Видео успешно загружено: {url}")
                return url
            else:
                log.error(f"Не удалось загрузить видео: {file_path.name}")
                return None
        except googleapiclient.errors.HttpError as e:
            if "uploadLimitExceeded" in str(e):
                log.error(f"Ошибка при загрузке видео {file_path.name}: Превышен лимит загрузок.")
                ttk.messagebox.show_error("Ошибка", "Превышен лимит загрузок на YouTube!", parent=self.root)
            else:
                log.error(f"Ошибка при загрузке видео {file_path.name}: {e}")
            return None
        finally:
            self.update_progress(0)

    def process_upload(self, file_path: Path, date_str: str, source_paths: List[Path], uploaded_files_log: Set[str], output_folder: Path) -> bool:
        output_filename = file_path.name
        if output_filename in uploaded_files_log:
            log.info(f"Файл {output_filename} уже загружен на YouTube, пропускаю")
            return True

        if not file_path.exists():
            log.warning(f"Файл {file_path} не найден, пропускаю загрузку")
            return True

        log.info(f"Обнаружен файл для загрузки: {file_path.name}")
        youtube_url = self.upload_to_youtube(file_path, date_str)
        if youtube_url:
            self.create_info_file(file_path, source_paths, youtube_url)
            add_to_uploaded_log(output_filename)
            uploaded_files_log.add(output_filename)
            if self.move_after_upload.get():
                dest = output_folder / self.uploaded_folder_name.get() / output_filename
                dest.parent.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(dest))
                stats["moved_videos"] += 1
                log.info(f"Файл перемещен в {dest}")
            elif self.delete_after_upload.get():
                try:
                    file_path.unlink()
                    log.info(f"Объединенный файл удален: {file_path}")
                    stats["deleted_merged"] += 1
                except OSError as e:
                    log.error(f"Ошибка удаления {file_path}: {e}")
                    stats["failed_deletions"] += 1
            return True
        else:
            log.warning(f"Загрузка {file_path.name} не удалась, добавляю в очередь для следующего запуска")
            return False

    def main_processing(self):
        global stats
        input_folder = Path(self.input_folder.get())
        output_folder = Path(self.output_folder.get())
        ffmpeg_path = Path(self.ffmpeg_path.get())

        if not self.check_ffmpeg(ffmpeg_path):
            ttk.messagebox.show_error("Ошибка", "FFmpeg недоступен!", parent=self.root)
            return

        if not input_folder.exists() or not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)

        state = self.load_state()
        processed_dates = set(state.get('processed_dates', []))
        pending_uploads = state.get('pending_uploads', [])
        uploaded_files_log = load_uploaded_log()

        if self.upload_to_youtube_enabled.get():
            quota_used, quota_limit = self.get_quota_info()
            remaining_uploads = max(0, (quota_limit - quota_used) // VIDEO_UPLOAD_QUOTA_COST)
            log.info("=" * 50)
            log.info(f"Лимит загрузки YouTube: Использовано {quota_used} единиц, Осталось {remaining_uploads} загрузок, Лимит {quota_limit} единиц")
            log.info("=" * 50)
            if remaining_uploads <= 0:
                log.error("Достигнут лимит загрузок. Процесс остановлен.")
                ttk.messagebox.show_error("Ошибка", "Достигнут лимит загрузок на YouTube!", parent=self.root)
                return

        files_by_date: Dict[datetime.date, List[Tuple[float, Path]]] = defaultdict(list)
        for item in input_folder.iterdir():
            if item.is_file() and item.suffix.lower() == f".{self.output_format.get()}":
                date = self.get_creation_date(item)
                if date:
                    files_by_date[date].append((item.stat().st_mtime, item))

        for date in sorted(files_by_date.keys()):
            if str(date) in processed_dates:
                log.info(f"Дата {date} уже обработана, пропускаю объединение")
                continue
            date_str = date.strftime('%Y-%m-%d')
            output_filename = f"{date_str}_merged.{self.output_format.get()}"
            output_filepath = output_folder / output_filename
            list_file = output_folder / f"{date_str}_files.txt"

            sorted_files = sorted(files_by_date[date], key=lambda x: x[0])
            source_paths = [f[1] for f in sorted_files]
            log.info(f"Обрабатываю видео для даты {date_str}: {len(source_paths)} файлов")
            for src_path in source_paths:
                log.info(f" - {src_path.name} ({src_path.stat().st_size / (1024 * 1024):.2f} MB)")

            if len(source_paths) == 1:
                log.info(f"Только один фрагмент для даты {date_str}, добавляю для загрузки без объединения")
                pending_uploads.append({
                    'file_path': str(source_paths[0]),
                    'date_str': date_str,
                    'source_paths': [str(source_paths[0])]
                })
            else:
                log.info(f"Объединяю видео для даты {date_str}: {len(source_paths)} файлов")
                if not output_filepath.exists():
                    with open(list_file, 'w', encoding='utf-8') as f:
                        for path in source_paths:
                            normalized_path = os.path.normpath(str(path)).replace('\\', '/')
                            f.write(f"file '{normalized_path}'\n")
                    cmd = [str(ffmpeg_path), "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output_filepath)]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        stats["merged_days"] += 1
                        log.info(f"Видео успешно объединено: {output_filepath.name} ({output_filepath.stat().st_size / (1024 * 1024):.2f} MB)")
                        self.create_info_file(output_filepath, source_paths)
                        pending_uploads.append({
                            'file_path': str(output_filepath),
                            'date_str': date_str,
                            'source_paths': [str(p) for p in source_paths]
                        })
                    except subprocess.CalledProcessError as e:
                        log.error(f"Ошибка FFmpeg: {e.stderr.decode()}")
                        stats["merge_errors"] += 1
                        continue
                    finally:
                        list_file.unlink(missing_ok=True)

                if self.delete_sources.get():
                    for path in source_paths:
                        try:
                            path.unlink()
                            stats["deleted_sources"] += 1
                            log.info(f"Исходный файл удален: {path.name}")
                        except OSError:
                            stats["failed_deletions"] += 1
                            log.error(f"Не удалось удалить исходный файл {path.name}")

            processed_dates.add(str(date))
            self.save_state({'processed_dates': list(processed_dates), 'pending_uploads': pending_uploads})

        if self.upload_to_youtube_enabled.get():
            if not self.youtube_service:
                self.youtube_service = self.get_authenticated_service()
                if not self.youtube_service:
                    log.error("Не удалось инициализировать YouTube сервис. Загрузка отменена.")
                    return
                self.load_youtube_account()

            log.info("Проверяю незавершенные загрузки...")
            new_pending_uploads = []
            for upload_task in pending_uploads:
                file_path = Path(upload_task['file_path'])
                date_str = upload_task['date_str']
                source_paths = [Path(p) for p in upload_task['source_paths']]
                if not self.process_upload(file_path, date_str, source_paths, uploaded_files_log, output_folder):
                    new_pending_uploads.append(upload_task)

            log.info("Проверяю выходную папку на наличие незагруженных объединенных файлов...")
            for item in output_folder.iterdir():
                if item.is_file() and item.suffix.lower() == f".{self.output_format.get()}":
                    output_filename = item.name
                    if output_filename in uploaded_files_log:
                        continue
                    date_str = output_filename.split('_merged')[0] if '_merged' in output_filename else item.stem
                    source_paths = [item]
                    upload_task = {
                        'file_path': str(item),
                        'date_str': date_str,
                        'source_paths': [str(item)]
                    }
                    if not self.process_upload(item, date_str, source_paths, uploaded_files_log, output_folder):
                        new_pending_uploads.append(upload_task)

            self.save_state({'processed_dates': list(processed_dates), 'pending_uploads': new_pending_uploads})

            if stats['uploaded_videos'] == 0:
                log.info("Загружено более 3 файлов! Показываю QR-код...")
                try:
                    qr_url = "https://static.donationalerts.ru/uploads/qr/13684443/qr_a76ad0f6472716d3e8895e4d1227c527.png"
                    response = requests.get(qr_url)
                    response.raise_for_status()
                    qr_img = Image.open(BytesIO(response.content)).resize((150, 150), Image.LANCZOS)
                    self.qr_image = ImageTk.PhotoImage(qr_img)
                    self.log_text.image_create(tk.END, image=self.qr_image)
                    self.log_text.insert(tk.END, "\n")
                    self.log_text.see(tk.END)
                except Exception as e:
                    log.error(f"Не удалось загрузить QR-код: {e}")

        else:
            log.info("Загрузка на YouTube отключена. Пропускаю шаги загрузки.")
            self.save_state({'processed_dates': list(processed_dates), 'pending_uploads': pending_uploads})

        log.info(f"Итог: Обработано дней: {stats['merged_days']}, Загружено видео: {stats['uploaded_videos']}, "
                 f"Удалено исходников: {stats['deleted_sources']}, Удалено объединенных: {stats['deleted_merged']}, "
                 f"Перемещено видео: {stats['moved_videos']}, Ошибок объединения: {stats['merge_errors']}, "
                 f"Ошибок удаления: {stats['failed_deletions']}")

        log.info("=" * 50)
        log.info(f"ЗАГРУЖЕНО ВИДЕО: {stats['uploaded_videos']} !!!")
        log.info("=" * 50)

def load_uploaded_log() -> Set[str]:
    uploaded = set()
    if UPLOADED_LOG_FILE.exists():
        with open(UPLOADED_LOG_FILE, 'r', encoding='utf-8') as f:
            uploaded.update(line.strip() for line in f if line.strip())
    return uploaded

def add_to_uploaded_log(filename: str):
    with open(UPLOADED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')

class TextHandler(logging.Handler):
    def __init__(self, text_widget, root):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        self.root = root

    def emit(self, record):
        msg = self.format(record)
        if "ЗАГРУЖЕНО ВИДЕО" in msg:
            self.text_widget.tag_configure("large", font=("Helvetica", 14, "bold"))
            self.text_widget.insert(tk.END, msg + '\n', "large")
        else:
            self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = VideoMergerApp(root)
    root.mainloop()
