from flask import Flask, redirect, url_for, render_template, make_response, request, send_file, json, jsonify
from flask_restplus import Resource, Namespace
from nlp import app, api, models
from nlp.model_functions import *
import os, sys, logging
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
from gensim.models.word2vec import Word2Vec

import nltk
from nltk.corpus import stopwords


###################################################################################
# API Namespace

ns = Namespace('api', description='API Operations')

@ns.route('/universities')
class UniversityList(Resource):
    def get(self):
        json_url = os.path.join(app.SITE_ROOT, 'data', 'data.json')
        data = json.load(open(json_url))
        return jsonify(data)


### API Routes ###

@ns.route('/relfreq/<string:uni>/<string:word>')
# Descriptions of the variables
@ns.param('uni', 'University')
@ns.param('word', 'Word to check against Frequency')
class RelativeFrequency(Resource):
    def get(self, uni, word):
        logging.warning("See this message in Flask Debug Toolbar!")

        # Create an NLTKModel
        model = models.NLTKModel(models.UniModel.model_path + uni)

        tokens = model.tokenise()

        freq = nltk.FreqDist(tokens)

        return {word: (freq[word] / len(tokens)) * 100, "corpus": str(uni)}


@ns.route('/top50words/<string:uni>')
# Descriptions of the variables
@ns.param('uni', 'University')
class Top50Words(Resource):
    def post(self, uni):
        most_common = top50words(uni)
        return most_common


@ns.route('/similarity/<string:uni>/<string:word>')
class WordSimilarities(Resource):
    def get(self, uni, word):
        model = models.Word2VecModel.load(uni)

        most_similar = model.most_similar(positive=[word])

        return {word: most_similar}


api.add_namespace(ns)