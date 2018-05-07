from flask import Flask, redirect, url_for, render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app
import os, sys, logging, pickle, csv
from werkzeug.utils import secure_filename
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
warnings.filterwarnings(action='ignore', category=DeprecationWarning, module='gensim')
import gensim
from gensim.models.word2vec import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import re
import pandas as pd

# NLTK
import nltk
from nltk.corpus import stopwords
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize


###################################################################################
# Generic model


class UniModel:
    # Used to get the corpus sentences
    model_path = "./nlp/models/model_"
    # Used to get the
    nltk_path = "./nlp/tmp/"

    def __init__(self, remove_stopwords=True):
        self.stop_words = []
        self.stopword_file = os.path.join(app.SITE_ROOT, 'data', 'long_stopwords.txt')
        self.sentences = []

        if remove_stopwords:
            self.stop_words = self.make_stopwords()

    def make_stopwords(self):
        with open(self.stopword_file, 'r', encoding="utf-8") as inpFile:
            lines = inpFile.readlines()
            stop_words_temp = None
            try:
                stop_words_temp = map(lambda x: re.sub('\n', '', x), lines)
            except:
                logging.warning("Exception ignored in stopwords")
            return list(stop_words_temp)

    def clean(self, word):
        word = word.strip()
        word = word.lower()
        word = re.sub('[^A-Za-z0-9]+', '', word)
        if word not in self.stop_words:
            return word
        else:
            return ''

    def make_corpus(self, path):
        """
        Creates a list with every sentence in the corpus

        :param path: path to the file

        logging.warning(path)
        with open(path, 'r', encoding="utf-8") as inpFile:
            file = inpFile.readlines()
            for line in file:
                if line is not None or line != '\n':
                    words = line.split()
                    words = map(lambda word: self.clean(word), words)
                    words = list(filter(lambda word: True if len(word) > 0 else False, words))
                    words = list(filter(lambda word: True if word != '' else False, words))
                    self.sentences.append(words)"""
        csv.field_size_limit(2147483647)
        with open(path, 'r', newline='', encoding="utf-8") as inpFile:

            x = csv.reader(inpFile, delimiter=',', quotechar='"')

            wordThreshold = 5  # Important: filter out sentences with less than wordThreshold words

            for csvEntry in x:
                if len(csvEntry) > 1:
                    lines = csvEntry[1].split('\n')  # csvEntry[0] is url
                    for line in lines:
                        words = line.split()
                        words = map(lambda x: self.clean(x), words)
                        words = list(filter(lambda x: True if len(x) > 0 else False, words))
                        if len(words) > wordThreshold:  # Important: filter out sentences with less than wordThreshold words
                            self.sentences.append(words)
            return self.sentences


###################################################################################
# NLTK model


class NLTKModel(UniModel):
    def __init__(self, filename="", remove_stopwords=True):
        super().__init__(remove_stopwords)

        self.stopword_file = os.path.join(app.SITE_ROOT, 'data', 'long_stopwords.txt')

        if filename != "":
            self.filename = filename
            self.make_corpus(os.path.join(app.SITE_ROOT, filename))

    def get_file(self):
        path = os.path.join(app.SITE_ROOT, self.filename)

        # Open the file
        f = open(path, 'r', encoding="utf-8").read().strip()

        return f

    def tokenise(self, remove_stopwords=True):
        def make_nltk_filename(filename):
            list = filename.split('/')
            list[-1] = "nltk_" + list[-1]
            to_return = "/".join(list)
            return to_return

        def load_tokens():
            f = self.get_file()
            try:
                t = nltk.word_tokenize(f)
            except:
                t = None
                logging.warning("Exception ignored")
            return t

        tokens = None

        if remove_stopwords:
            filtered_words = []
            if os.path.isfile(os.path.join(app.SITE_ROOT, make_nltk_filename(self.filename))):
                with open(os.path.join(app.SITE_ROOT, make_nltk_filename(self.filename)), 'rb') as fp:
                    filtered_words = pickle.load(fp)
                    logging.warning("Loaded")
            else:
                tokens = load_tokens()
                try:
                    logging.warning(self.stop_words) # GOTTA FIX STOPWORDS. MAYBE COPY THE CLEAN FUNCTION?
                    filtered_words = [re.sub('[^A-Za-z]+', '', word.strip().lower()) for word in tokens if word not in self.stop_words]
                    filtered_words = [word for word in filtered_words if not '']
                except:
                    logging.warning("Exception ignored")
                # Save the file
                #logging.warning(os.path.join(app.SITE_ROOT, make_nltk_filename(self.filename)))
                with open(os.path.join(app.SITE_ROOT, make_nltk_filename(self.filename)), 'wb') as fp:
                    pickle.dump(filtered_words, fp)
                    logging.warning("Saved")
            return filtered_words
        else:
            return load_tokens()


###################################################################################
# Word2Vec model

def make_word2vec_model(filename=""):
    path = os.path.join(app.SITE_ROOT, "./models/model_" + filename)
    # Check if the file exists
    if os.path.isfile(os.path.join(app.SITE_ROOT, path)):
        return Word2VecModel().load(path)
    else:
        return Word2VecModel(filename)


class Word2VecModel(UniModel):
    def __init__(self, filename="", remove_stopwords=True):
        super().__init__(remove_stopwords)

        self.model = Word2Vec()

        if filename != "":
            self.filename = filename
            self.sentences = self.make_corpus(os.path.join(app.SITE_ROOT, "./tmp/" + self.filename))
            self.make_model(self.filename)

            self.stopword_file = os.path.join(app.SITE_ROOT, 'data', 'long_stopwords.txt')

    def make_model(self, filename, save_model=True, store_model=True):

        # Make a Word2Vec model
        model = Word2Vec(list(self.sentences), size=100, window=5, min_count=1, workers=4, hs=1, negative=0)

        if save_model:
            # Save the model
            self.save(model, filename)

        if store_model:
            # Store model in memory
            self.model = model

    def get_most_similar(self, positive, negative):
        logging.warning(type(self.model))
        return self.model.most_similar(positive, negative)

    def similarity(self, word1, word2):
        return self.model.similarity(word1, word2)

    def get_word_vector(self, word):
        return self.model[word]

    def get_top_words(self, amount=50):
        return self.model.index2word[:amount]

    def get_word_occurance(self, word):
        return self.model.vocab[word].count

    def save(self, model, filename):
        path = os.path.join(app.SITE_ROOT, 'models', "model_" + filename)
        logging.warning("Saving...")
        if model.wv == None:
            model.save_word2vec_format(path)
        else:
            model.wv.save_word2vec_format(path)

    def load(self, filename):
        self.model = KeyedVectors.load_word2vec_format(filename)
        return self

    def make_tsne(self, items):
        def make_tsnse_dict(items):
            d = {}
            for item in items:
                d[item] = self.model.vocab[item]
            return d

        d = make_tsnse_dict(items)

        vocab = list(d)

        X = self.model[vocab]

        tsne = TSNE(perplexity=25, n_components=2, learning_rate=5, init='pca',random_state=3, n_iter=2000)
        X_tsne = tsne.fit_transform(X)
        df = pd.concat([pd.DataFrame(X_tsne),
                        pd.Series(vocab)],
                       axis=1)

        df.columns = ['x', 'y', 'word']

        return df
