import os
from datetime import datetime
from pathlib import Path

from flask import abort, send_file

from config import ConfigProject
from injectors.injectors import SyncFileWithDb
from models.models import FileInfo, db


class MainResponse:
    def __init__(self, synchron: SyncFileWithDb = None, *args, **kwargs):
        super().__init__()
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

    def sync_files(self):
        try:
            self.synchron.sync_local_storage_with_db(ConfigProject.basedir)
            query = FileInfo.query.filter(
                FileInfo.path_file.like(f"%{ConfigProject.basedir}%")
            )
            response = self.create_answer_for_request(query)
            return response, 200
        except Exception as e:
            return {"message": f"{e}"}, 400

    def get_files_info(self):
        """
        Информация по всем файлам

        Для получения полного списка файлов используйте
        пагинацию с помощью **per_page** и **page**.
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """
        try:
            query = FileInfo.query
            response = self.create_answer_for_request(query)
            return response, 200
        except Exception as e:
            return {"message": str(e)}, 400

    def files_in_folder(self):
        """
        Информация по файлам из введенной папки

        Для получения полного списка файлов используйте
        пагинацию с помощью **per_page** и **page**.
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """
        try:
            if not self.directory_name:
                return {"message": "directory_name is required"}, 400
            query = FileInfo.query.filter(
                FileInfo.path_file.like(f"%{self.directory_name}%")
            )
            response = self.create_answer_for_request(query)
            return response, 200
        except Exception as e:
            return {"message": f"{e}"}, 400

    def one_file_info(self):
        """Информация по одному файлу"""
        try:
            if not self.file_id:
                return {"message": "file_id is required"}, 400
            file = FileInfo.query.filter(FileInfo.id == self.file_id).first()
            if not file:
                return {"message": "File not found."}, 404
            return file.to_answer(), 200
        except Exception as e:
            return {"message": str(e)}, 500

    def get_download_file(self):
        """Скачать файл по ID"""
        try:
            if not self.file_id:
                return {"message": "file_id is required"}, 400
            file = FileInfo.query.filter(FileInfo.id == self.file_id).first()
            if not file:
                return {"message": "File not found."}, 404
            file_path = os.path.join(file.path_file, file.name + file.extension)
            if not os.path.isfile(file_path):
                abort(404, description="File not found on server")
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return {"message": str(e)}, 500

    def upload_file(self):
        """Загрузить файл в базу данных"""

        if self.file_obj is None or self.file_obj.filename == "":
            return {"error": "No selected file"}, 400
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
                db.session.add(new_file_info)
                db.session.commit()
                return {
                    "message": f"File info saved successfully! File ID = {new_file_info.id}"
                }, 200
            else:
                return {"error": "Файл уже существет"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def delete_file(
        self,
    ):
        """Удаляет файл из базы данных и из файловой системы."""
        if not self.file_id:
            return {"message": "file_id is required"}, 400
        file = FileInfo.query.filter(FileInfo.id == self.file_id).first()
        if not file:
            return {"message": "File not found."}, 404

        file_path = os.path.join(file.path_file, file.name + file.extension)
        if not os.path.isfile(file_path):
            abort(404, description="File not found on server")
        try:
            os.remove(file_path)
            db.session.delete(file)
            db.session.commit()
            return {"message": "File deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            return {"error": str(e)}, 500

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
            db.session.commit()
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
