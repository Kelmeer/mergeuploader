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
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import requests
from io import BytesIO
from PIL import Image, ImageTk

try:
    from tqdm import tqdm
except ImportError:
    print("Ошибка: Библиотека 'tqdm' не найдена.")
    print("Пожалуйста, установите ее: pip install tqdm")
    sys.exit(1)

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
TOKEN_PICKLE_FILE = Path("token.pickle")
UPLOADED_LOG_FILE = Path("uploaded_videos.log")
CLIENT_SECRETS_FILE = Path("client_secrets.json")

# --- Константы YouTube API ---
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/userinfo.profile"]

class VideoMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Merger and YouTube Uploader")
        self.root.geometry("800x900")

        # Переменные настроек
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.ffmpeg_path = tk.StringVar(value="ffmpeg")
        self.output_format = tk.StringVar(value="avi")
        self.delete_sources = tk.BooleanVar(value=False)
        self.move_after_upload = tk.BooleanVar(value=True)
        self.delete_after_upload = tk.BooleanVar(value=False)
        self.uploaded_folder_name = tk.StringVar(value="UPLOADED_TO_YOUTUBE")
        self.video_title_prefix = tk.StringVar(value="Архив Запись ")
        self.video_description = tk.StringVar(value="Автоматически объединенная и загруженная запись.")
        self.video_tags = tk.StringVar(value="архив,автозагрузка,запись")
        self.category_id = tk.StringVar(value="22")
        self.privacy_status = tk.StringVar(value="private")

        self.youtube_service = None
        self.account_name = tk.StringVar()
        self.account_image = None

        self.create_gui()
        self.load_youtube_account()

    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Папка с исходниками:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=150).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Выбрать", command=self.select_input_folder).grid(row=0, column=2)

        ttk.Label(main_frame, text="Папка для объединенных:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=150).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Выбрать", command=self.select_output_folder).grid(row=1, column=2)

        ttk.Label(main_frame, text="Путь к FFmpeg:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.ffmpeg_path, width=150).grid(row=2, column=1, padx=5)
        ttk.Button(main_frame, text="Выбрать", command=self.select_ffmpeg).grid(row=2, column=2)

        ttk.Label(main_frame, text="Формат видео:").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(main_frame, textvariable=self.output_format, 
                    values=["avi", "mp4", "mkv"], state="readonly").grid(row=3, column=1, sticky=tk.W)

        ttk.Checkbutton(main_frame, text="Удалять исходники после объединения", 
                       variable=self.delete_sources).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="Перемещать после загрузки", 
                       variable=self.move_after_upload).grid(row=5, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="Удалять объединенные после загрузки", 
                       variable=self.delete_after_upload).grid(row=6, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(main_frame, text="Папка для загруженных:").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.uploaded_folder_name, width=150).grid(row=7, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Настройки YouTube", font=("Arial", 12, "bold")).grid(row=8, column=0, columnspan=3, pady=10)
        
        self.avatar_label = ttk.Label(main_frame)
        self.avatar_label.grid(row=9, column=0, sticky=tk.W)
        ttk.Label(main_frame, textvariable=self.account_name).grid(row=9, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="Сменить аккаунт", command=self.change_account).grid(row=9, column=2)

        ttk.Label(main_frame, text="Префикс заголовка:").grid(row=10, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.video_title_prefix, width=150).grid(row=10, column=1, sticky=tk.W)
        ttk.Label(main_frame, text="Описание:").grid(row=11, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.video_description, width=150).grid(row=11, column=1, sticky=tk.W)
        ttk.Label(main_frame, text="Теги (через запятую):").grid(row=12, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.video_tags, width=150).grid(row=12, column=1, sticky=tk.W)
        ttk.Label(main_frame, text="Категория ID:").grid(row=13, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.category_id, width=150).grid(row=13, column=1, sticky=tk.W)
        ttk.Label(main_frame, text="Приватность:").grid(row=14, column=0, sticky=tk.W)
        ttk.Combobox(main_frame, textvariable=self.privacy_status, 
                    values=["private", "public", "unlisted"], state="readonly").grid(row=14, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Лог выполнения:").grid(row=15, column=0, columnspan=3, pady=5)
        self.log_text = tk.Text(main_frame, height=15, width=100)
        self.log_text.grid(row=16, column=0, columnspan=3, pady=5)

        ttk.Button(main_frame, text="Запустить обработку", command=self.start_processing).grid(row=17, column=0, columnspan=3, pady=10)

        handler = TextHandler(self.log_text)
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
            messagebox.showerror("Ошибка", "Выберите папки для исходников и вывода!")
            return
        Thread(target=self.main_processing, daemon=True).start()

    def check_ffmpeg(self, ffmpeg_path: Path) -> bool:
        try:
            subprocess.run([str(ffmpeg_path), "-version"], capture_output=True, check=True)
            log.info(f"FFmpeg доступен: {ffmpeg_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            log.error(f"FFmpeg не найден или не работает: {ffmpeg_path}")
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
            with open(TOKEN_PICKLE_FILE, 'rb') as token:
                creds = pickle.load(token)
        if creds and not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)
        if not creds or not creds.valid:
            if not CLIENT_SECRETS_FILE.exists():
                log.error("Файл client_secrets.json не найден!")
                return None
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)
        return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)

    def load_youtube_account(self):
        self.youtube_service = self.get_authenticated_service()
        if self.youtube_service:
            try:
                # Получаем информацию о профиле через Google People API
                creds = None
                if TOKEN_PICKLE_FILE.exists():
                    with open(TOKEN_PICKLE_FILE, 'rb') as token:
                        creds = pickle.load(token)
                
                people_service = googleapiclient.discovery.build('people', 'v1', credentials=creds)
                profile = people_service.people().get(resourceName='people/me', personFields='names,photos').execute()
                self.account_name.set(profile['names'][0]['displayName'])
                
                # Загружаем аватар
                photo_url = profile['photos'][0]['url']
                response = requests.get(photo_url)
                img_data = BytesIO(response.content)
                img = Image.open(img_data).resize((50, 50), Image.LANCZOS)
                self.account_image = ImageTk.PhotoImage(img)
                self.avatar_label.configure(image=self.account_image)
            except Exception as e:
                log.error(f"Ошибка загрузки информации об аккаунте: {e}")
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
        return {'processed_dates': []}

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

    def upload_to_youtube(self, file_path: Path, date_str: str) -> Optional[str]:
        if not self.youtube_service:
            return None
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
        with tqdm(total=100, unit='%') as pbar:
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pbar.update(int(status.progress() * 100) - pbar.n)
        if response:
            video_id = response.get('id')
            url = f"https://www.youtube.com/watch?v={video_id}"
            stats["uploaded_videos"] += 1
            return url
        return None

    def main_processing(self):
        global stats
        input_folder = Path(self.input_folder.get())
        output_folder = Path(self.output_folder.get())
        ffmpeg_path = Path(self.ffmpeg_path.get())

        if not self.check_ffmpeg(ffmpeg_path):
            messagebox.showerror("Ошибка", "FFmpeg недоступен!")
            return

        if not input_folder.exists() or not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)

        self.youtube_service = self.get_authenticated_service()
        state = self.load_state()
        processed_dates = set(state.get('processed_dates', []))
        uploaded_files_log = load_uploaded_log()

        files_by_date: Dict[datetime.date, List[Tuple[float, Path]]] = defaultdict(list)
        for item in input_folder.iterdir():
            if item.is_file() and item.suffix.lower() == f".{self.output_format.get()}":
                date = self.get_creation_date(item)
                if date:
                    files_by_date[date].append((item.stat().st_mtime, item))

        for date in sorted(files_by_date.keys()):
            if str(date) in processed_dates:
                continue
            date_str = date.strftime('%Y-%m-%d')
            output_filename = f"{date_str}_merged.{self.output_format.get()}"
            output_filepath = output_folder / output_filename
            list_file = output_folder / f"{date_str}_files.txt"

            if len(files_by_date[date]) <= 1 or output_filename in uploaded_files_log:
                continue

            sorted_files = sorted(files_by_date[date], key=lambda x: x[0])
            source_paths = [f[1] for f in sorted_files]

            if not output_filepath.exists():
                with open(list_file, 'w', encoding='utf-8') as f:
                    for path in source_paths:
                        normalized_path = os.path.normpath(str(path)).replace('\\', '/')
                        f.write(f"file '{normalized_path}'\n")
                cmd = [str(ffmpeg_path), "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output_filepath)]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    stats["merged_days"] += 1
                    self.create_info_file(output_filepath, source_paths)
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
                    except OSError:
                        stats["failed_deletions"] += 1

            if self.youtube_service and output_filename not in uploaded_files_log:
                youtube_url = self.upload_to_youtube(output_filepath, date_str)
                if youtube_url:
                    self.create_info_file(output_filepath, source_paths, youtube_url)
                    add_to_uploaded_log(output_filename)
                    uploaded_files_log.add(output_filename)
                    if self.move_after_upload.get():
                        dest = output_folder / self.uploaded_folder_name.get() / output_filename
                        dest.parent.mkdir(exist_ok=True)
                        shutil.move(str(output_filepath), str(dest))
                        stats["moved_videos"] += 1
                    elif self.delete_after_upload.get():
                        try:
                            output_filepath.unlink()
                            log.info(f"Удален объединенный файл: {output_filepath}")
                            stats["deleted_merged"] += 1
                        except OSError as e:
                            log.error(f"Ошибка удаления {output_filepath}: {e}")
                            stats["failed_deletions"] += 1

            processed_dates.add(str(date))
            self.save_state({'processed_dates': list(processed_dates)})

        log.info(f"Обработано дней: {stats['merged_days']}, Загружено: {stats['uploaded_videos']}, Удалено объединенных: {stats['deleted_merged']}")

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
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoMergerApp(root)
    root.mainloop()
