from flask import request, session, redirect, url_for, abort, render_template, flash
from .nlp import app
from .db import get_db

import nltk
from nltk.book import *

# List holds all the text corpora
text_list = [text1, text2, text3, text4, text5, text6, text7, text8, text9]


# For counting the lexical diversity of any given text
def lexical_diversity(text):
    return len(set(text)) / len(text)


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/diversity')
def test():
    diversity = [[str(t), lexical_diversity(t)] for t in text_list]
    return render_template('lexical_diversity.html', texts=diversity)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
