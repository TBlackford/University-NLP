from flask import Flask, redirect, url_for, render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app, api
import os
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

    with open(file, 'r') as inpFile:
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

# I feel like I should save this to disk
class UniModel:

    # Includes stopwords
    tokens = []

    # Excludes stopwords
    sentences = []

    def __init__(self, file=""):
        if(file != ""):
            self.tokenise(file)

    def tokenise(self, to_tokenise):
        path = os.path.join(SITE_ROOT, 'tmp', to_tokenise)

        f = open(path, 'rU').read()

        self.tokens = nltk.word_tokenize(f)

        # Now to remove all the stop words
        self.sentences = get_sentences(to_tokenise)


    def get_word_freq(self, word, remove_stopwords=False):
        if(remove_stopwords):
            freq1 = nltk.FreqDist(self.sentences)
            return (freq1[word] / len(self.sentences)) * 100
        else:
            freq1 = nltk.FreqDist(self.tokens)
            return (freq1[word] / len(self.tokens)) * 100


def make_uni_model(key, corpus):
    uni_models[key] = UniModel(corpus)

# Dictionary to hold the uni text file key and the uni model for faster processing
uni_models = {}

def retrieve_uni_corpus(uni):
    path = os.path.join(SITE_ROOT, 'tmp', uni)

    f = open(path, 'rU').read()

    tokens = nltk.word_tokenize(f)

    return tokens

###################################################################################

@app.route('/')
def index_page():
    path = os.path.join(SITE_ROOT, 'tmp')

    files = os.listdir(path) # Somewhere, I need to open the file

    return render_template('index.html', files=files)


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')


###################################################################################

ns = Namespace('api', description='API Operations')

### File Upload ###

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
        file.save(os.path.join(SITE_ROOT, 'tmp', filename))
        return redirect(url_for('index_page'))


@ns.route('/upload_files')
class ShowUploadedFiles(Resource):
    def get(self):
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
        if(word not in stopwords):
            tokenised_uni = retrieve_uni_corpus(uni)
            freq1 = nltk.FreqDist(tokenised_uni)
            return {word: (freq1[word] / len(tokenised_uni)) * 100, "corpus": str(uni)}
        else:
            return {word: "Word is in the list of ignored words", "corpus": str(uni)}


@ns.route('/universities')
class Universities(Resource):
    def get(self):
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)


@ns.route('/similarity/<int:uni>/<string:word>')
class WordSimilarities(Resource):
    def get(self, uni, word):
        sentences = get_sentences(retrieve_uni_corpus(uni), stopwords)

        model = Word2Vec(sentences, window=10, size=100, workers=4, min_count=5, hs=1, negative=0)

        most_similar = model.most_similar(positive=[word])

        return {word: most_similar}


api.add_namespace(ns)
