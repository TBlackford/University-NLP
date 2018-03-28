from nlp import app, api, models
import nltk, logging, json, os

#TODO: Make words most similar to single word function
#TODO: Make percentage cosine similarity between two words function
#TODO: Remove weird buttons

def top50words(uni):
    """model = models.make_word2vec_model(uni)

    common = model.get_top_words()

    word = model.get_word_occurance(common[0])

    logging.warning("Word: " + common[0] + " - Occurance: " + str(word.count))

    logging.warning(common)

    model = models.NLTKModel("./tmp/" + uni)

    tokens = model.tokenise(True)

    frequency = nltk.FreqDist(tokens)

    common = frequency.most_common(50)
    common = [{"word": word, "occurrance": freq} for word, freq in common]"""

    path = "./top50words/" + uni
    path = os.path.join(app.SITE_ROOT, path)

    def _load_or_make():
        # Check if the file exists
        if os.path.isfile(path):
            return _load()
        else:
            data = _make()
            _save(data)
            return data

    def _load():
        return json.load(open(path))

    def _save(data):
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

    def _make():
        model = models.make_word2vec_model(uni)

        words = model.get_top_words()
        common = [{"word": word, "occurrance": model.get_word_occurance(word).count} for word in words]

        return common

    data = _load_or_make()

    return {"name": uni, "list": data}


def most_similar(uni, positive, negative):
    model = models.make_word2vec_model(uni)

    similar = model.get_most_similar(positive, negative)
    similar = [{"word": word, "similarity": sim} for word, sim in similar]

    return {"name": uni, "list": similar}


def similarity(uni, word1, word2):
    model = models.make_word2vec_model(uni)

    similar = model.similarity(word1, word2)

    logging.warning(similar)

    return {"similarity": {"rate": similar, "word1": word1, "word2": word2}}
