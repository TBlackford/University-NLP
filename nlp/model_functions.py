from nlp import app, api, models
import nltk, logging, json


def top50words(uni):
    model = models.NLTKModel("./tmp/" + uni)

    tokens = model.tokenise(True)

    frequency = nltk.FreqDist(tokens)

    common = frequency.most_common(50)
    common = [{"word": word, "occurrance": freq} for word, freq in common]

    return {"name": uni, "list": common}


def most_similar(uni, positive, negative):
    model = models.make_word2vec_model(uni)

    logging.warning("WORD2VEC MODEL TYPE")
    logging.warning(type(model))

    similar = model.get_most_similar(positive, negative)
    similar = [{"word": word, "similarity": similarity} for word, similarity in similar]

    return {"name": uni, "list": similar}


