from flask import request

from injectors.injectors import SyncFileWithDb
from models.models import app
from services.services import MainResponse


@app.route("/api/sync", methods=["GET"])
def sync_files():
    sync = SyncFileWithDb()
    response = MainResponse(sync).sync_files()
    return response


@app.route("/api/files", methods=["GET"])
def get_files_info():
    data = request.args.to_dict()
    main_data = MainResponse(**data)
    response = main_data.get_files_info()
    return response


@app.route("/api/files_in_folder", methods=["POST"])
def files_in_folder():
    data = request.get_json()
    main_data = MainResponse(**data)
    response = main_data.files_in_folder()
    return response


@app.route("/api/file/<int:file_id>", methods=["GET"])
def get_one_file_info(file_id):
    main_data = MainResponse(file_id=file_id)
    file_data = main_data.one_file_info()
    return file_data


@app.route("/api/file/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    main_data = MainResponse(file_id=file_id)
    file_data = main_data.get_download_file()
    return file_data


@app.route("/api/upload", methods=["POST"])
def upload_file():
    upload_path = request.form.get("upload_path")
    file_obj = request.files.getlist("")[0] if "" in request.files else None
    main_data = MainResponse(upload_path=upload_path, file_obj=file_obj)
    response = main_data.upload_file()
    return response


@app.route("/api/file/<int:file_id>/del", methods=["DELETE"])
def delete_file(file_id):
    main_data = MainResponse(file_id=file_id)
    file_data = main_data.delete_file()
    return file_data


@app.route("/api/file/update", methods=["PUT"])
def put_update_file():
    data = request.get_json()
    main_data = MainResponse(**data)
    file_data = main_data.update_file()
    return (file_data,)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
