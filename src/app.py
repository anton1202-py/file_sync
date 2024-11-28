from datetime import datetime
import os
from pathlib import Path
from flask import request, send_file, abort
from integrations import SyncFileWithDb
from models import db, FileInfo, app
from flask_restx import Api, Resource

from flasgger import Swagger

api = Api(app, version='1.0', title='File API',
             description='Работа с файлами и сохранением их в базу данных',
             )
swagger = Swagger(app)



class FileSync(Resource):
    def post(self):
        """
        Cинхронизация базы данных с папкой.

        Показывает файлы, которые есть в введенной папке. Если файлы из этой папки
        есть в базе, но нет в локальном хранилище - они удалятся из базы

        Для получения полного списка файлов используйте 
        пагинацию с помощью **per_page** и **page**.  
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """
        try:
            sync = SyncFileWithDb()
            data = request.get_json()

                # Извлекаем название папки и параметры пагинации
            directory_name = data.get('directory_name')
            page = data.get('page', 1)
            per_page = data.get('per_page', 100)
            if not directory_name:
                return {"message": "directory_name is required"}, 400
            sync.sync_local_storage_with_db(directory_name)
                
                # Извлекаем все записи из базы данных, которые соответствуют указанной папке
            query = FileInfo.query.filter(FileInfo.path_file.like(f"%{directory_name}%"))
                
                # Пагинация
            paginated_files = query.paginate(page=page, per_page=per_page, error_out=False)
                
                # Подсчитываем количество файлов и общую сумму размеров
            file_amount = paginated_files.total  # Общее количество файлов
            total_size = sum(file.size for file in paginated_files.items)

                # Формируем список файлов с их метаданными
            file_list = []
            for file in paginated_files.items:
                    file_data = {
                        "id": file.id,
                        "name": file.name,
                        "extension": file.extension,
                        "path_file": file.path_file,
                        "size": file.size,
                        "date_create": file.date_create.isoformat(),
                        "date_change": file.date_change.isoformat() if file.date_change else None,
                        "comment": file.comment,
                    }
                    file_list.append(file_data)

                # Формируем финальный ответ
            response = {
                    "file_amount": file_amount,
                    "total_size": total_size,
                    "current_page": paginated_files.page,
                    "total_pages": paginated_files.pages,
                    "per_page": per_page,
                    "has_next": paginated_files.has_next,
                    "has_prev": paginated_files.has_prev,
                    "files": file_list
                
                }
            return response, 200
        except Exception as e:
            return {"message": f"{e}"}, 400

class FileListResource(Resource):

    def get(self):
        """
        Информация по всем файлам

        Для получения полного списка файлов используйте 
        пагинацию с помощью **per_page** и **page**.  
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """
        try:
            data = request.args
            page = int(data.get('page', 1))
            per_page = int(data.get('per_page', 100))

            query = FileInfo.query

            paginated_files = query.paginate(page=page, per_page=per_page, error_out=False)
            file_amount = paginated_files.total  # Общее количество файлов
            total_size = sum(file.size for file in paginated_files.items)

            file_list = []
            for file in paginated_files.items:
                file_data = {
                    "id": file.id,
                    "name": file.name,
                    "extension": file.extension,
                    "path_file": file.path_file,
                    "size": file.size,
                    "date_create": file.date_create.isoformat(),
                    "date_change": file.date_change.isoformat() if file.date_change else None,
                    "comment": file.comment,
                }
                file_list.append(file_data)
            response = {
                "file_amount": file_amount,
                "total_size": total_size,
                "current_page": paginated_files.page,
                "total_pages": paginated_files.pages,
                "per_page": per_page,
                "has_next": paginated_files.has_next,
                "has_prev": paginated_files.has_prev,
                "files": file_list
            }
            return response, 200
        except Exception as e:
            return {"message": str(e)}, 500


class FileListInFolder(Resource):
    def post(self):
        """
        Информация по файлам из введенной папки

        Для получения полного списка файлов используйте 
        пагинацию с помощью **per_page** и **page**.  
        **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
        **page** - номер страницы (по умолчанию 1)
        """
        try:
            data = request.get_json()

                # Извлекаем название папки и параметры пагинации
            directory_name = data.get('directory_name')
            page = data.get('page', 1)
            per_page = data.get('per_page', 100)
            if not directory_name:
                return {"message": "directory_name is required"}, 400
                
                # Извлекаем все записи из базы данных, которые соответствуют указанной папке
            query = FileInfo.query.filter(FileInfo.path_file.like(f"%{directory_name}%"))
                
                # Пагинация
            paginated_files = query.paginate(page=page, per_page=per_page, error_out=False)
                
                # Подсчитываем количество файлов и общую сумму размеров
            file_amount = paginated_files.total  # Общее количество файлов
            total_size = sum(file.size for file in paginated_files.items)

                # Формируем список файлов с их метаданными
            file_list = []
            for file in paginated_files.items:
                    file_data = {
                        "id": file.id,
                        "name": file.name,
                        "extension": file.extension,
                        "path_file": file.path_file,
                        "size": file.size,
                        "date_create": file.date_create.isoformat(),
                        "date_change": file.date_change.isoformat() if file.date_change else None,
                        "comment": file.comment,
                    }
                    file_list.append(file_data)

                # Формируем финальный ответ
            response = {
                    "file_amount": file_amount,
                    "total_size": total_size,
                    "current_page": paginated_files.page,
                    "total_pages": paginated_files.pages,
                    "per_page": per_page,
                    "has_next": paginated_files.has_next,
                    "has_prev": paginated_files.has_prev,
                    "files": file_list
                
                }
            return response, 200
        except Exception as e:
            return {"message": f"{e}"}, 400


