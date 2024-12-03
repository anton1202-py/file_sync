import os
from datetime import datetime
from pathlib import Path

from flask import abort, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import ConfigProject
from models.models import FileInfo

# DATABASE_URL = f"postgresql://admin:testadmin@localhost/filedb"
# engine = create_engine(DATABASE_URL)
# # Создайте сессию
# Session = sessionmaker(bind=engine)
# session = Session()


class SyncFileWithDb:
    """Синхронизация файлов с базой данных"""

    def __init__(self, session):
        self.session = session

    def _add_files(self, directory: str) -> None:
        """Добавлет файлы в БД"""

        files_to_insert = []
        for root, dirs, files in os.walk(directory):
            data = (
                self.session.query(FileInfo)
                .filter(FileInfo.path_file == str(root).replace("\\", "/"))
                .all()
            )
            if data:
                for file_obj in data:
                    common_file_path = os.path.join(
                        file_obj.path_file, file_obj.name + file_obj.extension
                    )
                    if not common_file_path:
                        self.session.delete(file_obj)
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
                file_obj = (
                    self.session.query(FileInfo)
                    .filter(
                        FileInfo.name == str(file_name),
                        FileInfo.path_file == file_path,
                        FileInfo.extension == file_extension,
                    )
                    .first()
                )
                if not file_obj:
                    db_file_info = FileInfo(
                        name=str(file_name),
                        extension=str(file_extension),
                        path_file=file_path,
                        size=file_size,
                    )
                    files_to_insert.append(db_file_info)
                if (len(files_to_insert) >= 7000 and i < (len(files) - 2)) or (
                    i == (len(files) - 1) and files_to_insert
                ):
                    self.session.bulk_save_objects(files_to_insert)
                    self.session.commit()
                    files_to_insert = []

    def _del_files_from_db(self, directory: str) -> None:
        """Удаляет файлы из БД, если нет в файловом хранилище"""
        for root, dirs, files in os.walk(directory):
            # Сравниваю, есть ли в файловой системе файлы, которые есть в БД.
            # Если нет - удаляю из БД
            data = (
                self.session.query(FileInfo)
                .filter(FileInfo.path_file == str(root).replace("\\", "/"))
                .all()
            )
            if data:
                for file_obj in data:
                    common_file_path = os.path.join(
                        file_obj.path_file, file_obj.name + file_obj.extension
                    )
                    if not common_file_path:
                        self.session.delete(file_obj)
                        self.session.commit()

    def sync_local_storage_with_db(self, directory):
        """Синхронизирует локальное хранилище файлов с базой данных"""
        self._add_files(directory)
        self._del_files_from_db(directory)

    def sync_files(self) -> list[FileInfo]:
        self.sync_local_storage_with_db(ConfigProject.basedir)
        response = FileInfo.query.filter(
            FileInfo.path_file.like(f"%{ConfigProject.basedir}%")
        )
        return response


