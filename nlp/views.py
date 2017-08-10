from flask import request, session, redirect, url_for, abort, render_template, flash
from nlp import app

import nltk
from nltk.book import *

# List holds all the text corpora
text_list = [text1, text2, text3, text4, text5, text6, text7, text8, text9]


# For counting the lexical diversity of any given text
def lexical_diversity(text):
    return len(set(text)) / len(text)


@app.route('/')
def show_entries():
    return render_template('index.html')


@app.route('/diversity')
def test():
    diversity = [[str(t), lexical_diversity(t)] for t in text_list]
    return render_template('lexical_diversity.html', texts=diversity)

