import ast
import BaseHTTPServer
import time
import sys
import urlparse
from nltk.corpus import wordnet as wn
import json
import inflect
import re
import urllib
import tables
import cgi
from code4lib_brainforks import explore, ngramFilter, creativeBook, creativeSearch, creativeSearchnosub, creativeMaker, foreignLingo, relatedFilter
import itertools

HOST_NAME = '188.165.227.168' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8080 # Maybe set this to 9000.
oneGrams = {}
twoGrams = {}
filters = tables.Filters(complevel=9, complib="blosc", fletcher32=False)
h5fbi = tables.open_file("google_bigrams.h5", mode="r", title="Google Books Bigrams", filters=filters)
h5fone = tables.open_file("google_onegrams.h5", mode="r", title="Google Books Onegrams", filters=filters)

class Bigram(tables.IsDescription):
    w1 = tables.StringCol(20)
    w2 = tables.StringCol(20)
    freq  = tables.UInt32Col()
class Onegram(tables.IsDescription):
    w1 = tables.StringCol(20)
    freq = tables.UInt32Col()

def noDup2(listy):
    listtmp=[]
    for temp in listy:
        if len(temp) > 2:
            listtmp.append(temp[0:2])
        else:
            listtmp.append(temp)

    k = sorted(listtmp, key=lambda tup: tup[0],reverse=True)
    return list(k for k,_ in itertools.groupby(k))

def noDup(listy):

    x = listy
    x = list(set(x))
    return x

def get_synonyms(word):
    pluralizer = inflect.engine()

    syn_set = []
    wnsynset = wn.synsets(word)


    for i in range(0, len(wnsynset)):
        
        for lemma in wnsynset[i].lemma_names():

            syn_set.append(lemma.lower())
            
# adds plurals and removes dups
    
    syn_setnodup = []
    for item in syn_set:
        if item not in syn_setnodup:
            syn_setnodup.append(item)

    syn_set_final = []
    for item in syn_setnodup:
        syn_set_final.append(item)
        syn_set_final.append(pluralizer.plural(item))

    
    return syn_set_final

def get_singplu(word):

    syn_set = []
    pluralizer = inflect.engine()


    if len(word.split()) == 1:
        wnsynset = wn.synsets(word)
        print wnsynset
        #for it in wnsynset:
        if len(wnsynset) > 0:
            it = wnsynset[-1]
            print it.lemma_names()
        else:
            return [[],[]]
        

        if word.lower() in it.lemma_names():
            print "IT IS SINGULAR"
            return [word, pluralizer.plural(word)]
        
        #for i in range(0, len(wnsynset)):
         #   for lemma in wnsynset[i].lemma_names():
        #      syn_set.append(lemma)
        

        #if wnsynset:
            #for it in syn_set:
        else:
            print "IT IS PLURAL"
            sing = str(it.lemma_names()[0])
            plu = word
            return [sing, word]

        return [word, word]

    else:

        
        temp = word.split()[-1]
        others = " ".join(word.split()[0:-1])
        wnsynset = wn.synsets(temp)
        print "WNSYNSET" + str(wnsynset)
        print "MULTIWORD"


        #for it in wnsynset:
        #going to take first word in synset

        if wnsynset:
            it = wnsynset[-1]
            if temp in it.lemma_names():
                print it.lemma_names()
                print "IT IS SINGULAR"
                sing = others + " " + temp
                print "PLURAL IS" + str(temp)
                plu = others + " " + pluralizer.plural(temp)
                print "PLURAL IS" + str(plu)
                return [sing, plu]
            
            #for i in range(0, len(wnsynset)):
            #   for lemma in wnsynset[i].lemma_names():
            #       syn_set.append(lemma)
          
            #if wnsynset:
                #for it in syn_set:
            #if pluralizer.plural(wnsynset[-1]) == temp:
            else:
                print "IT IS PLURAL"
                sing = others + " " + str(it.lemma_names()[0])
                print "SING IS" + str(sing)
                plu = others + " " + temp
                print "PLURAL IS" + str(temp)
                return [sing, plu]

        
        return [word, word]


