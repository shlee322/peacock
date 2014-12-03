from flask import Flask

app = Flask(__name__)

from main import main
app.register_blueprint(main.blueprint)


if __name__ == '__main__':
    app.run()
