from discorss_models.base import db_session
from website import create_app


app = create_app()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True)
