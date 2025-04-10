import os
import subprocess
import platform
import sys
import pickle
import time
import shutil
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import math
import zipfile
import requests
import json # Для парсинга вывода ffprobe

# Библиотеки для GUI и YouTube
try:
    from tqdm import tqdm # Для прогресс-баров
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Простая заглушка для tqdm, если библиотека не установлена
    def tqdm(iterable=None, **kwargs):
        if iterable is None:
            # Возвращаем объект с методами update/close, чтобы не было ошибок
            class SimpleProgress:
                n = 0
                total = kwargs.get('total', None)
                def update(self, n=1): self.n += n
                def close(self): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
            print(f"Прогресс ({kwargs.get('desc', '')}): ", end='')
            return SimpleProgress()
        else:
            # Просто возвращаем итератор
            print(f"Обработка ({kwargs.get('desc', '')})...")
            return iterable
    print("Предупреждение: Библиотека 'tqdm' не найдена. Прогресс-бары будут упрощены.")
    print("Установите: pip install tqdm")

try:
    import google_auth_oauthlib.flow
    import google.auth.transport.requests
    import googleapiclient.discovery
    import googleapiclient.errors
    from googleapiclient.http import MediaFileUpload
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    print("Предупреждение: Библиотеки Google API не найдены. Загрузка на YouTube будет недоступна.")

# --- Определение базовой директории ---
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent
print(f"Рабочая директория скрипта: {BASE_DIR}")

# --- НАСТРОЙКИ ---
INPUT_FOLDER = BASE_DIR
OUTPUT_FOLDER_NAME = "merged_videos"
OUTPUT_FOLDER = BASE_DIR / OUTPUT_FOLDER_NAME
# OUTPUT_FORMAT определяется автоматическиall_local = False

    if found_all_local:
        print("Все необходимые инструменты FFmpeg найдены локально.")
        return local_ffmpeg_path, local_ffprobe_path
    else:
        print("Не все инструменты найдены. Попытка скачивания с GitHub...")
        # ... (логика скачивания и распаковки, как в предыдущем ответе,
        #      но извлекаем ОБА файла: ffmpeg.exe и ffprobe.exe) ...

        is_64bit = platform.architecture()[0] == '64bit'
        arch_suffix = "win64" if is_64bit else "win32"
        ffmpeg_version = "6.0" # Используем конкретную версию
        zip_filename = f"ffmpeg-{ffmpeg_version}-essentials_build-{arch_suffix}.zip"
        download_url = f"https://github.com/ShareX/FFmpeg/releases/download/v{ffmpeg_version}/{zip_filename}"
        temp_zip_path = из первого найденного файла
DELETE_SOURCES_AFTER_MERGE = True # Удалять исходные .avi/.mp4/... файлы
DELETE_MERGED_AFTER_UPLOAD = True # Удалять объединенный файл после загрузки и создания .txt
CREATE_FRAGMENT_LIST_FILE = True # Создавать .txt со списком фрагментов

# Настройки YouTube API
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_PICKLE_FILE = BASE_DIR / "token.pickle"
UPLOADED_LOG_FILE = BASE_DIR / "uploaded_videos.log"
MOVE_UPLOADED_TXT_TO = "UPLOADED_INFO" # Имя подпапки для .txt файлов успешно загруженных видео

