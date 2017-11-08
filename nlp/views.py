from flask import Flask, redirect, url_for, render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app, api
import os, sys, logging
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
from gensim.models.word2vec import Word2Vec
from sklearn.manifold import TSNE
import re

# NLTK
import nltk

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

###################################################################################


def get_stopwords(stopword_file):
    with open(stopword_file, 'r') as inpFile:
        lines = inpFile.readlines()
        stop_words_temp = map(lambda x: re.sub('\n', '', x), lines)
        stop_words = list(map(lambda x: re.sub('[^A-Za-z0-9]+', '', x), stop_words_temp))

    return stop_words


def clean(stop_words, word):
    word = word.strip()
    word = word.lower()
    word = re.sub('[^A-Za-z0-9]+', '', word)
    if(word not in stop_words):
        return word
    else:
        return ''


def get_sentences(file):
    sentences = []

    with open("./nlp/tmp/" + file) as f:
        content = f.readlines()
        sentences.append(content)


    """for line in file:
        if line is not None or line != '\n':
            words = line.split()
            words = map(lambda x: clean(stopwords, x), words)
            words = list(filter(lambda x: True if len(x) > 0 else False, words))
            sentences.append(words)"""

    return sentences


# List of words that should be ignored by the API
stopword_file = os.path.join(SITE_ROOT, 'data', 'long_stopwords.txt')

stopwords = get_stopwords(stopword_file)

###################################################################################


def tokenise(to_tokenise, remove_stopwords=False):
    path = os.path.join(SITE_ROOT, 'tmp', to_tokenise)

    f = open(path, 'rU').read()

    tokens = nltk.word_tokenize(f)

    if not remove_stopwords:
        # Now to remove all the stop words
        sentences = get_sentences(to_tokenise)
        return sentences
    else:
        return tokens


def get_word_freq(word, sentences):
    freq1 = nltk.FreqDist(sentences)
    return (freq1[word] / len(sentences)) * 100

def retrieve_uni_corpus(uni):
    path = os.path.join(SITE_ROOT, 'tmp', uni)

    f = open(path, 'rU').read()

    #tokens = nltk.word_tokenize(f)

    return f

###################################################################################
# Simple pages

@app.route('/')
def index_page():
    path = os.path.join(SITE_ROOT, 'tmp')

    files = os.listdir(path) # Somewhere, I need to open the file

    return render_template('index.html', files=files)


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')


###################################################################################
# Model stuff

# None of this is done at all
def make_word2vec_model(filename):
    #corpus = retrieve_uni_corpus(filename)

    sentences = get_sentences(filename)

    # Make a Word2Vec model
    model = Word2Vec(list(sentences), size=100, window=5, min_count=1, workers=4)

    # Save the model
    model.wv.save_word2vec_format("./nlp/models/model_" + filename, binary=True)

    logging.warning(sentences)

###################################################################################
# File Upload

ALLOWED_EXTENSIONS = set(['txt', 'csv'])
UPLOAD_FOLDER = '/tmp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if('file' not in request.files):
        #flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if(file.filename == ''):
        #flash('No selected file')
        return redirect(request.url)
    if(file and allowed_file(file.filename)):
        filename = secure_filename(file.filename)
        # Save the raw file to the tmp directory
        file.save(os.path.join(SITE_ROOT, 'tmp', filename))

        make_word2vec_model(filename)

        return redirect(url_for('index_page'))

###################################################################################
# API Namespace

ns = Namespace('api', description='API Operations')

@ns.route('/upload_files')
class ShowUploadedFiles(Resource):
    def get(self):
        logging.warning("See this message in Flask Debug Toolbar!")
        path = os.path.join(SITE_ROOT, 'tmp')

        files = os.listdir(path)

        return {"universities": files}


### API Routes ###

@ns.route('/relfreq/<string:uni>/<string:word>')
# Descriptions of the variables
@ns.param('uni', 'University')
@ns.param('word', 'Word to check against Frequency')
class RelativeFrequency(Resource):
    def get(self, uni, word):
        logging.warning("See this message in Flask Debug Toolbar!")
        if(word not in stopwords):
            corpus = retrieve_uni_corpus(uni)
            tokenised_uni = tokenise(corpus)
            return {word: get_word_freq(word, tokenised_uni), "corpus": str(uni)}
        else:
            return {word: "Word is in the list of ignored words", "corpus": str(uni)}


@ns.route('/universities')
class Universities(Resource):
    def get(self):
        logging.warning("See this message in Flask Debug Toolbar!")
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)


@ns.route('/similarity/<string:uni>/<string:word>')
class WordSimilarities(Resource):
    def get(self, uni, word):
        logging.warning("See this message in Flask Debug Toolbar!")

        path = os.path.join(SITE_ROOT, 'models', "model_" + uni)
        model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True, unicode_errors='ignore')

        most_similar = model.most_similar(positive=[word])

        return {word: most_similar}


api.add_namespace(ns)
