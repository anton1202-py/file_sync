import os
from models import FileInfo, app, db
from flask import request, send_file, abort
from flask_restx import Api

from integrations import SyncFileWithDb
from views import MainResponse

api = Api(app, version='1.0', title='File API',
             description='Работа с файлами и сохранением их в базу данных',
             )


@app.route('/api/sync', methods=['GET'])
def sync_files():
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
        main_data = MainResponse()
        data = request.get_json()
        directory_name = data.get('directory_name')
        if not directory_name:
            return {"message": "directory_name is required"}, 400
        sync.sync_local_storage_with_db(directory_name)
        query = FileInfo.query.filter(FileInfo.path_file.like(f"%{directory_name}%"))  
        response = main_data.create_answer_for_request(data, query)
        return response, 200
    except Exception as e:
        return {"message": f"{e}"}, 400


@app.route('/api/files', methods=['GET'])
def get_files_info():
    """
    Информация по всем файлам

    Для получения полного списка файлов используйте 
    пагинацию с помощью **per_page** и **page**.  
    **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
    **page** - номер страницы (по умолчанию 1)
    """
    try:
        main_data = MainResponse()
        data = request.args
        query = FileInfo.query
        response = main_data.create_answer_for_request(data, query)
        return response
    except Exception as e:
        return {"message": str(e)}


@app.route('/api/files_in_folder', methods=['POST'])
def files_in_folder():
    """
    Информация по файлам из введенной папки

    Для получения полного списка файлов используйте 
    пагинацию с помощью **per_page** и **page**.  
    **per_page** - число строк, выдаваемое на странице (по умолчанию 100)
    **page** - номер страницы (по умолчанию 1)
    """
    try:
        main_data = MainResponse()
        data = request.get_json()
        directory_name = data.get('directory_name')
        if not directory_name:
            return {"message": "directory_name is required"}, 400
        query = FileInfo.query.filter(FileInfo.path_file.like(f"%{directory_name}%"))
        response = main_data.create_answer_for_request(data, query)
        return response, 200
    except Exception as e:
        return {"message": f"{e}"}, 400


@app.route('/api/file/<int:file_id>', methods=['GET'])
def get_one_file_info(file_id):
    """Информация по одному файлу"""
    try:
        if not file_id:
            return {"message": "file_id is required"}, 400
        file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
        if not file:
            return {"message": "File not found."}, 404
        main_data = MainResponse()
        file_data = main_data.one_file_info(file)
        return file_data, 200
    except Exception as e:
        return {"message": str(e)}, 500
    

@app.route('/api/file/<int:file_id>/download', methods=['GET'])
def get_download_file(file_id):
    """Скачать файл по ID"""
    try:
        if not file_id:
            return {"message": "file_id is required"}, 400
        file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
        if not file:
            return {"message": "File not found."}, 404
        file_path = os.path.join(file.path_file, file.name + file.extension)
        if not os.path.isfile(file_path):
            abort(404, description="File not found on server")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return {"message": str(e)}, 500


@app.route('/api/upload', methods=['POST'])
def upload_file(self):
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

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        main_data = MainResponse()
        file_name, file_extension, new_file_info = main_data.upload_file(upload_path, file)
        
        try:
            if (not FileInfo.query.filter(FileInfo.name == file_name,
                FileInfo.extension == file_extension, FileInfo.path_file == upload_path).first()):
                db.session.add(new_file_info)
                db.session.commit()
                return {"message": "File info saved successfully!"}, 200
            else:
                return {"error": "Файл уже существет"}, 400            
        except Exception as e:
            return {"error": str(e)}, 500


@app.route('/api/file/<int:file_id>/del', methods=['DELETE'])
def delete_file(self, file_id):
    """Удаляет файл из базы данных и из файловой системы."""
    if not file_id:
        return {"message": "file_id is required"}, 400
    file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
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


@app.route('/api/file/update', methods=['PUT'])
def put_update_file():
    """Обновляет информацию о файле"""
    try:
        data = request.get_json()
        main_data = MainResponse()
        file_data = main_data.update_file(data)
        return file_data, 200
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
