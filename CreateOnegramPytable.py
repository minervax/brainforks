import traceback
import tables
import os

# Onegram table definition
class Onegram(tables.IsDescription):
	w1 = tables.StringCol(20)
	freq  = tables.UInt32Col()

def compressed_ngram_yielder(path):
	for f in os.listdir(path):
		print "Working on "+f
		inFile=open(path+f,'r')
		try:
			[w1,year,occ,vol] = inFile.readline().split()
			w1 = w1.lower()

			occur = int(occ)
			for line in inFile:
				[w1_tmp,year,occ_tmp,vol] = line.split()
				w1_tmp = w1_tmp.lower()

				if(w1 != w1_tmp):
					if('_' not in w1):
						yield [w1,occur]
					w1 = w1_tmp
					occur = int(occ_tmp)
				else:
					occur = occur+int(occ_tmp)
			inFile.close()
		except:
			print "ERROR READING "+str(f)
			traceback.print_exc()

def flush_cache(cache,Onegram,h5f,rows):
	for key, value in cache.iteritems():
		Onegram["w1"], Onegram["freq"] = [key,value]
		Onegram.append()
		rows += 1
		if rows % 100000 == 0:
			h5f.flush()
			print("{:d} ngrams flushed...".format(rows))
	return rows

# Initialize the H5 file.
h5filename = "google_onegrams.h5"
filters = tables.Filters(complevel=9, complib="blosc", fletcher32=False)
h5f = tables.open_file(h5filename, mode="w", title="Google Books Onegrams", filters=
filters)
Onegrams_table = h5f.create_table("/", "onegrams", Onegram, "Onegrams Table")

# Write the Onegrams to the table.
Onegram, rows = Onegrams_table.row, 0

cached_rows = 0
rows=0
cache = {}
current_letter = ''
for ngram in compressed_ngram_yielder("/root/downloads/google_ngrams/1/"):
	if not ngram[0][0].isalnum():
		continue

	if(cached_rows > 10000000 or (ngram[0][0] != current_letter and cached_rows > 0)):
		print "Flush cache..."+ngram[0][0]+" "+current_letter
		rows = flush_cache(cache,Onegram,h5f,rows)
		cached_rows=0	
		cache = {}
		current_letter=ngram[0][0]

	if(cache.has_key(ngram[0])):
		cache[ngram[0]] = cache[ngram[0]] + ngram[1]
	else:
		cache[ngram[0]] = ngram[1]
		current_letter=ngram[0][0]
		cached_rows=cached_rows+1
		if(cached_rows % 100000 == 0):
			print("{:d} ngrams cached...".format(cached_rows))
	
rows = flush_cache(cache,Onegram,h5f,rows)
cached_rows=0	
cache = {}

h5f.root.onegrams.cols.w1.create_index()
h5f.root.onegrams.cols.freq.createCSIndex()
h5f.flush()
h5f.close()