# Настройки видео YouTube
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
DEFAULT_ BASE_DIR / zip_filename

        print(f"URL для скачивания ({'64-bit' if is_64bit else '32-bit'}): {download_VIDEO_TITLE_PREFIX = "Архив Запись "
DEFAULT_VIDEO_DESCRIPTION = "Автоматически объединенная и загруженная запись."
DEFAULT_TAGS = ["архив", "автозагрузкаurl}")

        try:
            print(f"Скачивание {", "запись"]
DEFAULT_CATEGORY_ID = "22"zip_filename}...")
            response = requests.get(download_url, stream
DEFAULT_PRIVACY_STATUS = "private"
# --- КОНЕЦ НАСТРОЕК ---

# Глобальные переменные
stats = {
    "merged_=True, timeout=120) # Увеличен таймаут
            response.raise_days": 0, "skipped_days_single": 0, "skipped_days_exists": 0,
    "deleted_sources":for_status()
            total_size = int(response.headers.get('content-length',  0, "failed_deletions": 0, "uploaded_videos": 0,
    0))

            # Используем tqdm для прогресс-бара скачивания
"failed_uploads": 0, "txt_created": 0, "failed            with tqdm(total=total_size, unit='B', unit_scale=True_txt": 0,
    "deleted_merged": 0, "failed_merged, unit_divisor=1024,
                      desc=zip_filename,_deletion": 0, "merge_errors": 0,
    "metadata ascii=' >=') as pbar:
                 with open(temp_zip_path,_errors": 0
}
ffmpeg_path = None
ffprobe_path = None
 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8detected_input_format = None # Будет определен как ".avi",192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            if total ".mp4" и т.д.

# === ВСПОМОГАТЕЛЬНЫЕ Ф_size != 0 and pbar.n != total_size:
                 print("\nПредупреждение: Размер скачанного файла не совпадает с ожидаемымУНКЦИИ ===

def find_or_download_ffmpeg_tools():
    """
.")

            print(f"\nРаспаковка {ffmpeg_exe_name} и {ffprobe_exe_name} из архива...")
            extracted_ffmpeg = False    Ищет ffmpeg.exe и ffprobe.exe в BASE_DIR. Если не находит,
            extracted_ffprobe = False
            with zipfile.ZipFile(
    скачивает с GitHub (ShareX/FFmpeg) и извлекает оба файла.
    Возвращает кортеж (путь_temp_zip_path, 'r') as zip_ref:
                к_ffmpeg, путь_к_ffprobe) или (None, None).
    """
    global ffmpeg_path, ffprobe_path
    ffmpeg_exefor member in zip_ref.namelist():
                    member_lower = member.lower().replace('\\',_name = "ffmpeg.exe"
    ffprobe_exe_name '/')
                    # Извлекаем ffmpeg.exe
                    if member_ = "ffprobe.exe"
    local_ffmpeg = BASE_DIR / ffmpeg_exe_name
    local_ffprobe = BASE_DIR / ffprobe_lower.endswith('/bin/ffmpeg.exe'):
                        with zip_ref.open(member) as source, open(local_ffmpeg_path, 'wb') asexe_name

    print(f"\nПоиск {ffmpeg_exe target:
                            shutil.copyfileobj(source, target)
                        _name} и {ffprobe_exe_name}...")
    ifprint(f" - {ffmpeg_exe_name} извлечен.")
                        extracted_ffmpeg local_ffmpeg.is_file() and local_ffprobe.is_file():
        print(f"Найдены локальные: {local_ffmpeg} и {local_ffprobe}")
        ffmpeg_path = local_ffmpeg
        ffprobe_path = local_ = True
                    # Извлекаем ffprobe.exe
                    elif member_lower.endswith('/ffprobe
        return ffmpeg_path, ffprobe_path
    else:
        missing = []
        if not local_ffmpeg.is_file(): missing.append(bin/ffprobe.exe'):
                        with zip_ref.open(ffmpeg_exe_name)
        if not local_ffprobe.is_file(): missing.append(member) as source, open(local_ffprobe_path, 'wbffprobe_exe_name)
        print(f"Не найден(') as target:
                            shutil.copyfileobj(source, target)ы) в папке программы ({BASE_DIR}): {', '.join(missing)}")

                        print(f" - {ffprobe_exe_name} извлечен.")
                        extracted_ffprobe = True
                    # Прерываем цикл        print("Попытка скачивания с GitHub (ShareX/FFmpeg)..., если оба файла найдены
                    if extracted_ffmpeg and extracted_ffprobe:
                        break")

        is_64bit = platform.architecture()[0] == '64bit

            # Удаляем временный zip
            try:
                temp_zip_path.unlink()
'
        arch_suffix = "win64" if is_64bit else "                print(f"Временный файл {zip_filename} удален.")
            except OSError aswin32"
        ffmpeg_version = "6.0"
        zip_filename = f"ffmpeg-{ffmpeg_version}-essentials_ e:
                print(f"Предупреждение: Не удалось удалитьbuild-{arch_suffix}.zip"
        download_url = f" временный файл {zip_filename}: {e}")

            # Проверяhttps://github.com/ShareX/FFmpeg/releases/download/ем результат
            if extracted_ffmpeg and extracted_ffprobe:
                v{ffmpeg_version}/{zip_filename}"
        temp_zip_print("Инструменты FFmpeg успешно скачаны и извлечены.")
                return localpath = BASE_DIR / zip_filename

        print(f"URL для скачивания ({'_ffmpeg_path, local_ffprobe_path
            else:
64-bit' if is_64bit else '32-                print("Ошибка: Не удалось извлечь один или оба инструмента из архива.")
                # Удаляем частично извлеченные файлы, если они есть
                if local_ffmpeg_path.exists() and not extracted_ffmpeg: local_ffmpeg_path.unlink()
                if local_ffprobe_path.exists() and not extracted_ffprobe: local_ffprobe_path.unlink()
                return None, None

        except requests.exceptions.RequestException as e:bit'}): {download_url}")

        try:
            print(f"Ска
            print(f"\nОшибка скачивания FFmpeg: {e}")
            if temp_zip_path.exists(): temp_zip_path.unlink()чивание {zip_filename}...")
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_
            return None, None
        except zipfile.BadZipFile:
            print("\for_status()
            total_size = int(response.headers.get('content-length', nОшибка: Скачанный файл не является корректным ZIP-архивом.")0))

            # Используем tqdm для прогресса скачивания, если доступ
            if temp_zip_path.exists(): print(f"Фен
            progress_desc = f"Скачивание {zip_filename}"
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=progress_desc,айл сохранен для диагностики: {temp_zip_path}")
            else disable=not TQDM_AVAILABLE) as pbar, \
                 open(temp_zip_path, 'wb') as f:
                : print("Файл не сохранен.")
            return None, None
        except Exception as e:
for chunk in response.iter_content(chunk_size=8192):
                    if chunk            print(f"\nНеожиданная ошибка при получении FFmpeg: {e}")
            if:
                        f.write(chunk)
                        pbar.update( temp_zip_path.exists(): temp_zip_path.unlink()len(chunk))

            print("\nСкачивание завершено.")
            print
            return None, None

def get_video_creation_date((f"Распаковка {ffmpeg_exe_name} и {ffprobe_exe_name} из архива...")

            extracted_ffmpeg = False
            extracted_ffprobe = Falsefile_path, ffprobe_path_str):
    """
    Извлекает дату создания видео с помощью ffprobe.
    Ищет тег 'creation_time' в 'format' -> 'tags'.
    Возвращает
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for member in zip_ref. объект datetime.date или None.
    """
    global stats
    commandnamelist():
                    member_lower = member.lower().replace('\\', = [
        ffprobe_path_str,
        '-v', 'quiet '/')
                    # Ищем файлы в подпапке bin
                    if member_lower.endswith(',             # Тихий режим
        '-print_format', 'json',  # Выf'/bin/{ffmpeg_exe_name.lower()}'):
                        with zipвод в JSON
        '-show_format',            # Показать информацию о формате/контейнере
        str(file_path.resolve())   _ref.open(member) as source, open(local_ffmpeg, 'wb') as target# Путь к файлу
    ]
    try:
        result:
                            shutil.copyfileobj(source, target)
                        print(f"- {ffmpeg_exe_name} извлечен.")
                        extracted_ffmpeg = subprocess.run(command, capture_output=True, text=True = True
                    elif member_lower.endswith(f'/bin/{ff, check=True, encoding='utf-8', errors='ignore')
        metadata = json.loads(result.stdout)

        # Ищем датуprobe_exe_name.lower()}'):
                         with zip_ref.open(member в format -> tags -> creation_time
        creation_time_str = metadata.get('format', {}).get('tags', {}).get('creation_time')

        if creation_time_) as source, open(local_ffprobe, 'wb') as target:
                            shutil.copyfileobj(source, target)
                         print(f"- {ffprobe_str:
            # Формат даты часто ISO 8601 (YYYY-MM-DDTHH:MM:SS.ffffffZ)
            # Отexe_name} извлечен.")
                         extracted_ffprobe = True
                    # Прерываем если оба найдены
                    if extracted_ffmpeg and extracted_ffprobe:
                        break

            if extracted_ffmpeg and extracted_ffprobe:
                секаем время и часовой пояс, если они есть
            date_part = creation_time_strffmpeg_path = local_ffmpeg
                ffprobe_path = local_ffprobe
                print(f"Успешно извлечены в {BASE_DIR}")
                try: temp_zip_path.unlink(); print(f"В.split('T')[0]
            # Пытаемся распарсить какременный файл {zip_filename} удален.")
                except OSError as YYYY-MM-DD
            return datetime.strptime(date_part, '%Y-%m-%d').date()
        else:
            # print e: print(f"Предупреждение: Не удалось удалить {zip_filename}: {e}")
(f"Предупреждение: Тег 'creation_time' не найден                return ffmpeg_path, ffprobe_path
            else:
                missing_in_zip = []
                if not extracted_ffmpeg: missing_in_ для {file_path.name}")
            stats["metadata_errors"] += 1zip.append(ffmpeg_exe_name)
                if not extracted_ffprobe: missing_in_zip.append(ffprobe_exe_
            return None # Явно возвращаем None, если тега нет

    except subprocessname)
                print(f"Ошибка: Не удалось найти {', '.join(missing_in_zip)} внутри архива.")
                print(f"Архив сохранен как:.CalledProcessError as e:
        print(f"Ошибка ffprobe для файла {file_path.name}: {e.stderr}")
        stats {temp_zip_path}")
                return None, None

        except requests["metadata_errors"] += 1
        return None
    except json.exceptions.RequestException as e: print(f"\nОшибка скачивания: {e}")
.JSONDecodeError:
        print(f"Ошибка: Не удалось рас        except zipfile.BadZipFile: print(f"\nОшибка: Скачанный файл не ZIP-архив ({temp_zip_path})")
        except Exceptionпарсить JSON вывод ffprobe для {file_path.name}")
        stats["metadata_ as e: print(f"\nНеожиданная ошибка при получении FFerrors"] += 1
        return None
    except ValueError:
        print(f"Ошибка: Неверный формат даты ('{creation_time_str}') в метаданных {file_path.name}")
        stats["metadata_errors"] += 1
        return Nonempeg: {e}")

        # Очистка в случае ошибки
        if temp_zip_path.
    except Exception as e:
        print(f"Неожиданexists():
             try: temp_zip_path.unlink()
             except OSError:ная ошибка при получении даты из метаданных {file_path.name pass
        return None, None

def get_video_creation_date_from_metadata}: {e}")
        stats["metadata_errors"] += 1
(file_path):
    """Пытается извлечь дату создания        return None

def get_human_readable_size(size_bytes из метаданных видео с помощью ffprobe."""
    global stats
    if not ff):
    # ... (без изменений) ...
    if size_bytesprobe_path or not ffprobe_path.is_file():
        print("Предупреждение: ffprobe не найден, не могу извлечь дату из метаданных.")
        return None # Не можем работать без ffprobe

    command = [
 == 0: return "0 B"
    size_name = ("B", "KB",        str(ffprobe_path),
        "-v", "quiet", "MB", "GB", "TB")
    i = int(math. # Тихий режим
        "-print_format", "json", # Выfloor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
    p = math.pow(1вод в JSON
        "-show_format", # Показать информацию о контейнере
        "-show024, i)
    s = round(size_bytes /_streams", # Показать информацию о потоках (на всякий случай)
        str( p, 2) if p > 0 else 0
    return f"{s} {size_file_path)
    ]

    try:
        result = subprocess.run(command, capturename[i]}"

def scan_and_confirm(input_dir, ffprobe_path):
    """Сканирует папку, использует ffprobe для даты, собирает статистику и запрашивает подтверждение."""
    print(f"\nСка_output=True, text=True, check=True, encoding='utf-8нирование '{input_dir}' и извлечение дат создания видео...")
    #', errors='ignore')
        metadata = json.loads(result.stdout Используем tqdm для сканирования
    file_list = list(input_dir.iter)

        date_str = None
        # Ищем в тегах формата (наиболее вероятно)
        if 'format' in metadata and 'tags'dir()) # Получаем список файлов один раз
    files_by_date in metadata['format']:
            tags = metadata['format']['tags']
            # При = defaultdict(lambda: {'files': [], 'ext': None}) # Словарь для группировки
    total_fragments_found = 0
    fragmentsоритет тегов: creation_time, date, DateTimeOriginal (EX_to_process_count = 0
    total_size_bytesIF), CreateDate (EXIF)
            for tag_key in ['creation_time', ' = 0
    source_extensions = set() # Сохраняем уникальные расширения

    with tqdm(total=len(file_list), desc="Скаdate', 'DateTimeOriginal', 'CreateDate']:
                if tag_key in tags:
                    date_str = tags[tag_key]
                    break

нирование", unit="файл", ascii=" >=") as pbar:
        for item        # Если не нашли в формате, попробуем в первом видео потоке (менее вероятно)
        if not date_str and 'streams' in metadata:
             for stream in metadata['streams']:
                 if stream.get('codec_type') == 'video' and 'tags' in stream:
                     tags = stream['tags']
                     for tag_key in ['creation_time', 'date']: # Реже EXIF в потоках
                        if tag_key in tags:
                            date_str = tags[tag_key]
                            break
                 if date_str: break # Нашли в потоке, выходим

        if date_str:
            try:
                # Пытаемся распарсить разные форматы
                # ISO 8601 с 'T' и опциональной 'Z'/'смещением'
                if 'T in file_list:
            pbar.update(1)
            if item.is_file()' in date_str:
                    # Убираем миллисекунды и and item.parent.resolve() == input_dir.resolve():
                 # Проверяем на типичные видео расширения (можно расширить)
                if item.suffix.lower() in ['.avi', '.mp4', '.mov', '.mkv', '.wm Z/смещение для простоты
                    date_str_cleaned = date_str.splitv']:
                    total_fragments_found += 1
                    source_extensions.add(item('.')[0].replace('Z', '')
                    # Обработка смещения (+.suffix.lower()) # Сохраняем расширение
                    # --- Извлечение даты через ffprobe ---
                    creation_date = get_video_creation_date(item, str(ffprobe_path))
                    # ------------------------------------
                    if creation_date:
                        date_key = creation_date
                        files_by_/-HH:MM или +/-HHMM) - упрощенная, игнорируем егоdate[date_key]['files'].append((item.stat().st_mtime, item))
                        # Сохраняем расширение первого файла за этот день
                        if files_by_
                    if '+' in date_str_cleaned: date_str_cleaned = date_strdate[date_key]['ext'] is None:
                            files_by_cleaned.split('+')[0]
                    if '-' in date_str_date[date_key]['ext'] = item.suffix

    print(f"\nНа_cleaned[-6:] and ':' in date_str_cleaned[-6:]: #йдено всего {total_fragments_found} видеофайлов.")
    if stats Проверка на -HH:MM в конце
                          date_str_cleaned = date_["metadata_errors"] > 0:
        print(f"Предупреждение: Не удалось извлечь дату из метаданных для {stats['metadata_str_cleaned[:-6]
                    elif '-' in date_str_cleaned[-5errors']} файлов.")

    if not files_by_date:
        :]: # Проверка на -HHMM
                         date_str_cleaned = dateprint("Не найдено видеофайлов с извлеченной датой создания для обработки.")
        return None, False

    # Считаем статистику для дней_str_cleaned[:-5]

                    parsed_dt = datetime.from, где > 1 файла
    days_with_multiple_files = 0
    forisoformat(date_str_cleaned)
                    return parsed_dt. date, data in files_by_date.items():
        if len(data['files'])date()
                # Формат 'YYYY:MM:DD HH:MM:SS' (EXIF)
                elif ':' in date_str and len(date_str.split()) > 1:
            days_with_multiple_files +=1
            fragments_to == 2:
                    parsed_dt = datetime.strptime(date_str, '%Y:%_process_count += len(data['files'])
            for _, filem:%d %H:%M:%S')
                    return parsed_dt.date()
                # Формат 'YYYY-MM-DD' (или_path in data['files']:
                try:
                    total_size_bytes += file_path.stat().st_size
                except FileNotFoundError: pass
                except OSError: с временем через пробел)
                elif '-' in date_str:
                    parsed_dt = datetime.fromisoformat(date_str.split()[0]) # pass

    if fragments_to_process_count == 0:
        print("\ Берем только дату
                    return parsed_dt.date()
                else:
                    print(f"Предупреждение: Неизвестный формат даты '{nНе найдено дней с количеством видеофрагментов > 1.")
        print("Объединение и загрузка не требуются.")
        return files_by_date, False

    date_str}' в метаданных {file_path.name}")
print("\n--- Информация для подтверждения ---")
    print(f"Обнару                    return None
            except ValueError:
                print(f"Предупреждение: Не удалось расжено {days_with_multiple_files} дней с несколькими фрагментами.")
    printпарсить дату '{date_str}' из метаданных {file_path(f"Всего будет объединено фрагментов: {fragments_to_process_count}")
    .name}")
                return None
        else:
            # Дата не найдена вprint(f"Общий объем этих фрагментов: {get_human_readable_size(total метаданных
            return None

    except subprocess.CalledProcessError as e:
        print(f"Предупреждение: Ошибка ffprobe при ч_size_bytes)}")
    print(f"Обнаруженные типы файлов: {', '.join(source_extensions)}")
    if DELETE_SOURCES_тении метаданных {file_path.name}. Stderr: {e.stderr[-AFTER_MERGE:
         print("ВНИМАНИЕ: Исходные файлы этих фрагментов будут УДАЛЕНЫ после успешного объединения!")
    if GOOGLE_LIBS_AVAILABLE:
        print(f"Будет предпри200:]}")
        stats["metadata_errors"] += 1
        return None
    except json.JSONDecodeError:
        print(f"Предупреждение: Не удалось декодировать JSON от ffprobe для {file_path.nameнята попытка загрузить объединенные видео на YouTube.")
    else:
        print("Загрузка на YouTube недоступна (библиотеки не найдены).")
    print("-" *}")
        stats["metadata_errors"] += 1
        return None 34)

    while True:
        answer = input("Продолжить выполнение
    except Exception as e:
        print(f"Предупре операции? (Y/Да или N/Нет): ").lower().strip()
        if answer in ['ждение: Неожиданная ошибка при чтении метаданных {filey', 'yes', 'д', 'да']:
            return files_by_date, True
        _path.name}: {e}")
        stats["metadata_errors"]elif answer in ['n', 'no', 'н', 'нет']:
            return files_by_date, False
        else:
            print += 1
        return None

def get_creation_date(file_path):
    """Полу("Неверный ввод. Пожалуйста, введите Y или N.")

чает дату создания: сначала из метаданных видео, потом из ФС."""
    # 1. Попытка извлечь из метаданных видео
    metadata_date = get_video_creation_date_from_metadata(file_path)
    # --- Функции YouTube (get_authenticated_service, load_uploaded_log, add_to_uploadedif metadata_date:
        return metadata_date

    # 2_log - без изменений) ---
def get_authenticated_service():
    # ... (без изменений) ...
    global GOOGLE_LIBS_AVAILABLE
    if not GOOGLE_LIBS. Если не удалось, используем дату из файловой системы (как раньше)
    #_AVAILABLE: return None
    creds = None
    if TOKEN_PICKLE_FILE.exists(): print(f"Предупреждение: Дата для {file_path.name}
        try:
            with open(TOKEN_PICKLE_FILE, 'rb') as token: не найдена в метаданных, используется дата файла.") # Опционально
 creds = pickle.load(token)
        except Exception: creds = None
    if not cred    try:
        if platform.system() == "Windows":
            timestamp = file_path.s or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: creds.refresh(google.auth.stat().st_ctime
        else:
            try: timestamp = file_path.stat().sttransport.requests.Request()); print("Токен доступа YouTube обновлен.")
            except Exception_birthtime
            except AttributeError: timestamp = file_path.stat(). as e:
                print(f"Ошибка обновления токена YouTube: {e}"); creds = None
                if TOKEN_PICKLE_FILE.exists(): try: TOKEN_PICKLE_FILE.unlink(); except OSError: pass
        st_mtime
        return datetime.fromtimestamp(timestamp).date()if not creds:
            if not CLIENT_SECRETS_FILE
    except Exception as e:
        print(f"Предупреждение: Не удалось.exists(): print(f"Критическая ошибка: Файл '{CLIENT_SECRETS_FILE.name}' не найден."); return None
            try:
                flow = google_auth_oauth получить дату из ФС для {file_path.name}: {e}")
        returnlib.flow.InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
                creds = flow.run None

def get_human_readable_size(size_bytes):
_local_server(port=0); print("Аутентификация YouTube пройдена.")
                try:
                    with open(TOKEN_PICK    # ... (без изменений) ...
    if size_bytes == 0: returnLE_FILE, 'wb') as token: pickle.dump(creds "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math., token); print(f"Токен сохранен: {TOKEN_PICKLE_FILE.name}")
                except IOError as e: print(f"Предупреждение: Не удалось сохранить тоfloor(math.log(size_bytes, 1024)))кен: {e}")
            except Exception as e: print(f"Ошибка во if size_bytes > 0 else 0
    if i >= len(size_name): i = len(size_name) - 1
    p = math время аутентификации YouTube: {e}"); return None
    try:
        if not creds.pow(1024, i)
    s = round(: return None
        service = googleapiclient.discovery.build(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def scan_and_confirm(input_dir):
    """API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print("Сервис YouTube API инициализирован."); return service
    except Exception as e:
        print(f"Критическая ошибка при создании сервиса YouTube APIСканирует папку, определяет формат, собирает статистику и запрашивает подтверждение: {e}")
        if TOKEN_PICKLE_FILE.exists():."""
    global detected_input_format
    print(f"\nСканирование папки '{input_dir}' на наличие видеофайлов...")
    files_by try: TOKEN_PICKLE_FILE.unlink(); except OSError: pass
_date = defaultdict(list)
    total_files_found = 0
    fragments_to_process_count = 0
    total_size_bytes        return None

def load_uploaded_log():
    # ... (без изменений) ...
     = 0
    first_file_suffix = None

    try:
        uploaded = set();
    if UPLOADED_LOG_FILE.exists():
        try:all_items = list(input_dir.iterdir()) # Получаем
            with open(UPLOADED_LOG_FILE, 'r', encoding список один раз
        with tqdm(total=len(all_items), desc="Сканирование файлов", unit="файл", disable=not TQDM_AVAILABLE) as pbar='utf-8') as f:
                for line in f:
:
            for item in all_items:
                pbar.update(1)
                    filename = line.strip();
                    if filename: uploaded.add(filename)
        except IOError as e: print(f"Предупреждение: Не удалось                # Ищем файлы только в корне input_dir
                # Поддерживаем несколько распространен прочитать лог {UPLOADED_LOG_FILE.name}: {eных видео форматов
                if item.is_file() and item.suffix.lower()}")
    return uploaded

def add_to_uploaded_log(filename):
    # ... ( in ['.avi', '.mp4', '.mov', '.mkv', '.mts', '.m2ts'] \
                   and item.parent.resolve() == input_без изменений) ...
     try:
        with open(UPLOADED_LOG_FILE, 'a', encoding='utf-8') as f: f.write(filenamedir.resolve():

                    # Определяем формат по первому найденному файлу
                    if first + '\n')
     except IOError as e: print(f"Пре_file_suffix is None:
                        first_file_suffix = item.suffix.lower()
                        detected_input_format = first_fileдупреждение: Не удалось записать в лог {UPLOADED_LOG_FILE.name}: {e}")

def upload_to_youtube(youtube_service, file_path_to_upload):
    """За_suffix
                        print(f"\nОбнаружен формат входных файлов: {detected_input_гружает один видеофайл на YouTube с прогресс-баром tqdm."""
    global stats
    ifformat}")

                    # Пропускаем файлы другого формата, если формат уже определен
                    if detected not GOOGLE_LIBS_AVAILABLE or not youtube_service:
        print("    _input_format and item.suffix.lower() != detected_input_format:
                        #Пропуск загрузки: сервис YouTube недоступен.")
        return None

    file_ print(f"Пропуск файла другого формата: {item.name}") #path = Path(file_path_to_upload)
    if not Дебаг
                        continue

                    total_files_found += 1 file_path.exists():
        print(f"Ошибка загрузки: Ви
                    creation_date = get_creation_date(item) # Использудеофайл не найден: {file_path.name}")
        statsем новую функцию
                    if creation_date:
                        files_by_date[["failed_uploads"] += 1
        return None

    try:
        datecreation_date].append((item.stat().st_mtime, item_str = file_path.stem.split('_')[0]; title = f"{DEFAULT_VIDEO_TITLE_PREFIX}{date_str}"; tags = DEFAULT_TAGS + [)) # Сортируем по времени модификации ФС

        if detecteddate_str]
    except Exception:
        title = file_path.stem;_input_format is None:
             print("Видеофайлы для обработки tags = DEFAULT_TAGS

    body = {'snippet': {'title': title, ' не найдены.")
             return None, False

        print(f"description': DEFAULT_VIDEO_DESCRIPTION, 'tags': tags, 'categoryId': DEFAULT_CATEGORY_ID}, 'status': {'privacyStatus': DEFAULT_PRIVACY_STATUS, 'Найдено всего {total_files_found} файлов формата {detected_input_format}.")selfDeclaredMadeForKids': False}}

    print(f"    Заголо
        if stats["metadata_errors"] > 0:
             print(f"Превок: {title}, Приватность: {DEFAULT_PRIVACY_STATUS}")

дупреждение: Было {stats['metadata_errors']} ошибок при ч    try:
        filesize = file_path.stat().st_size
        media = Mediaтении метаданных.")

        if not files_by_date:FileUpload(str(file_path), chunksize=5*1024*1
            print("Не найдено файлов с валидной датой для обработки.")
            return None, False024, resumable=True) # 5MB chunk
        request = youtube

        # Считаем статистику для дней, где > 1 файла
        _service.videos().insert(part=",".join(body.keysfor date, file_info_list in files_by_date.items():
()), body=body, media_body=media)
        response = None; retry            if len(file_info_list) > 1:
                fragments_to_process_count += len(file_info_list)_delay = 5; max_retries = 5; current_
                for _, file_path in file_info_list:
                    retry = 0

        # --- tqdm прогресс-бар для загрузки ---
        with tqdmtry: total_size_bytes += file_path.stat().st_size
                    (total=filesize, unit='B', unit_scale=True, unit_divisor=1except (FileNotFoundError, OSError): pass

        if fragments_to_process_024,
                  desc=f"Загрузка {file_path.name}", ascii='count == 0:
            print("\nНе найдено дней с количеством фрагментов > 1.") >=') as pbar:
            last_progress_bytes = 0
            while response is
            print("Объединение и загрузка не требуются.")
            return None:
                try:
                    status, response = request.next_chunk()
                    if files_by_date, False # Есть данные, но не продолжать

        # Вы status:
                        current_progress_bytes = int(status.progress() * filesize)
                        pbar.update(current_progress_bytes - last_водим информацию пользователю
        print("\n--- Информация для подтверждения ---")progress_bytes) # Обновляем на разницу
                        last_progress_
        print(f"Найдено фрагментов для объединения: {fragments_to_process_countbytes = current_progress_bytes
                    if response:
                        pbar.update} (в днях, где > 1 файла)")
        print(f"Формат файлов: {detected_input_format}")
        print(f"Общий(filesize - last_progress_bytes) # Убедимся что дошли до 100%
                        print(f"\n    УСП объем этих фрагментов: {get_human_readable_size(total_ЕШНО ЗАГРУЖЕНО! Video ID: {response['size_bytes)}")
        if DELETE_SOURCES_AFTER_MERGE:id']}")
                        stats["uploaded_videos"] += 1
                        return response['id'] # Успех
                except googleapiclient.errors.HttpError
             print("ВНИМАНИЕ: Исходные файлы этих фрагментов будут as e:
                    pbar.close() # Закрываем бар при УДАЛЕНЫ после успешного объединения!")
        if GOOGLE_LIBS_AVAILABLE: ошибке
                    print("")
                    if e.resp.status in [403]: print(f"    КРИТИЧЕСКАЯ ОШИБКА API (
            print(f"Будет предпринята попытка загрузить объHttpError {e.resp.status}): {e}"); stats["failed_uploads"] += единенные видео на YouTube.")
            if CREATE_FRAGMENT_LIST_FILE: print("-> После загрузки будет создан .txt со списком исходников.")
            if DELETE_MER1; return None
                    elif e.resp.status in [500, 502, 503, 504]:
                        current_retry += 1
                        ifGED_AFTER_UPLOAD: print("-> После загрузки ОБЪЕДИНЕН current_retry > max_retries: print(f"    ОШИБКА API (HttpErrorНЫЙ файл будет УДАЛЕН.")
        else:
            print("Загрузка на YouTube недоступна (библиотеки не найдены).")
        print("-" * {e.resp.status}): {e}. Превышено кол-во 34)

        # Запрашиваем подтверждение
        while True:
            answer = input("Продолжить выполнение операции? (Y/Да попыток."); stats["failed_uploads"] += 1; return None
 или N/Нет): ").lower().strip()
            if answer in ['                        print(f"    ОШИБКА API (HttpError {e.resp.status}): {y', 'yes', 'д', 'да']: return files_by_date, True
            e}. Попытка #{current_retry}/{max_retries} через {retry_delay} секelif answer in ['n', 'no', 'н', 'нет']: return files_by_date, False
            else: print("Неверный ввод..."); time.sleep(retry_delay); retry_delay *= 2
. Пожалуйста, введите Y или N.")

    except Exception as e: # Ловим общие ошибки сканирования
        print(f"\nК                    else: print(f"    НЕИЗВЕСТНАЯ ОШритическая ошибка во время сканирования папки: {e}")
        importИБКА API (HttpError {e.resp.status}): {e traceback
        traceback.print_exc() # Печатаем полный}"); stats["failed_uploads"] += 1; return None
                    # Возобновляем pbar если будет повторная попытка (не реализовано в этой струк трейсбек для диагностики
        return None, False

# --- Функции YouTube ---
def get_authenticated_service():
    # ... (без изменений) ...
    if not GOOGLE_LIBS_AVAILABLE: return None
    creтуре)
                except Exception as e:
                    pbar.close()
                    print("")ds = None
    if TOKEN_PICKLE_FILE.exists():
        try:
            with open(TOKEN_PICKLE_FILE, 'rb') as token: creds = pickle.load(token)
        except Exception: creds = None
    if not cred
                    current_retry += 1
                    if current_retry > max_retries: print(f"    НЕИЗВЕСТНАs or not creds.valid:
        if creds and credsЯ ОШИБКА ЗАГРУЗКИ: {e}. Пре.expired and creds.refresh_token:
            try:
                вышено кол-во попыток."); stats["failed_uploads"] += creds.refresh(google.auth.transport.requests.Request())
1; return None
                    print(f"    НЕИЗВЕСТНАЯ ОШИБ                print("Токен YouTube обновлен.")
            except Exception as e:
                print(КА ЗАГРУЗКИ: {e}. Попытка #{current_retry}/{max_retries} через {retry_delay} сек..."); time.sleep(retry_delayf"Ошибка обновления токена YouTube: {e}")
                if TOKEN_PICKLE); retry_delay *= 2
                    # Возобновляем pbar если будет повторная попытка

        # Если вышли из цикла без return (не должно произойти при resumable=True, но на всякий случай)
        print_FILE.exists():
                    try: TOKEN_PICKLE_FILE.unlink()("\n    Не удалось завершить загрузку.")
        stats["failed_uploads"]
                    except OSError: pass
                creds = None
        if not creds:
            if += 1
        return None
    except Exception as e:
         not CLIENT_SECRETS_FILE.exists(): print(f"Критическая ошибка: {CLIENT_SECRETS_FILE.name} неprint(f"\n    Критическая ошибка при инициализации загрузки {file_path.name}: найден."); return None
            try:
                flow = google_auth_ {e}")
        stats["failed_uploads"] += 1
        return None

# === ОСНoauthlib.flow.InstalledAppFlow.from_client_secrets_fileОВНАЯ ЛОГИКА ===

def main_processing(files_data, ffmpeg_path_str, ffprobe_path_str):
    """Глав(str(CLIENT_SECRETS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
ная функция: объединение, удаление, загрузка."""
    global stats

    # Создаем папки для временных файлов и списков
    OUTPUT_FOLDER.mkdir(parents                print("Аутентификация YouTube пройдена.")
                try:
                    with open(TOKEN_PICKLE_FILE, 'wb') as token: pickle=True, exist_ok=True)
    MERGED_LIST_.dump(creds, token); print(f"Токен сохранен: {TOKEN_PICKLE_FILE.name}")
                except IOError as e: print(f"ПреFOLDER.mkdir(parents=True, exist_ok=True)
    дупреждение: Не удалось сохранить токен: {e}")
            exceptprint(f"\nПапка для временных объединенных видео: {OUTPUT_FOLDER.relative_to(BASE_DIR)}")
    print(f"Папка Exception as e: print(f"Ошибка аутентификации YouTube: {e}"); для списков объединенных файлов: {MERGED_LIST_FOLDER.relative_to(BASE_DIR)}")

    # Аутентификация YouTube
    youtube = None return None
    try:
        if not creds: return None
        service
    if GOOGLE_LIBS_AVAILABLE:
        print("\nПопытка аутентификации = googleapiclient.discovery.build(API_SERVICE_NAME, в YouTube...")
        youtube = get_authenticated_service()
        if API_VERSION, credentials=creds, static_discovery=False)
        print("Сервис not youtube: print("Не удалось аутентифицироваться в YouTube. За YouTube API инициализирован.")
        return service
    except Exception as e:
        грузка будет пропущена.")
        else: print("Аутенprint(f"Критическая ошибка создания сервиса YouTube API: {e}")
        if TOKENтификация YouTube успешна.")
    else: print("\nЗагрузка на YouTube пропуска_PICKLE_FILE.exists():
             try: TOKEN_PICKLE_ется.")

    # Лог загруженных
    uploaded_files_logFILE.unlink()
             except OSError: pass
        return None

def load = load_uploaded_log()
    print(f"Загружен_uploaded_log():
    # ... (без изменений) ...
     лог YouTube: {len(uploaded_files_log)} файлов уже обработано.")

    #uploaded = set()
    if UPLOADED_LOG_FILE.exists Обработка по дням
    print("\n--- Начало обработки видео по дням ---")():
        try:
            with open(UPLOADED_LOG_FILE, 'r', encoding='utf
    # Фильтруем дни с >1 файла
    dates_to_process =-8') as f:
                for line in f:
                    filename {date: data for date, data in files_data.items() if len(data[' = line.strip();
                    if filename: uploaded.add(filename)
        except IOErrorfiles']) > 1}
    total_dates_to_process = as e: print(f"Предупреждение: Не удалось прочитать len(dates_to_process)
    processed_real_dates = лог {UPLOADED_LOG_FILE.name}: {e}")
    return uploaded

def add_to_uploaded_log(filename):
    # ... (без изменений 0
    if not dates_to_process: print("Нет дней с) ...
    try:
        with open(UPLOADED_LOG_FILE, 'a', encoding='utf-8') as f: f.write(filename >1 файла для обработки."); return

    for date, data in sorted(dates_to_process.items + '\n')
    except IOError as e: print(f"Предупреждение: Не удалось записать в лог {UPLOADED_LOG()):
        processed_real_dates += 1
        date_str = date_FILE.name}: {e}")

def upload_to_youtube(youtube_service, file_path_to_upload):
    """За.strftime('%Y-%m-%d')
        file_info_list = data['files']
гружает видео на YouTube с прогресс-баром tqdm."""
    global stats
    if        file_extension = data['ext'] # Получаем расширение

        if not file_extension: # На всякий случай
             print(f"Предупреждение: Не удалось определить расширение для даты {date_str}. not GOOGLE_LIBS_AVAILABLE or not youtube_service:
        print("     Пропуск.")
             continue

        # Формируем имена файлов с правиПропуск загрузки: сервис YouTube недоступен.")
        return None

    file_path = Path(file_path_to_upload)
    if not file_path.exists():
        print(f"Ошибка загрузки: Вильным расширением
        output_filename = f"{date_str}_деофайл не найден: {file_path.name}"); stats["failed_uploads"] += merged{file_extension}"
        output_filepath = OUTPUT_FOLDER /1; return None

    try:
        date_str = file_path.stem.split('_')[0]; title = f"{DEFAULT_VIDEO_TITLE_PREFIX}{date output_filename
        list_txt_filename = MERGED_LIST_FOLDER /_str}"; tags = DEFAULT_TAGS + [date_str]
    except Exception f"{date_str}_merged_list.txt" # Имя файла списка:
        print(f"Предупреждение: Не удалось извлечь дату из {
        ffmpeg_list_filename = OUTPUT_FOLDER / f"{date_strfile_path.name}."); title = file_path.stem; tags = DEFAULT_TAGS
    }_files.txt" # Временный список для ffmpeg

        printbody = {'snippet': {'title': title, 'description': DEFAULT_VIDEO_DESCRIPTION, 'tags':(f"\n[{processed_real_dates}/{total_dates_to_process}] Обработка tags, 'categoryId': DEFAULT_CATEGORY_ID}, 'status': {'privacy даты: {date_str} ({len(file_info_list)}Status': DEFAULT_PRIVACY_STATUS, 'selfDeclaredMadeForKids': исходных '{file_extension}' файлов)")

        sorted_files = sorted(file_info_list, key=lambda x: x[0])
        source_ False}}

    print(f"    Начало загрузки '{file_path.name}' (file_paths = [f[1] for f in sorted_files]Приватность: {DEFAULT_PRIVACY_STATUS})...")
    try:
        # Размер файла для tqdm
        file_size = file_path.stat().st_size
        media = MediaFileUpload(str(file_path
        source_file_names_only = [p.name for p in source_file), chunksize=5*1024*1024, resumable=True)_paths] # Только имена для списка
        source_file_strings = [
        request = youtube_service.videos().insert(part=",".join(body.keysstr(p.resolve()) for p in source_file_paths]

        merge_successful = False()), body=body, media_body=media)
        response = None
        retry
        merged_file_exists = output_filepath.exists()

        _delay = 5; max_retries = 5; current_retry = 0

        # Проверяем лог загруженных (по имени объединенного файла)
        if output# Создаем прогресс-бар tqdm для загрузки
        progress_desc_filename in uploaded_files_log:
            print(f"     = f"Загрузка {file_path.name}"
        with tqdm(total=file_sizeПропуск: Файл '{output_filename}' уже помечен как загруженный."), unit='B', unit_scale=True, unit_divisor=1
            stats["skipped_days_exists"] += 1
            # Удаляем исходники, если нужно и файл есть (на случай если он остался)
            if DELETE024, desc=progress_desc, ascii=True, disable=_SOURCES_AFTER_MERGE and merged_file_exists:
                 not TQDM_AVAILABLE, ncols=80) as pbar:
            print(f"    Проверка/удаление исходников для уже загруженного {datewhile response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        # Обновляем прогресс-бар по_str}...")
                 # ... (логика удаления исходников, как раньше количеству загруженных байт
                        # status.resumable_progress) ...
                 deleted_for_day = 0; failed_for_day = 0
                 for file_to_delete in source_file_paths: содержит байты
                        pbar.update(status.resumable_progress - pbar.n)
                    if response:
                        pbar.update
                      if file_to_delete.exists():
                          try: file_to_delete.(file_size - pbar.n) # Завершаем до 100%
unlink(); deleted_for_day += 1
                          except OSError as e: print(f"                              print(f"\n    УСПЕШНО ЗАГРУЖЕНЕ УДАЛОСЬ удалить {file_to_delete.name}: {e}"); failed_for_day += 1
                 stats["deleted_sources"] += deleted_for_day; stats["failed_НО! Video ID: {response['id']}")
                        stats["uploaded_videos"] += 1
                        return response['id']
                except googleapiclient.errors.HttpError as e:
                    pbar.close() # Закрываем бар приdeletions"] += failed_for_day
                 if failed_for ошибке
                    print("") # Новая строка после бара
                    if e.resp.status in [403]: print(f"    КРИТИЧЕСКАЯ ОШИ_day == 0 and deleted_for_day > 0: print(f"    БКА API ({e.resp.status}): {e}"); stats["failed_uploadsУдалено {deleted_for_day} исходных файлов.")

            #"] += 1; return None
                    elif e.resp.status in Удаляем и сам объединенный файл, если он вдруг остался
            if output [500, 502, 503, 504]:
                        _filepath.exists():
                try:
                    output_filepath.unlink()
                    current_retry += 1
                        if current_retry > max_retries: print(f"    print(f"    Удален ранее объединенный файл: {output_filename}")
                except OSError as e:
                    print(f"    Предупреждение: Не удалосьОШИБКА API ({e.resp.status}): {e}. Превышено кол-во попыток."); stats["failed_uploads"] += 1; return None
 удалить ранее объединенный файл {output_filename}: {e}")
            continue #                        print(f"    ОШИБКА API ({e.resp.status}): {e}. По К следующей дате

        if merged_file_exists:
            print(f"    Предупреждение: Объединенный файл '{outputпытка #{current_retry}/{max_retries} через {retry__filename}' уже существует, но не загружен.")
            merge_successful = True

        # delay} сек...")
                        for _ in range(retry_delay): time.sleep(1);1. Объединение
        if not merged_file_exists:
            try print(".", end="", flush=True) # Визуальная задержка
                        print("")
                        retry_delay *= 2
                    else: print(f":
                with open(ffmpeg_list_filename, 'w', encoding='utf-8') as f    НЕИЗВЕСТНАЯ ОШИБКА API ({e.resp.status}): {e}"); stats["failed_uploads"] +=:
                    for file_path_str in source_file_strings: f.write(f"file '{file_path_str.replace('\\', '/')}'\n")
            except IOError as e:
 1; return None
                except Exception as e: # Другие ошибки (сеть                print(f"    ОШИБКА: Не удалось создать времен и т.п.)
                     pbar.close(); print("")
                     current_retry += 1ный список для FFmpeg: {e}"); stats["merge_errors"] += 1
                if ffmpeg_list_filename.exists(): ffmpeg_list_filename.unlink
                     if current_retry > max_retries: print(f"(); continue

            command = [
                ffmpeg_path_str, "-y",    НЕИЗВЕСТНАЯ ОШИБКА ЗАГ "-f", "concat", "-safe", "0",
                "-i", str(ffmpegРУЗКИ: {e}. Превышено кол-во попыток.");_list_filename.resolve()),
                "-c", "copy", # stats["failed_uploads"] += 1; return None
                     print(f"    НЕ !!! ЕСЛИ ОШИБКИ - ЗАКОММЕНТИРИЗВЕСТНАЯ ОШИБКА ЗАГРУЗОВАТЬ !!!
                str(output_filepath.resolve())
            КИ: {e}. Попытка #{current_retry}/{max_ret]
            print(f"    Запуск FFmpeg для объединения...")ries} через {retry_delay} сек...")
                     for _ in range(retry

            # --- tqdm индикатор для объединения (без % т.к. -_delay): time.sleep(1); print(".", end="", flush=True)
                     print("")
                     retry_delay *= 2
        # Если цикл завершился безc copy) ---
            process = None
            try:
                 # Запускаем в фоне, чтобы tqdm мог работать
                 process = subprocess.Popen return (не должно случиться, но на всякий случай)
        print("\n    Не(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, удалось завершить загрузку."); stats["failed_uploads"] += 1; return None

    except Exception as e:
        print(f"\n    Критическая ошибка при инициализации загру encoding='utf-8', errors='ignore')
                 with tqdm(desc=f"Объединение {date_str}", unit="op", barзки {file_path.name}: {e}"); stats["failed_uploads"] += _format='{l_bar}{bar}| {elapsed}') as pbar:
                     while1; return None

def create_fragment_list_file(output_filepath, source_file_paths):
    """Создает .txt файл со списком исходных файлов process.poll() is None: # Пока процесс работает
                         pbar.update(1) # Просто двигаем бар
                         time.sleep(0.5) # Пауза, чтобы не гру."""
    global stats
    txt_filename = output_filepath.withзить CPU
                 # Проверяем результат после завершения
                 stdout, stderr =_suffix('.txt')
    target_dir = BASE_DIR / MOVE_UPLOADED_TXT_TO
    target_dir.mkdir(parents=True, exist_ process.communicate()
                 if process.returncode == 0:
                     print(fok=True) # Создаем папку, если ее нет
    target"\n    Объединение успешно завершено: '{output_filename}'")
                     merge_txt_path = target_dir / txt_filename.name # Путь для перемещения

    print(f"    Создание списка фрагментов: {target_successful = True; stats["merged_days"] += 1
                 else:
                     print_txt_path.name}...")
    try:
        with open(target_txt_path, 'w', encoding='utf-8') as f(f"\n    ОШИБКА FFmpeg при объединении (код {process.returncode})!")
                     print(f"    Сообщение (stderr): {stderr[-500:]}..."); merge_successful = False; stats["merge:
            f.write(f"Фрагменты, объединенные в файл: {output_filepath.name}\n")
            f.write("="_errors"] += 1
            except Exception as e:
                print(f * 30 + "\n")
            for source_path in source_file_paths"\n    Неожиданная ОШИБКА при вызове FFmpeg: {e:
                f.write(f"{source_path.name}\n")
        }"); merge_successful = False; stats["merge_errors"] += 1
print(f"    Список фрагментов успешно создан: {target_txt_path}")                if process and process.poll() is None: process.kill() # У
        stats["txt_created"] += 1
        return True
биваем процесс, если он завис
            finally:
                 if ffmpeg_list_filename.    except IOError as e:
        print(f"    ОШИБКА приexists():
                     try: ffmpeg_list_filename.unlink()
                     except OSError создании файла списка фрагментов {target_txt_path.name}: {e}")
        stats["failed_: pass
            # --- Конец tqdm обертки ---

        # 2txt"] += 1
        return False

# === ОСНОВНАЯ ЛОГИКА ===

def main_processing(files_by_date):
    """Глав. Удаление исходников (если успешно и включено)
        if merge_successfulная функция: объединение, удаление, загрузка."""
    global stats, and DELETE_SOURCES_AFTER_MERGE:
            print(f" ffmpeg_path, detected_input_format # Используем глобальные пути    Удаление исходных файлов для {date_str}...")
            # ... (логика удаления и формат

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True) исходников, как раньше) ...
            deleted_for_day = 0
    print(f"\nПапка для объединенных видео: {OUTPUT_FOLDER}")
    uploaded; failed_for_day = 0
            for file_to_delete in source_file_paths:
                 if file_to_delete_txt_dir = BASE_DIR / MOVE_UPLOADED_TXT_TO
    uploaded_txt.exists():
                     try: file_to_delete.unlink(); deleted_dir.mkdir(parents=True, exist_ok=True)
    print(f"Папка для логов (.txt) загруженных видео_for_day += 1
                     except OSError as e: print(: {uploaded_txt_dir.relative_to(BASE_DIR)}")

    youtube = None
    if GOOGLE_LIBS_AVAILABLE:
        printf"      НЕ УДАЛОСЬ удалить {file_to_delete.name}: {e}"); failed_for_day += 1
            stats("\nПопытка аутентификации в YouTube...")
        youtube =["deleted_sources"] += deleted_for_day; stats["failed_ get_authenticated_service()
        if not youtube: print("Не удалось аутентифициdeletions"] += failed_for_day
            if failed_forроваться в YouTube. Загрузка будет пропущена.")
        else: print("Аутентификация YouTube успешна.")
    else: print_day == 0 and deleted_for_day > 0: print("\nЗагрузка на YouTube пропускается.")

    uploaded_files_log =(f"    Удалено {deleted_for_day} исходных load_uploaded_log()
    print(f"Загружен лог YouTube: {len(uploaded_files_log)} файлов уже обработано.")

    print файлов.")
            elif deleted_for_day > 0 or failed_for_day > 0("\n--- Начало обработки видео по дням ---")
    dates_to_process =: print(f"    Удалено: {deleted_for_day {date: info for date, info in files_by_date.items}, Ошибок: {failed_for_day}")

        # 3. Загрузка на YouTube (если успешно и сервис доступен)
        if merge_() if len(info) > 1}
    if not dates_to_process: print("Нет дней с >1 файла для обработки."); return

    # Общийsuccessful and GOOGLE_LIBS_AVAILABLE and youtube:
            video_id = upload_to_youtube(youtube, output_filepath)

            if video_id:
                 прогресс-бар по дням
    progress_bar_days = tqdm(sorted# 4. Создание файла списка фрагментов
                print(f"    Создание списка фрагментов: {list_txt_filename.name}")
                try:
                    with(dates_to_process.items()),
                             desc="Обработка дней",
                             unit=" open(list_txt_filename, 'w', encoding='utf-8день",
                             total=len(dates_to_process),
                             disable=not TQDM_AVAILABLE,
                             ncols=80,
                             ascii=True)

') as f:
                        f.write(f"Фрагменты,    for date, file_info_list in progress_bar_days:
        date объединенные в файл: {output_filename}\n")
                        f_str = date.strftime('%Y-%m-%d')
        #.write(f"Дата объединения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("-" * 20 + "\n")
                        for name in source_file_names Используем автоопределенный формат
        output_filename = f"{date_str}_merged{detected_input_format}"
        output_filepath = OUTPUT_only:
                            f.write(name + '\n')
                    _FOLDER / output_filename
        list_filename = OUTPUT_FOLDER / f"{date_str}_files.txt"

        # Обновляем описание прогресс-бара для текущего дняprint(f"    Список успешно создан.")
                    stats["list_created"] += 1

                    # 5. Удаление объединенного файла ПОСЛЕ создания списка
                    print(f"    Удаление временного объ
        progress_bar_days.set_description(f"Обработка {date_str}")

        # Используем print для логов внутри tqdm, чтобы не перекрывать бар
        # tqdm.write(f"\nОбработка датыединенного файла: {output_filename}")
                    try:
                        output_filepath.unlink()
                        print(f"    Файл успешно удален.")
                        stats["deleted_merged"] += 1
                    except OSError as e:
                        : {date_str} ({len(file_info_list)} исходных файлов)") #print(f"    ОШИБКА при удалении объединенного файла: {e}")
 Вариант вывода

        sorted_files = sorted(file_info_list, key=lambda x: x[0])
        source_file_paths =                        stats["failed_merged_deletions"] += 1

                    # 6. Добавление в лог УЖЕ ПОСЛЕ ВСЕХ ДЕЙСТВИЙ
                    add_to_uploaded_log(output_filename) # Логги [f[1] for f in sorted_files]
        source_file_strings = [str(p.resolve()) for p in source_file_paths]
        merge_successful = False
        руем имя файла, который был загружен
                    uploaded_files_log.add(output_filename)

merged_file_exists = output_filepath.exists()

        if output_filename in uploaded_files_                except IOError as e:
                    print(f"    ОШИБКА приlog:
            tqdm.write(f"[{date_str}] Пропуск: создании файла списка {list_txt_filename.name}: {e}")
                    stats Файл '{output_filename}' уже помечен как загруженный.")
            stats["skipped["failed_list_creations"] += 1
                    # Не удаляем объединенный файл и_days_exists"] += 1
            # Удаляем исходники, если нужно
            if DELETE_SOURCES_AFTER_MERGE and merged_file_exists не логгируем, если список не создался
            else:
                :
                 # tqdm.write(f"[{date_str}] Удаление исходников для уже загруженного...") # Меньше спама
                 deleted_for_day# Ошибка загрузки (уже залогирована)
                print(f"    За = 0; failed_for_day = 0
                 for file_to_delete in source_file_paths:
                      if file_to_delete.existsгрузка '{output_filename}' не удалась. Файл не будет удален, список не будет создан.")
                # Оставляем объединенный файл для():
                          try: file_to_delete.unlink(); deleted_for повторной попытки

        elif not merge_successful:
             print(f"    Про_day += 1
                          except OSError: failed_for_day += 1
пуск дальнейших действий из-за ошибки объединения.")
        elif not (                 stats["deleted_sources"] += deleted_for_day; stats["failed_deletions"] += failed_for_day
                 # if failed_for_day >GOOGLE_LIBS_AVAILABLE and youtube):
            print(f"    Пропуск загру 0: tqdm.write(f"[{date_str}] Ошибок удаления исходников: {failed_for_day}")
            continue # К следузки и связанных действий (YouTube недоступен).")


# === Точка входа ===
if __name__ == "__main__":
    print("--- Запуск программы обработки видео ---")
    ющей дате (следующей итерации tqdm)

        if mergedprint(f"Версия Python: {platform.python_version()}")
_file_exists:
            tqdm.write(f"[{date_str}] Предупреждение: Файл '{output_filename}' уже существует.")
            merge_successful = True    print(f"ОС: {platform.system()} {platform.

        # 1. Объединение
        if not merged_file_exists:
            release()}")
    if not GOOGLE_LIBS_AVAILABLE:
         print("\try:
                with open(list_filename, 'w', encoding='utf-8') as f:
                    for file_path_str innПредупреждение: Библиотеки Google API не найдены. Загрузка source_file_strings: f.write(f"file '{file_path_str.replace('\\', '/')}'\n")
            except IOError as e:
 на YouTube недоступна.")
         print("Установите: pip install google-api-python-                tqdm.write(f"[{date_str}] ОШИБКА: Не удалось создать файл списка {list_filename.name}: {e}"); stats["mergeclient google-auth-httplib2 google-auth-oauthlib\n")

    # 1._errors"] += 1
                if list_filename.exists(): list_filename.unlink(); continue

 Поиск/скачивание FFmpeg и FFprobe
    ffmpeg_path,            command = [
                str(ffmpeg_path), "-y", "- ffprobe_path = find_or_download_ffmpeg_tools()
hide_banner", "-loglevel", "warning", # Меньше вывода ffmpeg
                "-f",    if not ffmpeg_path or not ffprobe_path:
         "concat", "-safe", "0",
                "-i", str(list_filename.resolve()),
                "-c", "copy", # !!! Копирование кодеков !!!print("\nКритическая ошибка: Не удалось найти или скачать необходимые инструменты FFmpeg/FFprobe.")
        input("Нажмите Enter для выхода...")
        sys.exit(1
                str(output_filepath.resolve())
            ]
            tqdm.write(f"[{date_str}] Запуск FFmpeg для объединения...")
            start_time = time.monotonic()
            try:
                # Запускаем без capture_output, чтобы ffmpeg мог писать свой прогресс (если он есть)
)

    # 2. Сканирование и подтверждение
    files_data, confirmed = scan_and_confirm(INPUT_FOLDER, ffprobe_path)                # Но это может засорить вывод tqdm, лучше capture_output=True
                result = subprocess.run(command, capture_output=True, text=True

    if not confirmed:
        print("\nОперация отменена пользователем.")
    elif files_data is None:
         print("\nНе удалось, check=True, encoding='utf-8', errors='ignore')
                duration = time.monotonic() - start_time
                tqdm.write(f"[{date просканировать файлы. Выход.")
    else:
        # 3. Запуск_str}] Объединение успешно ({duration:.1f} сек): '{ основного процесса
        try:
            main_processing(files_data,output_filename}'")
                merge_successful = True; stats["merged_days"] += 1
            except subprocess.CalledProcessError as e str(ffmpeg_path), str(ffprobe_path))
            # 4. Финальная статистика
            print("\n--- Завершение работы ---")
            print("Статистика выполнения:")
            print(f"- Дней с >1 файлом успешно:
                duration = time.monotonic() - start_time
                tqdm.write(f"[{date_str}] ОШИБКА FFmpeg ({duration:. объединено: {stats['merged_days']}")
            print(f"- Дней пропущено (уже загружено/обработано): {stats['skipped_days_exists']}")
            print(f"- Ошибок1f} сек)! Код: {e.returncode}. Stderr: {e.stderr[- при объединении (FFmpeg): {stats['merge_errors']}")
            print(f"-300:]}...")
                merge_successful = False; stats["merge_errors"] += 1
            except Exception as e:
                duration Ошибок извлечения даты из метаданных: {stats['metadata_errors']}")
            if DELETE_SOURCES_AFTER_MERGE:
                print(f"- Исходных файлов удалено: {stats['deleted_sources']}")
                print(f"- Ошибок при уда = time.monotonic() - start_time
                tqdm.write(f"[{date_str}] Неожиданная ОШИБКА FFmpeg ({duration:.1f} сек): {e}"); merge_successful = False; stats["merge_errors"] += 1
            finally:
                 if list_filename.exists():
лении исходников: {stats['failed_deletions']}")
            else:
                print("- Удаление исходных файлов было ОТКЛЮЧЕНО.")
                     try: list_filename.unlink()
                     except OSError: pass

        # 2. Удаление исходников
        if merge_successful and DELETE_SOURCES_AFTER_            if GOOGLE_LIBS_AVAILABLE:
                print(f"- Видео успешно загружено на YouTube: {stats['uploaded_videos']}")
                print(f"- ОMERGE:
            # tqdm.write(f"[{date_str}] Удаление исходных файлов...") # Меньше спама
            deleted_for_day = 0;шибок при загрузке на YouTube: {stats['failed_uploads']}")
                print(f failed_for_day = 0
            for file_to_delete"- Списков фрагментов создано: {stats['list_created']}")
                print(f in source_file_paths:
                 if file_to_delete.exists():
                     try: file_to_delete.unlink(); deleted_"- Ошибок при создании списков: {stats['failed_list_creations']}")
                for_day += 1
                     except OSError: failed_for_day += 1
print(f"- Объединенных файлов удалено после загрузки: {stats['deleted_merged            stats["deleted_sources"] += deleted_for_day; stats["failed_deletions"] += failed_for_day
            if failed']}")
                print(f"- Ошибок при удалении объединенных файлов: {stats['failed_merged_deletions']}")
            else:
                print("-_for_day > 0: tqdm.write(f"[{date_str}] Ошибок удаления Загрузка на YouTube и связанные действия были пропущены.")
            print("-" * 25) исходников: {failed_for_day}")

        # 3. Загрузка, создание TXT, удаление объединенного
        if merge_successful and GOOGLE_LIBS_AVAILABLE and youtube and output_filename not in

        except Exception as main_exc:
            print("\n!!! Неперехваченная КРИТИЧЕСКАЯ ОШИБКА в основном процессе !!!")
            print( uploaded_files_log:
            # Оборачиваем вызов upload_to_youtube, чтобы он писал через tqdm.write
            original_write = sys.stdout.write
f"Тип ошибки: {type(main_exc).__name__}")            try:
                sys.stdout.write = lambda s: tqdm.write(s, end='') # Перенаправляем stdout в tqdm
                video_id = upload_to_youtube
            print(f"Сообщение: {main_exc}")
            import traceback
            traceback.print_exc()

    input("\nНажмите Enter для выхода...")
    sys.exit(0)