class FileData(Resource):
    def get(self, file_id):
        """Информация по одному файлу"""
        try:
            if not file_id:
                return {"message": "file_id is required"}, 400

            file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            if not file:
                return {"message": "File not found."}, 404
            file_data = {
                    "id": file.id,
                    "name": file.name,
                    "extension": file.extension,
                    "path_file": file.path_file,
                    "size": file.size,
                    "date_create": file.date_create.isoformat(),
                    "date_change": file.date_change.isoformat() if file.date_change else None,
                    "comment": file.comment,
            }
            return file_data, 200
        except Exception as e:
            return {"message": str(e)}, 500


class DownloadFile(Resource):
    def get(self, file_id):
        """
        Скачать файл
        Скачать файл введя его id
        """
        try:
            if not file_id:
                return {"message": "file_id is required"}, 400
            file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            if not file:
                return {"message": "File not found."}, 404
            file_path = f'{file.path_file}/{file.name}{file.extension}'
            if not os.path.isfile(file_path):
                abort(404, description="File not found on server")
        
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return {"message": str(e)}, 500


class UploadFile(Resource):
    def post(self):
        """
        Загрузить файл в базу данных
        
        Загружает файл в файловую ситему и базу данных.  
        **upload_path** - путь до папки, в которую нужно загрузить файл.
        По умолчанию загружается в /home/orbis-service/Downloads/
        """
        upload_path = request.form.get('upload_path')
        file = request.files.getlist('')[0] if '' in request.files else None
        if file is None or file.filename == '':
            return {"error": "No selected file"}, 400

        if not upload_path:
            upload_path = '/home/orbis-service/Downloads/'
        file_path = os.path.join(upload_path, file.filename)
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file.save(file_path)

        path = Path(file_path)
        file_name = path.stem
        file_extension = path.suffix
        file_size = round(
                os.path.getsize(path) / 1024, 2
        )
        try:
            if (
                not FileInfo.query.filter(
                        FileInfo.name == file_name,
                        FileInfo.size == file_size,
                        FileInfo.extension == file_extension,
                        FileInfo.path_file == upload_path
                                          ).first()
            ):
                new_file_info = FileInfo(
                    name=str(file_name),
                    extension=str(file_extension),
                    path_file=upload_path,
                    size=file_size,
                )
                db.session.add(new_file_info)
                db.session.commit()
                return {"message": "File info saved successfully!"}, 200
            else:
                return {"error": "Файл уже существет"}, 400            
        except Exception as e:
            return {"error": str(e)}, 500


class DeleteFile(Resource):
    def delete(self, file_id):
        """
        Удаляет файл из базы данных и из файловой системы.
        """
        if not file_id:
            return {"message": "file_id is required"}, 400
        file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
        if not file:
            return {"message": "File not found."}, 404
        file_path = f'{file.path_file}/{file.name}{file.extension}'
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


class UpdateFileInfo(Resource):

    def patch(self):
        """Обновляет информацию о файле"""
        try:
            data = request.get_json()
            file_id = data.get('file_id')
            new_name = data.get('new_name')
            new_path_file = data.get('new_path_file')
            new_comment = data.get('new_comment')
            file_obj = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            if file_obj is None:
                return {"message": "File not found."}, 404

            old_file_path = f"{file_obj.path_file}/{file_obj.name}{file_obj.extension}"
            update_name = file_obj.name
            update_path = file_obj.path_file
            update_comment = file_obj.comment
            # Обновляем поля, если есть чем
            if new_name:
                update_name = new_name
            if new_comment:
                update_comment = new_comment
            if new_path_file:
                update_path = new_path_file

            file_obj.name = update_name
            file_obj.path_file = update_path
            file_obj.comment = update_comment
            if update_name == new_name or update_path == new_path_file:
                file_obj.date_change = datetime.now()  # Обновляем дату изменения
            # Сохраняем изменения в базе данных
            db.session.commit()
            # Путь к новому файлу
            new_file_path = f"{file_obj.path_file}/{file_obj.name}{file_obj.extension}"
            # Переименовываем или перемещаем файл в файловой системе
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)  # Перемещаем файл
            else:
                return {"message": " Old file not found."}, 404
            file_data = {
                "id": file_obj.id,
                "name": file_obj.name,
                "extension": file_obj.extension,
                "path_file": file_obj.path_file,
                "size": file_obj.size,
                "date_create": file_obj.date_create.isoformat(),
                "date_change": file_obj.date_change.isoformat() if file_obj.date_change else None,
                "comment": file_obj.comment,
            }
            return file_data, 200
        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(FileSync, '/api/sync')
api.add_resource(FileListResource, '/api/files')
api.add_resource(FileListInFolder, '/api/files_in_folder')
api.add_resource(FileData, '/api/file/<int:file_id>')
api.add_resource(DownloadFile, '/api/file/<int:file_id>/download')
api.add_resource(UploadFile, '/api/upload')
api.add_resource(DeleteFile, '/api/file/<int:file_id>/del')
api.add_resource(UpdateFileInfo, '/api/file/update')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
