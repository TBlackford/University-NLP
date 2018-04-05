from nlp.models import *
import time

def test_similarity(model):
    if model == None:
        model = make_word2vec_model("princeton.csv")

    print(model.similarity("student", "study"))


tests = {
            "similarity": test_similarity
        }


def run_tests(preload_model=False):
    total_start = time.time()

    model = None
    if preload_model:
        model = make_word2vec_model("princeton.csv")

    for name, test in tests.items():
        start = time.time()

        test(model)

        end = time.time()
        print("Time taken for " + name + ": ", end - start)

    total_end = time.time()
    print("Time taken for all tests: ", total_end - total_start)

if __name__ == '__main__':
    run_tests(True)
    run_tests(False)