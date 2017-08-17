from nlp import app, api
import matplotlib.pyplot as plt
from flask import request, make_response
from flask.views import MethodView

from io import BytesIO
import random
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter


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

        ax = fig.add_subplot(111)
        x = []
        y = []
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        for i in range(10):
            x.append(now)
            now += delta
            y.append(random.randint(0, 1000))
        ax.plot_date(x, y, '-')
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

        return self.make_image(fig)

#app.add_url_rule('/img/', view_func=ImageAPI.as_view('img'))