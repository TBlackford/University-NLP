import random
from flask import request, session, redirect, url_for, abort, render_template, flash, make_response
from io import BytesIO
from nlp import app

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from numpy import dot
from numpy.linalg import norm
from spacy.en import English

# List holds all the text corpora
#text_list = [text1, text2, text3, text4, text5, text6, text7, text8, text9]


# For counting the lexical diversity of any given text
def lexical_diversity(text):
    return len(set(text)) / len(text)


# cosine similarity
cosine = lambda v1, v2: dot(v1, v2) / (norm(v1) * norm(v2))


@app.route('/')
def show_entries():
    return render_template('index.html')


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')


@app.route('/api/<string:first>/<string:second>')
def compare_unis(first, second):
    # This will print out
    print("first: ", first)
    print("first: ", second)
    return render_template('index.html')






"""@app.route('/word2vec')
def word_to_vec():
    parser = English()
    # DOES NOT WORK
    # Let's see if it can figure out this analogy
    # Man is to King as Woman is to ??
    king = parser.vocab['king']
    man = parser.vocab['man']
    woman = parser.vocab['woman']

    result = king.vector - man.vector + woman.repvec

    # gather all known words, take only the lowercased versions
    allWords = list({w for w in parser.vocab if
                     w.has_repvec and w.orth_.islower() and w.lower_ != "king" and w.lower_ != "man" and w.lower_ != "woman"})
    # sort by similarity to the result
    allWords.sort(key=lambda w: cosine(w.repvec, result))
    allWords.reverse()
    print("\n----------------------------\nTop 3 closest results for king - man + woman:")

    words = [word.orth_ for word in allWords]

    for word in allWords[:3]:
        print(word.orth_)
    return render_template('lexical_diversity.html', words=words)"""


""""@app.route('/diversity')
def diversity():
    diversity = [[str(t), lexical_diversity(t)] for t in text_list]
    return render_template('lexical_diversity.html', texts=diversity)"""

