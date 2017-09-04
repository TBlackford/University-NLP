from flask import render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app, api
import os, random
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# NLTK
import nltk
# Removing this will improve performance maybe
from nltk.book import *

# Spacy
import numpy
import spacy.en
from collections import Counter

all_books = [text1, text2, text3, text4, text5, text6, text7, text8, text9]


# This function doesn't work for some reason
@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')


def retrieve_uni_corpus(uni):
    # For now, just get a random NLTK corpus
    #return random.choice(all_books)
    return text1

###################################################################################

ns = Namespace('api', description='API Operations')

@ns.route('/relfreq/<int:uni>/<string:word>')
# Descriptions of the variables
@ns.param('uni', 'University')
@ns.param('word', 'Word to check against Frequency')
class RelativeFrequency(Resource):
    def get(self, uni, word):
        uni = retrieve_uni_corpus(uni)
        freq1 = FreqDist(uni)
        return {word: (freq1[word] / len(uni)) * 100, "corpus": str(uni)}


@ns.route('/wordnet/<int:uni>/<string:word>')
class WordSimilarities(Resource):
    def get(self, uni, word):
        pass


@ns.route('/universities')
class Universities(Resource):
    def get(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)

###################################################################################


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

