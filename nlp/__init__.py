"""app = Flask(__name__) # create the application instance
api = Api(app)
app.config.from_object(__name__) # load config from this file , __init__.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('NLP_SETTINGS', silent=True)

from .views import *

if __name__ == '__main__':
    app.run(debug=True)"""


from .app import app, api
from .views import *
