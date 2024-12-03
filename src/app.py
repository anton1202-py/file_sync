import flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import routers
from config import config


def setup_app():
    current = flask.Flask(__name__)

    username = config.username
    psw = config.psw
    db_name = config.db_name
    sqlalchemy_database_url = f"postgresql://{username}:{psw}@localhost/{db_name}"

    engine = create_engine(sqlalchemy_database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    return current, session


app, session = setup_app()

app.register_blueprint(routers.tasks_routers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
