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
# Removing this will improve performance maybe
from nltk.book import *

all_books = [text1, text2, text3, text4, text5, text6, text7, text8, text9]

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

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
    if 'file' not in request.files:
        #flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        #flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(SITE_ROOT, 'tmp', filename))
        return redirect(url_for('index_page',
                                filename=filename)) # Change the code here somewhere so the

### API Routes ###

@ns.route('/relfreq/<int:uni>/<string:word>')
# Descriptions of the variables
@ns.param('uni', 'University')
@ns.param('word', 'Word to check against Frequency')
class RelativeFrequency(Resource):
    def get(self, uni, word):
        uni = retrieve_uni_corpus(uni)
        freq1 = FreqDist(uni)
        return {word: (freq1[word] / len(uni)) * 100, "corpus": str(uni)}


@ns.route('/universities')
class Universities(Resource):
    def get(self):
        json_url = os.path.join(SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)


@ns.route('/wordnet/<int:uni>/<string:word>')
class WordSimilarities(Resource):
    def clean(self, stop_words, word):
        word = word.strip()
        word = word.lower()
        word = re.sub('[^A-Za-z0-9]+', '', word)
        if word not in stop_words:
            return word
        else:
            return ''

    def get_sentences(self, file, stopwords):
        line_count = 0
        sentences = []

        with open(file, 'r') as inpFile:
            x = inpFile.readlines()
            for line in x:
                if line is not None or line != '\n':
                    words = line.split()
                    words = map(lambda x: self.clean(stopwords, x), words)
                    words = list(filter(lambda x: True if len(x) > 0 else False, words))
                    sentences.append(words)

        return sentences

    def get_stopwords(self, stopword_file):
        stop_words = []

        with open(stopword_file, 'r') as inpFile:
            lines = inpFile.readlines()
            stop_words_temp = map(lambda x: re.sub('\n', '', x), lines)
            stop_words = list(map(lambda x: re.sub('[^A-Za-z0-9]+', '', x), stop_words_temp))

        return stop_words

    def get(self, uni, word):
        stopword_file = os.path.join(SITE_ROOT, 'data', 'long_stopwords.txt')

        stopwords = self.get_stopwords(stopword_file)

        sentences = self.get_sentences(retrieve_uni_corpus(uni), stopwords)

        model = Word2Vec(sentences, window=10, size=100, workers=4, min_count=5, hs=1, negative=0)

        most_similar = model.most_similar(positive=[word])

        return {word: most_similar}

api.add_namespace(ns)
