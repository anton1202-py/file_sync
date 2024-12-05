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
    fi = file_injector()
    response = fi.get_files_info()
    return jsonify(response)


@file_router.post("/files")
def files_in_folder():
    fi = file_injector()
    response = fi.files_in_folder(
        directory_name=request.get_json().get("directory_name", None)
    )
    return jsonify(response)


@file_router.get("/files/<int:file_id>")
def get_one_file_info(file_id):
    fi = file_injector()
    response = fi.one_file_info(file_id=file_id)
    return jsonify(response)


@file_router.get("/files/<int:file_id>/download")
def download_file(file_id):
    fi = file_injector()
    response = fi.get_download_file(file_id=file_id)
    return jsonify(response)


@file_router.post("/upload")
def upload_file():
    upload_path = request.form.get("upload_path")
    file_obj = request.files.getlist("")[0] if "" in request.files else None
    fi = file_injector()
    response = fi.upload_file(file_obj=file_obj, upload_path=upload_path)
    return jsonify(response)


@file_router.delete("/files/<int:file_id>")
def delete_file(file_id):
    fi = file_injector()
    response = fi.delete_file(file_id=file_id)
    return jsonify(response)


@file_router.post("/file/<int:file_id>")
def put_update_file(file_id):
    fi = file_injector()
    response = fi.update_file(
        file_id=file_id,
        new_name=request.get_json().get("new_name", None),
        new_comment=request.get_json().get("new_comment", None),
        new_path_file=request.get_json().get("new_path_file", None),
    )
    return jsonify(response)