def get_antonym(word):

    print "Antonym for: " + word

    if len(word.split()) > 1:
        word = word.replace(" ","_")

    # the slow part
    wnsynset = wn.synsets(word)

    print "WYNSET" + str(wnsynset)
    antonym = None
    # only getting one antonym
    for i in wnsynset:
        for el in i.lemmas():
            x = el.antonyms()
            if len(x) > 0:
                print "Antonym"
                antonym = x[0].name()
                break
    syn_set = []
    if antonym is not None:
        print "synonyms for antonym " + str(antonym)


        if len(antonym.split()) > 1:
            word = antonym.replace(" ","_")

       

        # the slow part
        wnsynset = wn.synsets(antonym)

        print "WYNSET" + str(wnsynset)

        for i in range(0, len(wnsynset)):
            for lemma in wnsynset[i].lemma_names():
                print "LEMMA"
                print lemma
                
                syn_set.append(lemma)


                deriv = wn.lemma(wnsynset[i].name() +"."+ lemma)
                print "DERIVATIONS"
                for x in deriv.derivationally_related_forms():
                    print x.name
                    syn_set.append(x.name())

            print "Hyponym function: " 
            for hypo in wnsynset[i].hyponyms():
                syn_set.append(re.findall(r"[a-zA-Z]*",hypo.name())[0])
                print re.findall(r"[a-zA-Z]*",hypo.name())[0]

            '''
            print "Hypernym function: " 
            for hyper in wnsynset[i].hypernyms():
                syn_set.append(re.findall(r"[a-zA-Z]*",hyper.name())[0])
                print re.findall(r"[a-zA-Z]*",hyper.name())[0]
            '''

    return syn_set

     
def get_semantic_score(word):

    print "STARTING semanticScore for" + word

    if len(word.split()) > 1:
        word = word.replace(" ","_")

    pluralizer = inflect.engine()

    syn_set = []

    # the slow part
    wnsynset = wn.synsets(word)

    print "WYNSET" + str(wnsynset)

    syn_set_final = []
    # not suitable for synonyms but good for relations
    abstractions = []


    for i in range(0, len(wnsynset)):

        
        for lemma in wnsynset[i].lemma_names():
            print "LEMMA"
            print lemma
            
            syn_set.append(lemma)

            
            deriv = wn.lemma(wnsynset[i].name() +"."+ lemma)
        
            print "DERIVATIONS"
            for x in deriv.derivationally_related_forms():
                print x.name()
                syn_set.append(x.name())

    syn_set_b = noDup(syn_set)

    if len(syn_set_b) < 11:
        print "FULL SYNONYMS INCLUDING ABSTRACTIONS"
        print syn_set_b
        
    for i in range(0, len(wnsynset)):
        print "Hypernym function: " 
        for hyper in wnsynset[i].hypernyms():

            # 15 in random - did it for fund to finance
            hyper = re.findall(r"[a-zA-Z]*",hyper.name())[0]
            if len(syn_set_b) > 10:

                abstractions.append(hyper)
            else:
                

                syn_set.append(hyper)
            print hyper
        
        print "Hyponym function: " 
        for hypo in wnsynset[i].hyponyms():
            hypo = re.findall(r"[a-zA-Z]*",hypo.name())[0]
            if len(syn_set_b) > 10:
                abstractions.append(hypo)
            else:
               
                syn_set.append(hypo)
            print hypo
        

        # adds plurals and removes dups
    
    syn_setnodup = noDup(syn_set)
    syn_set_final = []
    for item in syn_setnodup:
        syn_set_final.append(item.lower())
        syn_set_final.append(pluralizer.plural(item).lower())
    

    abstractions = noDup(abstractions)
    abstractions_final = []
    for item in abstractions:
        abstractions_final.append(item.lower())
        abstractions_final.append(pluralizer.plural(item).lower())
    
    uselesswords = ["issues", "issues", "organization", "organizations"]
   
    abstractions_final = [w for w in abstractions_final if w.lower() not in uselesswords]
    syn_set_final = [w for w in syn_set_final if w.lower() not in uselesswords]


    print "END semanticScore"

    return [syn_set_final, abstractions_final]



