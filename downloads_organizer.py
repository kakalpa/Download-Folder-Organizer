import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import pathlib

class MyHandler(FileSystemEventHandler):
    def __init__(self, download_folder):
        super().__init__()
        self.download_folder = download_folder
        self.logger = logging.getLogger(__name__)
        self.categorise_existing_files()

    def categorise_existing_files(self):
        existing_files = os.listdir(self.download_folder)
        for file in existing_files:
            self.categorise_file(file)

    def categorise_file(self, filename):
        src_file = os.path.join(self.download_folder, filename)
        categorise_files(src_file, self.download_folder, self.logger)

    def on_created(self, event):
        # Handle created events (e.g., new files)
        categorise_files(event.src_path, self.download_folder, self.logger)

def categorise_files(src_file, download_folder, logger):
    if os.path.isfile(src_file):
        filename = os.path.basename(src_file)
        file_extension = pathlib.Path(filename).suffix.lower()

        documents = [".doc", ".docx", ".pdf", ".txt", ".rtf"]
        videos = [".mp4", ".mov", ".avi"]
        photos = [".jpg", ".jpeg", ".png", ".gif"]
        programs = [".exe", ".msi"]
        compressed = [".zip", ".rar",".7zip"]

        if file_extension in documents:
            target_folder = os.path.join(download_folder, "Documents")
        elif file_extension in videos:
            target_folder = os.path.join(download_folder, "Videos")
        elif file_extension in photos:
            target_folder = os.path.join(download_folder, "Photos")
        elif file_extension in programs:
            target_folder = os.path.join(download_folder, "Programs")
        elif file_extension in compressed:
            target_folder = os.path.join(download_folder, "Compressed")
        else:
            target_folder = os.path.join(download_folder, "Other")

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        try:
            shutil.move(src=src_file, dst=os.path.join(target_folder, filename))
            logger.info(f"Moved {filename} to {target_folder}")
        except Exception as e:
            logger.error(f"Error moving {filename}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        download_folder = sys.argv[1]
    else:
        download_folder = os.path.join(r"C:\Users", os.getlogin(), "Downloads")

    logging.basicConfig(filename="files.log", level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    logger = logging.getLogger(__name__)

    event_handler = MyHandler(download_folder)
    observer = Observer()
    observer.schedule(event_handler, path=download_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
