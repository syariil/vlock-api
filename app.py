from flask import Flask
from resources.location import loc
from resources.users import us
from resources.favorite import fav
from resources.predict import pre
from flask_bcrypt import Bcrypt

bcript = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "VLOC REST API"
    app.config["API_VERSION"] = "v1.0.0"
    bcript.init_app(app)
    return app


app = create_app()


app.register_blueprint(loc)
app.register_blueprint(us)
app.register_blueprint(fav)
app.register_blueprint(pre)


@app.route("/")
def index():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
