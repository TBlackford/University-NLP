from flask import Flask, flash, redirect, url_for, render_template, make_response, request, send_file, json
from flask_restplus import Resource, Namespace
from nlp import app, api
from nlp.models import *
from nlp.model_functions import *
import os, sys, logging
import datetime
import random
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
from gensim.models.word2vec import Word2Vec

import nltk

###################################################################################
# Simple pages


@app.webapp.route('/')
def index_page():
    files = []

    path = os.path.join(app.SITE_ROOT, './data/data.json')

    with open(path) as json_data:
        d = json.load(json_data)

        unis = d["universities"]

        for uni in unis:
            files.append(uni["rank"] + " - " + uni["name"])

    return render_template('index.html', files=files)


@app.webapp.route('/report', methods=['POST'])
def report_page():
    def _top_50_words():
        most_common = [top50words(unis[0]), top50words(unis[1])]

        payload.update({"top50words": most_common})

    def _most_similar():
        """Gets the most similar word"""
        similar = []
        # Get the text from the first word
        word = data['most-similar']

        if word == '':
            return

        # Bundle the words
        positive = [word]
        negative = []  # TODO
        # Get the similarities
        similar.append(most_similar(unis[0], positive, negative))
        similar.append(most_similar(unis[1], positive, negative))

        payload.update({"most_similar": {"similar": similar, "positive": positive}})

    def _similarity():
        """Judges the similarity between two words"""
        similar = []
        # Get the text from the first word
        first_word = data['similar-word-1']
        second_word = data['similar-word-2']

        if first_word == '' or second_word == '':
            return

        similar.append(similarity(unis[0], first_word, second_word))
        similar.append(similarity(unis[1], first_word, second_word))

        payload.update({"similarity": similar})


    def _tsne():
        words = data['tsne-visualisation']

        words = words.replace(', ', ',').split(',')

        url_string = "?words="

        for word in words:
            url_string += word + "+"

        url_string = url_string[:-1]

        payload.update({"image_string": url_string})

    def _do_check(func, item):
        if all(i in data for i in item):
            func()

    #######################################################

    data = request.form

    # add in all unis
    unis = []
    unis.append(data["uni-1"] if "uni-1" in data else None)
    unis.append(data["uni-2"] if "uni-2" in data else None)

    # Remove all None types
    unis = [x for x in unis if x is not None]
    # Remove all blanks
    unis = [x for x in unis if x is not '']

    payload = {}

    # Check if there is stuff in the uni list
    if unis == []:
        redirect('/')
    else:
        # There's only one university selected
        if len(unis) < 2:
            redirect('/')
        else:

            # Add unis to payload
            payload.update({"universities": unis})

            _do_check(_tsne, ['tsne-visualisation'])

            # Get the most similar words
            _do_check(_most_similar, ['most-similar'])

            # Check the similarity between two words
            _do_check(_similarity, ['similar-word-1', 'similar-word-2'])

            # Get top 50 words info
            _do_check(_top_50_words, ['top-50-words'])


    return render_template('report.html', payload=payload)


@app.webapp.route("/img/tsne/<university>", methods=["GET"])
def tnse_image(university=None):
    words = request.args.get("words")

    if university is not None and words is not None:
        models = make_word2vec_model(university)
        words = words.split(' ')
        tsne_df = models.make_tsne(words)

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(tsne_df['x'], tsne_df['y'])

        for i, txt in enumerate(tsne_df['word']):
            ax.annotate(txt, (tsne_df['x'].iloc[i], tsne_df['y'].iloc[i]))

        canvas=FigureCanvas(fig)
        png_output = io.BytesIO()#
        canvas.print_png(png_output)
        response=make_response(png_output.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response


@app.webapp.route("/simple.png")
def simple_image():
    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    png_output = io.BytesIO()#
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.webapp.route('/universities')
def show_uni_list():
    return render_template('university_list.html')