def get_frequency(wordlist):
    wordfreq = ()

    # Bigram table definition

    if(len(wordlist) > 1):
        word1 = wordlist[0].replace('\'','\\\'').lower()
        word2 = wordlist[1].replace('\'','\\\'').lower()
        freq = 0
        for bg in h5fbi.root.bigrams.where("(w1=='"+word1+"') & (w2=='"+word2+"')"):
            print "Found: "+bg['w1']+" "+bg['w2']
            freq=freq+bg['freq']

        wordfreq = (word1+"_"+word2, freq)
        print freq

    else:
            word1 = wordlist[0].replace('\'','\\\'').lower()
            freq = 0
            
            print str(wordlist[0].lower())
            for bg in h5fone.root.onegrams.where("(w1=='"+word1+"')"):
                print "Found: "+bg['w1']
                freq=freq+bg['freq']

            freq = int(freq/11.75)
            print freq
            wordfreq = (word1,freq)

    return wordfreq

def get_explore(word):
	x = relatedFilter(word)
	return x

def get_ngramlist(word):
    x = ngramFilter(word)
    return x

def get_maker(word):
    x = creativeMaker(word)
    return x

def get_creativeBook(word):
    x = creativeBook(word)
    return x

def get_creativeSearch(word):
    x = creativeSearch(word)
    return x

def get_creativeSearch2(word):
    x = creativeSearchnosub(word)
    return x

def get_nonnative(word):
    x = foreignLingo(word)
    return x


class RedirectHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.do_GET()
    def do_GET(s):
        method_word = s.path[1:].split("/")

        print method_word
        ret = ""
        if method_word[0] == "Synonym":
            ret = get_synonyms(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "semanticscore":
            ret = get_semantic_score(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "singplu":
            ret = get_singplu(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "antonym":
            ret = get_antonym(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "ngram":
            ret = get_ngramlist(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "maker":
            ret = get_maker(urllib.unquote(method_word[1]).decode('utf8'))    
        if method_word[0] == "explore":
            ret = get_explore(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "creativebook":
            ret = get_creativeBook(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "creativesearch":
            ret = get_creativeSearch(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "creativesearch2":
            ret = get_creativeSearch2(urllib.unquote(method_word[1]).decode('utf8'))
        if method_word[0] == "nonnative":
            ret = get_nonnative(urllib.unquote(method_word[1]).decode('utf8'))  
        if method_word[0] == "getfreq":
    	    ret = []
    	    wlist = ast.literal_eval(urllib.unquote(method_word[1]))
    	    for words in wlist:
    	        ret.append(get_frequency(words))

    	if method_word[0] == "dbpedia":
            ret = dbpediajson(urllib.unquote(method_word[1]).decode('utf8'))
        
        s.send_response(200)
        s.send_header("content-type","application/json")
        s.send_header("Access-Control-Allow-Origin","*")
        s.end_headers()
        s.wfile.write(json.dumps(ret))
        s.wfile.close();           
    
    def do_OPTIONS(s):
	   s.do_GET()
    def do_POST(s):
        method_word = s.path[1:].split("/")
        length = int(s.headers.getheader('content-length'))
        postvars = cgi.parse_qs(s.rfile.read(length), keep_blank_values=1)
        print method_word
        ret = ""

        if method_word[0] == "getfreq":
            ret = []
            print postvars["list"][0]
            wlist = ast.literal_eval(urllib.unquote(postvars["list"][0]))
            wlist = noDup2(wlist)
            print wlist
            for words in wlist:
                ret.append(get_frequency(words))

        s.send_response(200)
        s.send_header("content-type","application/json")
        s.send_header("Access-Control-Allow-Origin","*")
        s.end_headers()
        s.wfile.write(json.dumps(ret))
        s.wfile.close();  

if __name__ == '__main__':

    """
    print "Loading word freq data..."
    oneGramFile = open("w1_.txt",'r').readlines()
    for line in oneGramFile:
        line = line.strip()
        [word,freq] = line.split("\t")
        oneGrams[word] = freq

    twoGramFile = open("w2_.txt",'r').readlines()
    for line in twoGramFile:
        line = line.strip()
        [freq,word1,word2] = line.split("\t")
        twoGrams[word1+" "+word2] = freq

    print "Data loaded..."
    """
    
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), RedirectHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

