import traceback
import tables
import gzip
import os

# Bigram table definition
class Bigram(tables.IsDescription):
	w1 = tables.StringCol(20)
	w2 = tables.StringCol(20)
	freq  = tables.UInt32Col()

def compressed_ngram_yielder(path):
	for f in os.listdir(path):
		print "Working on "+f
		if ('.gz' in f):
			inFile = gzip.open(path+f,'r')
		else:
			inFile=open(path+f,'r')
		try:
			[w1,w2,year,occ,vol] = inFile.readline().split()
			w1 = w1.lower()
			w2 = w2.lower()
			occur = int(occ)
			for line in inFile:
				[w1_tmp,w2_tmp,year,occ_tmp,vol] = line.split()
				w1_tmp = w1_tmp.lower()
				w2_tmp = w2_tmp.lower()


				if(w1 != w1_tmp or w2 != w2_tmp):
					if('_' not in w1 and '_' not in w2):
						yield [w1,w2,occur]
					w1 = w1_tmp
					w2 = w2_tmp
					occur = int(occ_tmp)
				else:
					occur = occur+int(occ_tmp)
			inFile.close()
		except:
			print "ERROR READING "+str(f)
			traceback.print_exc()

def flush_cache(cache,bigram,h5f,rows):
	for key, value in cache.iteritems():
		[w1,w2] = key.split('_')
		bigram["w1"], bigram['w2'],bigram["freq"] = [w1,w2,value]
		bigram.append()
		rows += 1
		if rows % 100000 == 0:
			h5f.flush()
			print("{:d} ngrams flushed...".format(rows))
	return rows

# Initialize the H5 file.
h5filename = "google_bigrams.h5"
filters = tables.Filters(complevel=9, complib="blosc", fletcher32=False)
h5f = tables.open_file(h5filename, mode="w", title="Google Books Bigrams", filters=
filters)
Bigrams_table = h5f.create_table("/", "bigrams", Bigram, "Bigrams Table")

# Write the Bigrams to the table.
bigram, rows = Bigrams_table.row, 0

cached_rows = 0
rows=0
cache = {}
current_letter = ''
for ngram in compressed_ngram_yielder("/root/downloads/google_ngrams/2/"):
	if not ngram[0][0].isalnum():
		continue
	if(cached_rows > 50000000 or (ngram[0][0] != current_letter and cached_rows > 0)):
		print "Flush cache..."+ngram[0][0]+" "+current_letter

		rows = flush_cache(cache,bigram,h5f,rows)
		cached_rows=0
		current_letter=ngram[0][0]
		cache = {}

	if(cache.has_key(ngram[0]+'_'+ngram[1])):
		cache[ngram[0]+'_'+ngram[1]] = cache[ngram[0]+'_'+ngram[1]] + ngram[2]
	else:
		cache[ngram[0]+'_'+ngram[1]] = ngram[2]
		cached_rows=cached_rows+1
		current_letter=ngram[0][0]
		if(cached_rows % 100000 == 0):
			print("{:d} ngrams cached...".format(cached_rows))

rows = flush_cache(cache,bigram,h5f,rows)
cached_rows=0	
cache = {}

h5f.root.bigrams.cols.w1.create_index()
h5f.root.bigrams.cols.freq.createCSIndex()
h5f.flush()
h5f.close()
