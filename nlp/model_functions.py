from nlp import app, api, models
import nltk, logging, json

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

    model = models.make_word2vec_model(uni)

    words = common = model.get_top_words()
    common = [{"word": word, "occurrance": model.get_word_occurance(word).count} for word in words]

    return {"name": uni, "list": common}


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
