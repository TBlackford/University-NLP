from flask import Flask, flash, redirect, url_for, render_template, make_response, request, send_file, json
from flask_restplus import Resource, Namespace
from nlp import app, api, models
from nlp.model_functions import *
import os, sys, logging
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
    path = os.path.join(app.SITE_ROOT, 'tmp')

    files = os.listdir(path) # Somewhere, I need to open the file

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
            logging.warning(data)

            # Get the most similar words
            _do_check(_most_similar, ['most-similar'])

            # Check the similarity between two words
            _do_check(_similarity, ['similar-word-1', 'similar-word-2'])

            # Get top 50 words info
            _do_check(_top_50_words, ['top-50-words'])


    return render_template('report.html', payload=payload)


@app.webapp.route('/upload', methods=['POST'])
def upload_page():
    ALLOWED_EXTENSIONS = set(['txt', 'csv'])
    UPLOAD_FOLDER = '/tmp/'
    app.webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # check if the post request has the file part
    if 'file' not in request.files:
        # flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save the raw file to the tmp directory
        file.save(os.path.join(app.SITE_ROOT, 'tmp', filename))

        logging.warning("making model")

        models.Word2VecModel(filename)

        return redirect(url_for('index_page'))


@app.webapp.route('/universities')
def show_uni_list():
    return render_template('university_list.html')
