import flask
from flask import jsonify, request

from injectors.services import file_injector, sync_injector

file_router = flask.Blueprint("tasks", __name__, url_prefix="/api/")


@file_router.get("/sync")
def sync_files():
    sync = sync_injector()
    response = sync.sync_files()
    return jsonify(response)


@file_router.get("/files")
def get_files_info():
    main_data = file_injector()
    response = main_data.get_files_info()
    return jsonify(response)


@file_router.post("/files_in_folder")
def files_in_folder():
    main_data = file_injector()
    print(request.get_json().get("directory_name", None))
    response = main_data.files_in_folder(
        directory_name=request.get_json().get("directory_name", None)
    )
    return jsonify(response)


@file_router.get("/file/<int:file_id>")
def get_one_file_info(file_id):
    main_data = file_injector()
    response = main_data.one_file_info(file_id=file_id)
    return jsonify(response)


@file_router.get("/file/<int:file_id>/download")
def download_file(file_id):
    main_data = file_injector()
    response = main_data.get_download_file(file_id=file_id)
    return jsonify(response)


@file_router.post("/upload")
def upload_file():
    upload_path = request.form.get("upload_path")
    file_obj = request.files.getlist("")[0] if "" in request.files else None
    main_data = file_injector()
    response = main_data.upload_file(file_obj=file_obj, upload_path=upload_path)
    return jsonify(response)


@file_router.delete("/file/<int:file_id>/del")
def delete_file(file_id):
    main_data = file_injector()
    response = main_data.delete_file(file_id=file_id)
    return jsonify(response)


@file_router.put("/file/update")
def put_update_file():
    main_data = file_injector()
    response = main_data.update_file(
        file_id=request.get_json().get("file_id", None),
        new_name=request.get_json().get("new_name", None),
        new_comment=request.get_json().get("new_comment", None),
        new_path_file=request.get_json().get("new_path_file", None),
    )
    return jsonify(response)
