import flask
from flask import jsonify, request

from injectors.injectors import file_injector, sync_injector

tasks_routers = flask.Blueprint("tasks", __name__, url_prefix="/api/")


@tasks_routers.route("/sync", methods=["GET"])
def sync_files():
    sync = sync_injector()
    response = sync.sync_files()
    return jsonify(response)


@tasks_routers.route("/files", methods=["GET"])
def get_files_info():
    main_data = file_injector()
    response = main_data.get_files_info(**request.args.to_dict())
    return jsonify(response)


@tasks_routers.route("/files_in_folder", methods=["POST"])
def files_in_folder():
    main_data = file_injector()
    response = main_data.files_in_folder(**request.get_json())
    return jsonify(response)


@tasks_routers.route("/file/<int:file_id>", methods=["GET"])
def get_one_file_info(file_id):
    main_data = file_injector()
    response = main_data.one_file_info(file_id=file_id)
    return jsonify(response)


@tasks_routers.route("/file/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    main_data = file_injector()
    response = main_data.get_download_file(file_id=file_id)
    return jsonify(response)


@tasks_routers.route("/upload", methods=["POST"])
def upload_file():
    upload_path = request.form.get("upload_path")
    file_obj = request.files.getlist("")[0] if "" in request.files else None
    main_data = file_injector()
    response = main_data.upload_file(upload_path=upload_path, file_obj=file_obj)
    return jsonify(response)


@tasks_routers.route("/file/<int:file_id>/del", methods=["DELETE"])
def delete_file(file_id):
    main_data = file_injector()
    response = main_data.delete_file(file_id=file_id)
    return jsonify(response)


@tasks_routers.route("/file/update", methods=["PUT"])
def put_update_file():
    main_data = file_injector()
    response = main_data.update_file(**request.get_json())
    return jsonify(response)
