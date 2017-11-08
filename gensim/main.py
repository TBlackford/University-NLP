import smart_open, os, errno
import nltk
from nltk import book
from gensim import corpora, models, similarities

all_texts = [book.text1, book.text2, book.text3, book.text4, book.text5, book.text6, book.text7, book.text8, book.text9]

####################################################################################################

class MySentences(object):
    def __init__(self, dirname='', fname='', text=None):
        if text is None:
            self.dirname = dirname
            self.fname = fname
            self.text = None
        else:
            self.text = text
        self.tokenized_text = []

    def tokenize(self, line):
        token = nltk.word_tokenize(line)
        self.tokenized_text.append(token)
        return token

    def __iter__(self):
        if self.text is None:
            for line in open(os.path.join(self.dirname, self.fname)):
                # This is broken for now
                yield str(line.encode('utf-8').strip().split())
        else:
            # Check for list (for NLTK)
            if type(self.text) is list:
                for text in self.text:
                    for line in text:
                        yield self.tokenize(line)
            else:
                for line in self.text:
                    yield self.tokenize(line)


####################################################################################################
                
def save_model(model, modelname):
    directory = "./models/"
    if os.path.isdir(directory):
        model.save(directory + modelname)
    else:
        try:
            os.makedirs(directory)
            save_model(model, modelname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise   


def load_model(directory='', fname=''):
    return models.Word2Vec.load(directory + fname) 

####################################################################################################

def make_model(modeldir='', txtfile='', modelname='model', text=None):
    sentences = MySentences(dirname=modeldir, fname=txtfile, text=text)

    print(type(sentences), "is the type of object: sentences")

    print("Sentences: ", sentences.tokenized_text, "\n")

    model = models.Word2Vec(sentences, min_count=20, size=200, workers=8)

    # Train the model
    model.build_vocab(sentences, update=True)
    total_examples = sum([len(sentence) for sentence in sentences])
    model.train(sentences, total_examples=total_examples, epochs=model.iter)

    # Save the model
    save_model(model, modelname + '.txt')

    return model

def make_or_load(modeldir='', txtfile='', modelname='', text=None):
    # Check if directory exists
    if os.path.isfile(modeldir + txtfile):
        return load_model(modeldir, txtfile)
    else:
        return make_model(modeldir=modeldir, txtfile=txtfile, modelname=modelname, text=text)
         

def main():
    #model = make_model('./data/', 'emory.txt')
    #model = make_model(text=book.text1)
    model = make_or_load(modeldir='./models/', txtfile='nltk_texts.txt', modelname='nltk_texts.txt', text=all_texts)

    word = 'man'

    # Buffer between garbage and useful stuffs
    print("\n\n\n")

    print("Accuracy:", model.accuracy('./models/questions-words.txt'))

    print("Word to find most similar to:", word)
    print(model.wv.most_similar(word, topn=5))

    print("woman + king - man is:")
    print(model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1))

    print("Similarity between man and woman:")
    print(model.similarity('woman', 'man'))


if __name__ == "__main__":
    #print(type(book.text1))
    main()