class WorkerWithFIles:

    def __init__(self, session, synchron: SyncFileWithDb = None, *args, **kwargs):
        super().__init__()
        self.session = session
        self.synchron = synchron
        self.page = int(kwargs.get("page", 1))
        self.per_page = int(kwargs.get("per_page", 100))
        self.file_id = kwargs.get("file_id", None)
        self.directory_name = kwargs.get("directory_name", None)
        self.upload_path = kwargs.get("upload_path", None)
        self.file_obj = kwargs.get("file_obj", None)
        self.new_name = kwargs.get("new_name", None)
        self.new_path_file = kwargs.get("new_path_file", None)
        self.new_comment = kwargs.get("new_comment", None)

    def create_answer_for_request(self, query):
        """Создает ответ для АПИ"""
        paginated_files = query.paginate(
            page=self.page, per_page=self.per_page, error_out=False
        )
        file_amount = paginated_files.total
        total_size = sum(file.size for file in paginated_files.items)
        file_list = [file.to_answer() for file in paginated_files.items]

        response = {
            "file_amount": file_amount,
            "total_size": total_size,
            "current_page": paginated_files.page,
            "total_pages": paginated_files.pages,
            "has_next": paginated_files.has_next,
            "has_prev": paginated_files.has_prev,
            "per_page": self.per_page,
            "files": file_list,
        }
        return response

    def get_files_info(self) -> dict:
        """
        Информация по всем файлам

        Для получения полного списка файлов используйте
        пагинацию с помощью **per_page** и **page**.
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """

        query = self.session.query(FileInfo).all()
        file_list = [file.to_answer() for file in query]
        # response = self.create_answer_for_request(query)
        return file_list

    def files_in_folder(self) -> dict:
        """
        Информация по файлам из введенной папки

        Для получения полного списка файлов используйте
        пагинацию с помощью **per_page** и **page**.
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """

        if not self.directory_name:
            return {"message": "directory_name is required"}, 400
        query = self.session.query(FileInfo).filter(
            FileInfo.path_file.like(f"%{self.directory_name}%")
        )
        response = self.create_answer_for_request(query)
        return response

    def one_file_info(self):
        """Информация по одному файлу"""
        if not self.file_id:
            return {"message": "file_id is required"}
        file = self.session.query(FileInfo).filter(FileInfo.id == self.file_id).first()
        if not file:
            return {"message": "File not found."}
        return file.to_answer()

    def get_download_file(self):
        """Скачать файл по ID"""
        try:
            if not self.file_id:
                return {"message": "file_id is required"}
            file = FileInfo.query.filter(FileInfo.id == self.file_id).first()
            if not file:
                return {"message": "File not found."}
            file_path = os.path.join(file.path_file, file.name + file.extension)
            if not os.path.isfile(file_path):
                abort(404, description="File not found on server")
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return {"message": str(e)}

    def upload_file(self):
        """Загрузить файл в базу данных"""

        if self.file_obj is None or self.file_obj.filename == "":
            return {"error": "No selected file"}
        if not self.upload_path:
            self.upload_path = ConfigProject.basedir
        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)
        file_path = os.path.join(self.upload_path, self.file_obj.filename)
        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)
        self.file_obj.save(file_path)
        path = Path(file_path)
        file_name = path.stem
        file_extension = path.suffix
        file_size = round(os.path.getsize(path) / 1024, 2)
        new_file_info = FileInfo(
            name=str(file_name),
            extension=str(file_extension),
            path_file=self.upload_path,
            size=file_size,
        )
        try:
            file = FileInfo.query.filter(
                FileInfo.name == file_name,
                FileInfo.extension == file_extension,
                FileInfo.path_file == self.upload_path,
            ).first()
            if not file:
                self.session.add(new_file_info)
                self.session.commit()
                return {
                    "message": f"File info saved successfully! File ID = {new_file_info.id}"
                }
            else:
                return {"error": "Файл уже существет"}
        except Exception as e:
            return {"error": str(e)}

    def delete_file(
        self,
    ):
        """Удаляет файл из базы данных и из файловой системы."""
        if not self.file_id:
            return {"message": "file_id is required"}
        file = FileInfo.query.filter(FileInfo.id == self.file_id).first()
        if not file:
            return {"message": "File not found."}

        file_path = os.path.join(file.path_file, file.name + file.extension)
        if not os.path.isfile(file_path):
            abort(404, description="File not found on server")
        try:
            os.remove(file_path)
            self.session.delete(file)
            self.session.commit()
            return {"message": "File deleted successfully"}
        except Exception as e:
            self.session.rollback()  # Откат транзакции в случае ошибки
            return {"error": str(e)}

    def update_file(self):
        """Обновляет информацию о файле"""
        try:
            file_obj = FileInfo.query.filter(FileInfo.id == int(self.file_id)).first()
            if file_obj is None:
                return {"message": "File not found."}

            old_file_path = os.path.join(
                file_obj.path_file, file_obj.name + file_obj.extension
            )
            update_name = file_obj.name
            update_path = file_obj.path_file
            update_comment = file_obj.comment

            if self.new_name:
                update_name = self.new_name
            if self.new_comment:
                update_comment = self.new_comment
            if self.new_path_file:
                update_path = self.new_path_file

            file_obj.name = update_name
            file_obj.path_file = update_path
            file_obj.comment = update_comment
            if update_name == self.new_name or update_path == self.new_path_file:
                file_obj.date_change = datetime.now()
            self.session.commit()
            new_file_path = os.path.join(
                file_obj.path_file, file_obj.name + file_obj.extension
            )
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
            else:
                return {"message": " Old file not found."}

            return file_obj.to_answer()
        except Exception as e:
            return {"error": str(e)}
