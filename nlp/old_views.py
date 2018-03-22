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
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize

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
    word = re.sub('[^A-Za-z0-9]+', '', word.strip().lower())
    if(word not in stop_words):
        return word
    else:
        return ''


def get_sentences(file):
    sentences = []

    with open("./nlp/models/model_" + file, 'r', encoding="utf-8") as inpFile:
        x = inpFile.readlines()
        for line in x:
            if line is not None or line != '\n':
                words = line.split()
                words = map(lambda x: clean(stopwords, x), words)
                words = list(filter(lambda x: True if len(x) > 0 else False, words))
                sentences.append(words)

    return sentences


# List of words that should be ignored by the API
stopword_file = os.path.join(SITE_ROOT, 'data', 'long_stopwords.txt')

stopwords = get_stopwords(stopword_file)

###################################################################################

"""
to_tokenise: must be a file
"""
def tokenise(to_tokenise, remove_stopwords=False):
    f = retrieve_uni_corpus(to_tokenise)

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

    f = open(path, 'r', encoding="utf8").read().strip()

    return f

###################################################################################
# Gensim functions

def get_saved_model(filename):
    path = os.path.join(SITE_ROOT, 'models', "model_" + filename)
    model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=False, unicode_errors='ignore')


###################################################################################
# Simple pages

@app.route('/')
def index_page():
    path = os.path.join(SITE_ROOT, 'tmp')

    files = os.listdir(path) # Somewhere, I need to open the file

    return render_template('index.html', files=files)

    return model


def get_most_similar(filename, word):
    # Get the model:
    model = get_saved_model(filename)

    logging.warning(model.wv.most_similar(positive=[word]))

    # Find the most similar:
    return model.wv.most_similar(positive=[word])


def similarity_between_words(model, first_word, second_word):
    return model.wv.similarity(first_word, second_word)




@app.route('/index')
def new_index():
    path = os.path.join(SITE_ROOT, 'tmp')

    files = os.listdir(path) # Somewhere, I need to open the file

    return render_template('index.html', files=files)

def add_to_data(to_add):
    return to_add if not None else ""

#@app.route('/report')
@app.route('/report', methods=['POST'])
def report_page():
    """# Check if any universities have been selected:
    unis = [request.form['uni1'], request.form['uni2']]

    most_common = []
    word_similarities = []
    similarities_two = []

    # Remove all None types
    unis = [x for x in unis if x is not None]

    # Check if unis is a list of None:
    if len(unis) == 0:
        return render_template('index.html')

    for uni in unis:
        # Check if models exist first
        if not os.path.isfile("./nlp/models/model_" + uni):
            # Make the model
            make_word2vec_model(uni)

    # Need to use a single loop
    for uni in unis:

        # Needs to check first
        if request.form['word-sim-1']:
            if request.form['most-similar']:
                set_list = [uni, get_most_similar(uni, request.form['word-sim-1'])]
                word_similarities.append(set(set_list))

            if request.form['show-wf']:
                pass

        if request.form['word-sim-2']:
            model = get_saved_model(uni)
            set_list = [uni, similarity_between_words(model, request.form['word-sim-1'], request.form['word-sim-2'])]
            similarities_two.append(set(set_list))

        # Check if top 50 is checked:
        if request.form['top-50-words']:
            tokens = tokenise(uni, remove_stopwords=True)
            word_counter = Counter([w.lower() for w in tokens if w not in stopwords])

            most_common.append(set([uni, word_counter.most_common(50)]))

        if request.form['tsne-visualisation']:
            pass"""

    # Works but makes weird characters appear
    #data = json.dumps(data)
    #data = json.dumps(data, sort_keys=False)
    #data = jsonify(data)

    data = request.form

    # add in all unis
    unis = []
    unis.append(data["uni-1"] if "uni-1" in data else None)
    unis.append(data["uni-2"] if "uni-2" in data else None)

    # Remove all None types
    unis = [x for x in unis if x is not None]
    # Remove all blanks
    unis = [x for x in unis if x is not '']

    most_common = []
    word_similarities = []
    similarities_two = []

    # Check if unis is a list of None:
    if len(unis) == 0:
        return redirect("/index")

    for uni in unis:
        # Check if models exist first
        if not os.path.isfile("./nlp/models/model_" + uni):
            # Make the model if it doesn't exist
            make_word2vec_model(uni)

    # Need to use a single loop
    for uni in unis:
        # Needs to check first
        if 'single-word-sim' in data:
            if 'most-similar' in data:
                set_list = [uni, get_most_similar(uni, data['single-word-sim'])]
                logging.warning("### SET LIST ###")
                logging.warning(set_list)
                word_similarities.append(set_list)

                """if 'show-wf' in data:
        pass

if 'multiple-word-sim' in data:
    model = get_saved_model(uni)
    set_list = [uni, similarity_between_words(model, data['word-sim-1'], data['word-sim-2'])]
    similarities_two.append(set_list)

# Check if top 50 is checked:
if 'top-50-words' in data:
    tokens = tokenise(uni, remove_stopwords=True)
    word_counter = Counter([w.lower() for w in tokens if w not in stopwords])
    #logging.warning(word_counter.most_common(50))
    most_common.append(set([uni, word_counter.most_common(50)]))

if 'tsne-visualisation' in data:
    pass"""

    data = {
        "unis": unis,
        "word-similarities": word_similarities,
        "most-common": most_common,
        "similarities-two": similarities_two
    }
    logging.warning(word_similarities)

    # Why am I making this a JSON object? Just pass the stuff through
    value = {
        "unis": unis,
        "word-similarities": [
            {"recite": 0.56}
        ]
    }

    #logging.warning(data)

    #logging.warning(json.dumps(word_similarities))

    return render_template('report.html', json=json.dumps(value))


@app.route('/loading', methods=['POST'])
def loading_page():
    # Here, make the JSON payload to send off to the report page

    #value = json.dumps(data)
    value = "test"

    # Make this work somehow
    return render_template('loading_screen.html', json=value)


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')


###################################################################################
# Model stuff

def make_word2vec_model(filename):
    sentences = []

    with open("./nlp/tmp/" + filename, 'r', encoding="utf-8", errors='ignore') as inpFile:
        x = inpFile.readlines()
        for line in x:
            if line is not None or line != '\n':
                words = line.split()
                words = map(lambda x: clean(stopwords, x), words)
                words = list(filter(lambda x: True if len(x) > 0 else False, words))
                sentences.append(words)

    # Make a Word2Vec model
    model = Word2Vec(list(sentences), size=100, window=5, min_count=1, workers=4, hs=1, negative=0)

    # Save the model
    model.wv.save_word2vec_format("./nlp/models/model_" + filename, binary=False)


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

        logging.warning("making model")

        # Make the model at the loading screen
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
        #logging.warning("See this message in Flask Debug Toolbar!")
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)


@ns.route('/similarity/<string:uni>/<string:word>')
class WordSimilarities(Resource):
    def get(self, uni, word):
        #logging.warning("See this message in Flask Debug Toolbar!")

        path = os.path.join(SITE_ROOT, 'models', "model_" + uni)
        model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=False, unicode_errors='ignore')

        most_similar = model.most_similar(positive=[word])

        return {word: most_similar}


api.add_namespace(ns)
