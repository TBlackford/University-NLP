from flask import Flask, render_template
from flask_restplus import Api as BaseApi
import os

webapp = Flask(__name__) # create the application instance

# Double check that this is indeed working with BLAS.

# Hacky way around the '/' not working.
class Api(BaseApi):

    def _register_doc(self, app_or_blueprint):
        # HINT: This is just a copy of the original implementation with the last line commented out.
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        #app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)

    @property
    def base_path(self):
        return ''


# Create the API instance using the above class
api = Api(
    webapp,
    title='University NLP',
    version='1.0',
    doc='/api/docs/',
)

# load config from this file , __init__.py
webapp.config.from_object(__name__)

# Load default config and override config from an environment variable
webapp.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

webapp.config.from_envvar('NLP_SETTINGS', silent=True)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

if __name__ == '__main__':
    webapp.run(debug=True, use_reloader=False, threaded=True)
