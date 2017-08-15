from .. import app
import matplotlib.pyplot as plt
from flask import request, make_response, jsonify
from flask.views import MethodView

from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageAPI(MethodView):
    """API used for RESTful rendering of matplotlib images"""

    def make_image(self, fig):
        """Turns Figure into a returnable image"""
        canvas = FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        response = make_response(png_output.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response

    def post(self):
        """Returns an image based off of json"""

        # Get the JSON
        content = request.json
        fig = Figure()

        return self.make_image(fig)
