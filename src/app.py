import flask

import routers
from injectors.connections import pg


def setup_app():
    current = flask.Flask(__name__)
    pg.setup(current)

    return current


app = setup_app()

app.register_blueprint(routers.file_router)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# Traceback (most recent call last):
# File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1511, in wsgi_app
#   response = self.full_dispatch_request()
# File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 919, in full_dispatch_request
#   rv = self.handle_user_exception(e)
# File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 917, in full_dispatch_request
#   rv = self.dispatch_request()
# File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 902, in dispatch_request
#   return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
# File "/src/./routers/routers.py", line 11, in sync_files
#   sync = sync_injector()
# File "/src/./injectors/services.py", line 7, in sync_injector
#   return SyncFileWithDb(pg_connection=connections.pg.acquire_session())
# File "/src/./injectors/pg.py", line 57, in acquire_session
#   return ConnectionsException.acquire_error()
# Traceback (most recent call last):
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1511, in wsgi_app
#     response = self.full_dispatch_request()
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 919, in full_dispatch_request
#     rv = self.handle_user_exception(e)
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 917, in full_dispatch_request
#     rv = self.dispatch_request()
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 902, in dispatch_request
#     return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
#   File "/src/./routers/routers.py", line 11, in sync_files
#     sync = sync_injector()
#   File "/src/./injectors/services.py", line 7, in sync_injector
#     return SyncFileWithDb(pg_connection=connections.pg.acquire_session())
#   File "/src/./injectors/pg.py", line 57, in acquire_session
#     return ConnectionsException.acquire_error()
#   File "/src/./injectors/pg.py", line 20, in acquire_error
#     injectors.pg.ConnectionsException:

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1103, in emit
#     stream.write(msg + self.terminator)
# UnicodeEncodeError: 'ascii' codec can't encode characters in position 1110-1115: ordinal not in range(128)

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1536, in __call__
#     return self.wsgi_app(environ, start_response)
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1514, in wsgi_app
#     response = self.handle_exception(e)
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 854, in handle_exception
#     self.log_exception(exc_info)
#   File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 875, in log_exception
#     self.logger.error(
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1506, in error
#     self._log(ERROR, msg, args, **kwargs)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1624, in _log
#     self.handle(record)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1634, in handle
#     self.callHandlers(record)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1696, in callHandlers
#     hdlr.handle(record)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 968, in handle
#     self.emit(record)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1108, in emit
#     self.handleError(record)
#   File "/usr/local/lib/python3.10/logging/__init__.py", line 1022, in handleError
#     traceback.print_exception(t, v, tb, None, sys.stderr)
#   File "/usr/local/lib/python3.10/traceback.py", line 121, in print_exception
#     print(line, file=file, end="")
# UnicodeEncodeError: 'ascii' codec can't encode characters in position 74-79: ordinal not in range(128)
