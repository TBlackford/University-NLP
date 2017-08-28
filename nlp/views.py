from flask import render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app, api
import os, random
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


# This function doesn't work for some reason
@app.route('/')
def index():
    return render_template('index.html')


# This function does
@app.route('/index')
def show_index():
    return render_template('index.html')


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')

###################################################################################

ns = Namespace('api', description='API Operations')


@ns.route('/universities')
class Universities(Resource):
    def get(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)

    # For updating the JSON -- Maybe not here though?
    def update(self, name, rank, website):
        pass


@ns.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"Hello": "World"}

    def post(self):
        return {"Hello": "World"}


@ns.route('/id/<int:id>')
@ns.param('id', 'ID Thing')
class ID(Resource):
    def get(self, id):
        return {"ID" : id}


ns_img = Namespace('img', "Matplotlib Image Renderer API")


@app.route('/plot.png')
def plot():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]

    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@ns_img.route('/plot')
class ImageAPI(Resource):
    """API used for RESTful rendering of matplotlib images"""

    def get(self):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)

        xs = range(100)
        ys = [random.randint(1, 50) for x in xs]

        axis.plot(xs, ys)
        canvas = FigureCanvas(fig)
        output = BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        return response

    @api.marshal_with(int)
    def post(self, id):
        print(id)
        return self.get(self)


api.add_namespace(ns)
api.add_namespace(ns_img)

