from flask import Flask

app = Flask(__name__)
app.debug = True

import config
app.config.from_object(config)


def connect_db():
    import pymysql
    return pymysql.connect(host=app.config['MYSQL_DATABASE_HOST'],
                           user=app.config['MYSQL_DATABASE_USER'], password=app.config['MYSQL_DATABASE_PASSWORD'],
                           database=app.config['MYSQL_DATABASE_DB'], charset='utf8')


@app.before_request
def before_request():
    from flask import g
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    from flask import g
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


import main.blueprint
import manager.blueprint
app.register_blueprint(main.blueprint.blueprint)
app.register_blueprint(manager.blueprint.blueprint)

if __name__ == '__main__':
    app.run()
