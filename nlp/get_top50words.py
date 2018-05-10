import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models.word2vec import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import gensim
from gensim.models.word2vec import Word2Vec
import csv, json, sys, os

json_data=open("./data/data.json").read()

unis = json.loads(json_data)["universities"]

model = gensim.models.Word2Vec.load('./models/bc')

total_word_count = 0

for word in model.wv.vocab:
	total_word_count = total_word_count + model.wv.vocab[word].count
	
for i in range(0, 50):	
	print((model.wv.vocab[model.wv.index2word[i]].count / total_word_count) * 100)
	#print((model.wv.vocab[model.wv.index2word[i]].count / 100) * total_word_count)
	
total_percentage = 0

for i in model.wv.vocab:	
	total_percentage = total_percentage + model.wv.vocab[i].count / total_word_count * 100
	
	print((model.wv.vocab[i].count / total_word_count) * 100)
	print(str(total_percentage))

for uni in unis:
	model = gensim.models.Word2Vec.load('./models/' + uni["model"])
	
	jsonfile = open('./top50words/' + uni["model"] + ".json", 'w')
	jsonfile.write("{\"top50\": [\n")
	
	total_word_count = 0

	for word in model.wv.vocab:
		total_word_count = total_word_count + model.wv.vocab[word].count
		
	for i in range(0, 50):
		json.dump({
			"word": model.wv.index2word[i],
			"frequency": (model.wv.vocab[model.wv.index2word[i]].count / total_word_count) * 100
		}, jsonfile, separators=(',',':'), sort_keys=True, indent=4)
		if i != 49:
			jsonfile.write(',\n')
		
	# close array and object
	jsonfile.write('\n]}')
