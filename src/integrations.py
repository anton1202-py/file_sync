import os
from pathlib import Path

from models import FileInfo, db, app


class SyncFileWithDb:
    """Синхронизация файлов с базой данных"""

    def __init__(self):
        self.app = app

    def _add_files(self, directory: str) -> None:
        """Добавлет файлы в БД"""
        with self.app.app_context():
            files_to_insert = []
            for root, dirs, files in os.walk(directory):
            # Сравниваю, есть ли в файловой системе файлы, которые есть в БД.
            # Если нет - удаляю из БД
                data = (
                    db.session.query(FileInfo)
                    .filter(FileInfo.path_file == str(root).replace("\\", "/"))
                    .all()
                )
                if data:
                    for file_obj in data:
                        common_file_path = os.path.join(file_obj.path_file, file_obj.name + file_obj.extension)
                        if not common_file_path:
                            db.session.delete(file_obj)

                # Записываю в БД файлы, которые еще не записаны
                for i, file in enumerate(files):
                    common_file_data = Path(file)
                    path_with_file_and_extension = os.path.join(root, file)

                    file_path = str(Path(path_with_file_and_extension).parent).replace(
                        "\\", "/"
                    )
                    file_name = common_file_data.stem
                    file_extension = common_file_data.suffix
                    try:
                        file_size = round(
                            os.path.getsize(path_with_file_and_extension) / 1024, 2
                        )
                    except:
                        file_size = 0

                    if (not db.session.query(FileInfo).filter(
                        FileInfo.name == str(file_name), FileInfo.path_file == file_path).first()):
                        db_file_info = FileInfo(
                            name=str(file_name),
                            extension=str(file_extension),
                            path_file=file_path,
                            size=file_size,
                        )
                        files_to_insert.append(db_file_info)
                    if (len(files_to_insert) >= 7000 and i < (len(files) - 2)) or (
                        i == (len(files) - 1) and files_to_insert):
                        db.session.bulk_save_objects(files_to_insert)
                        db.session.commit()
                        files_to_insert = []

    def _del_files_from_db(self, directory: str) -> None:
        """Удаляет файлы из БД, если нет в файловом хранилище"""
        with self.app.app_context():
            for root, dirs, files in os.walk(directory):
                # Сравниваю, есть ли в файловой системе файлы, которые есть в БД.
                # Если нет - удаляю из БД
                data = (
                    db.session.query(FileInfo)
                    .filter(FileInfo.path_file == str(root).replace("\\", "/"))
                    .all()
                )
                if data:
                    for file_obj in data:
                        common_file_path = os.path.join(file_obj.path_file, file_obj.name + file_obj.extension)
                        if not common_file_path:
                            db.session.delete(file_obj)
                            db.session.commit()

    def sync_local_storage_with_db(self, directory):
        """Синхронизирует локальное хранилище файлов с базой данных"""
        self._add_files(directory)
        self._del_files_from_db(directory)