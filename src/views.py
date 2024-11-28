from datetime import datetime
import os
from pathlib import Path
from models import db, FileInfo
from flask_restful import Resource


class MainResponse(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def create_answer_for_request(self, data, query):
        """Создает ответ для АПИ"""
        page = data.get('page', 1)
        per_page = data.get('per_page', 100)
        paginated_files = query.paginate(page=page, per_page=per_page, error_out=False)
        
        file_amount = paginated_files.total 
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
            "has_next": paginated_files.has_next,
            "has_prev": paginated_files.has_prev,
            "per_page": per_page,
            "files": file_list 
        }
        return response

    def one_file_info(self, file):
        """Информация по одному файлу"""
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
        return file_data

    def upload_file(self, upload_path, file):
        """
        Загрузить файл в базу данных
        """
        
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
        new_file_info = FileInfo(
            name=str(file_name),
            extension=str(file_extension),
            path_file=upload_path,
            size=file_size,
        )     
        return file_name, file_extension, new_file_info


    def update_file(self, data):
        """Обновляет информацию о файле"""
        try:
            file_id = data.get('file_id')
            new_name = data.get('new_name')
            new_path_file = data.get('new_path_file')
            new_comment = data.get('new_comment')
            file_obj = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            if file_obj is None:
                return {"message": "File not found."}

            old_file_path = os.path.join(file_obj.path_file, file_obj.name + file_obj.extension)
            update_name = file_obj.name
            update_path = file_obj.path_file
            update_comment = file_obj.comment
    
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
                file_obj.date_change = datetime.now()
            db.session.commit()
            new_file_path = os.path.join(file_obj.path_file, file_obj.name + file_obj.extension)

            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
            else:
                return {"message": " Old file not found."}
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
            return file_data
        except Exception as e:
            return {"error": str(e)}