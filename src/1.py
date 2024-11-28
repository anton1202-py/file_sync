class MainResponse(Resource):
    def create_answer_for_request(self, data, query):
        response = {
            "file_amount": file_amount,
            "total_size": total_size,
        }
        return response

    def sync_files_with_db(self):
            sync = SyncFileWithDb()
            data = request.get_json()
            directory_name = data.get('directory_name')
            if not directory_name:
                return {"message": "directory_name is required"}, 400 
            response = self.create_answer_for_request(data, query)
            return response, 200

    def files_info(self):
        data = request.args
        query = FileInfo.query
        response = self.create_answer_for_request(data, query)
        return response, 200
      
    def files_in_folder(self):
            data = request.get_json()
            directory_name = data.get('directory_name')
            if not directory_name:
                return {"message": "directory_name is required"}, 400
            query = FileInfo.query.filter(FileInfo.path_file.like(f"%{directory_name}%"))
            response = self.create_answer_for_request(data, query)
            return response, 200

    def one_file_info(self, file_id):
            if not file_id:
                return {"message": "file_id is required"}, 400

            file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            return file_data, 200

    def download_file(self, file_id):
            if not file_id:
                return {"message": "file_id is required"}, 400
            file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
            return send_file(file_path, as_attachment=True)


    def upload_file(self):
        upload_path = request.form.get('upload_path')
        file = request.files.getlist('')[0] if '' in request.files else None
        if file is None or file.filename == '':
            return {"error": "No selected file"}, 400

    def delete_file(self, file_id):
      
        if not file_id:
            return {"message": "file_id is required"}, 400
        file = FileInfo.query.filter(FileInfo.id == int(file_id)).first()
        if not file:
            return {"message": "File not found."}, 404
        file_path = f'{file.path_file}/{file.name}{file.extension}'
        if not os.path.isfile(file_path):
                abort(404, description="File not found on server")

    def update_file(self):
            data = request.get_json()
            file_id = data.get('file_id')
            old_file_path = f"{file_obj.path_file}/{file_obj.name}{file_obj.extension}"
            update_name = file_obj.name
            update_path = file_obj.path_file
            update_comment = file_obj.comment
            return file_data, 200