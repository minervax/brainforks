#includes support for Personal Names and Orgs (like Lightspeed) for linkeddata

import re
import requests
import sys
from bs4 import BeautifulSoup
import time
import operator
import json
import nltk
from nltk.collocations import *
from nltk import word_tokenize
from nltk import pos_tag
from nltk import wordpunct_tokenize
#from nltk.book import *
from nltk.stem import *
import pickle
import json
from collections import Counter
from nltk.corpus import wordnet as wn
import inflect
from requests import get
import requests
import os
#from nltk.tag.stanford import NERTagger
import urllib, json
import django.utils.encoding
import collections
import threading
import Queue
import operator

stopwords = ["v.", "my", "\'ve","\'re","\'ll","\'d",'vs.', "van", "de", "constantly", "leave", "n't", "'s", "a","a's","able","about","above","according","accordingly","across","actually","after","afterwards","again","against","ain't","all","allow","allows","almost","alone","along","already","also","although","always","am","among","amongst","an","and","another","any","anybody","anyhow","anyone","anything","anyway","anyways","anywhere","apart","appear","appreciate","appropriate","are","aren't","around","as","aside","ask","asking","associated","at","available","away","awfully","b","be","became","because","become","becomes","becoming","been","before","beforehand","behind","being","believe","below","beside","besides","best","better","between","beyond","both","brief","but","by","c","c'mon","c's","came","can","can't","cannot","cant","cause","causes","certain","certainly","changes","clearly","co","com","come","comes","concerning","consequently","consider","considering","contain","containing","contains","corresponding","could","couldn't","course","currently","d","definitely","described","despite","did","didn't","different","do","does","doesn't","doing","don't","done","down","downwards","during","e","each","edu","eg","eight","either","else","elsewhere","enough","entirely","especially","et","etc","even","ever","every","everybody","everyone","everything","everywhere","ex","exactly","example","except","f","far","few","fifth","first","five","followed","following","follows","for","former","formerly","forth","four","from","further","furthermore","g","get","gets","getting","given","gives","go","goes","going","gone","got","gotten","greetings","h","had","hadn't","happens","hardly","has","hasn't","have","haven't","having","he","he's","hello","help","hence","her","here","here's","hereafter","hereby","herein","hereupon","hers","herself","hi","him","himself","his","hither","hopefully","how","howbeit","however","i","i'd","i'll","i'm","i've","ie","if","ignored","immediate","in","inasmuch","inc","indeed","indicate","indicated","indicates","inner","insofar","instead","into","inward","is","isn't","it","it'd","it'll","it's","its","itself","j","just","k","keep","keeps","kept","know","knows","known","l","last","lately","later","latter","latterly","least","less","lest","let","let's","like","liked","likely","little","look","looking","looks","ltd","m","mainly","many","may","maybe","me","mean","meanwhile","merely","might","more","moreover","most","mostly","much","must","my","myself","n","name","namely","nd","near","nearly","necessary","need","needs","neither","never","nevertheless","new","next","nine","no","nobody","non","none","noone","nor","normally","not","nothing","novel","now","nowhere","o","obviously","of","off","often","oh","ok","okay","old","on","once","one","ones","only","onto","or","other","others","otherwise","ought","our","ours","ourselves","out","outside","over","overall","own","p","particular","particularly","per","perhaps","placed","please","plus","possible","presumably","probably","provides","q","que","quite","qv","r","rather","rd","re","really","reasonably","regarding","regardless","regards","relatively","respectively","right","s","said","same","saw","say","saying","says","second","secondly","see","seeing","seem","seemed","seeming","seems","seen","self","selves","sensible","sent","serious","seriously","seven","several","shall","she","should","shouldn't","since","six","so","some","somebody","somehow","someone","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specified","specify","specifying","still","sub","such","sup","sure","t","t's","take","taken","tell","tends","th","than","thank","thanks","thanx","that","that's","thats","the","their","theirs","them","themselves","then","thence","there","there's","thereafter","thereby","therefore","therein","theres","thereupon","these","they","they'd","they'll","they're","they've","think","third","this","thorough","thoroughly","those","though","three","through","throughout","thru","thus","to","together","too","took","toward","towards","tried","tries","truly","try","trying","twice","two","u","un","under","unfortunately","unless","unlikely","until","unto","up","upon","us","use","used","useful","uses","using","usually","uucp","v","value","various","very","via","viz","vs","w","want","wants","was","wasn't","way","we","we'd","we'll","we're","we've","welcome","well","went","were","weren't","what","what's","whatever","when","whence","whenever","where","where's","whereafter","whereas","whereby","wherein","whereupon","wherever","whether","which","while","whither","who","who's","whoever","whole","whom","whose","why","will","willing","wish","with","within","without","won't","wonder","would","would","wouldn't","x","y","yes","yet","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]
uselesswords = ["history","categories by type", "list of lists", "terms", "index", "wikiproject", "pages", "taskforce", "templates","verb", "television", "tv", "films", "redirects", "defunct", "relocated", "lists", "wikipedia", "portal", "terminology", "images of", "fictional"]
countries = ["New Zealeand", "New Zealander", "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo"," Republic of the","Congo"," Democratic Republic of the","Costa Rica","Cote d'Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar"," Burma","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","St. Kitts and Nevis ","St. Lucia","St. Vincent and The Grenadines ","Samoa","San Marino","Sao Tome and Principe ","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","UK"," United Kingdom"," USA"," United States of America"," United States"," America"," Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]
nationalities = ["Afghan","Albanian","Algerian","American","Andorran","Angolan","Antiguans","Argentinean","Armenian","Australian","Austrian","Azerbaijani","Bahamian","Bahraini","Bangladeshi","Barbadian","Barbudans","Batswana","Belarusian","Belgian","Belizean","Beninese","Bhutanese","Bolivian","Bosnian","Brazilian","British","Bruneian","Bulgarian","Burkinabe","Burmese","Burundian","Cambodian","Cameroonian","Canadian","Cape Verdean","Central African","Chadian","Chilean","Chinese","Colombian","Comoran","Congolese","Costa Rican","Croatian","Cuban","Cypriot","Czech","Danish","Djibouti","Dominican","Dutch","East Timorese","Ecuadorean","Egyptian","Emirian","Equatorial Guinean","Eritrean","Estonian","Ethiopian","Fijian","Filipino","Finnish","French","Gabonese","Gambian","Georgian","German","Ghanaian","Greek","Grenadian","Guatemalan","Guinea-Bissauan","Guinean","Guyanese","Haitian","Herzegovinian","Honduran","Hungarian","Icelander","Indian","Indonesian","Iranian","Iraqi","Irish","Israeli","Italian","Ivorian","Jamaican","Japanese","Jordanian","Kazakhstani","Kenyan","Kittian and Nevisian","Kuwaiti","Kyrgyz","Laotian","Latvian","Lebanese","Liberian","Libyan","Liechtensteiner","Lithuanian","Luxembourger","Macedonian","Malagasy","Malawian","Malaysian","Maldivan","Malian","Maltese","Marshallese","Mauritanian","Mauritian","Mexican","Micronesian","Moldovan","Monacan","Mongolian","Moroccan","Mosotho","Motswana","Mozambican","Namibian","Nauruan","Nepalese","Netherlander","New Zealander","Ni-Vanuatu","Nicaraguan","Nigerian","Nigerien","North Korean","Northern Irish","Norwegian","Omani","Pakistani","Palauan","Panamanian","Papua New Guinean","Paraguayan","Peruvian","Polish","Portuguese","Qatari","Romanian","Russian","Rwandan","Saint Lucian","Salvadoran","Samoan","San Marinese","Sao Tomean","Saudi","Scottish","Senegalese","Serbian","Seychellois","Sierra Leonean","Singaporean","Slovakian","Slovenian","Solomon Islander","Somali","South African","South Korean","Spanish","Sri Lankan","Sudanese","Surinamer","Swazi","Swedish","Swiss","Syrian","Taiwanese","Tajik","Tanzanian","Thai","Togolese","Tongan","Trinidadian or Tobagonian","Tunisian","Turkish","Tuvaluan","Ugandan","Ukrainian","Uruguayan","Uzbekistani","Venezuelan","Vietnamese","Welsh","Yemenite","Zambian","Zimbabwean"]
countriesnat = countries + nationalities
peopleandorgs = []

reload(sys)
sys.setdefaultencoding("utf-8")

def sparqlQuery(query, baseURL, format="application/json"):

	query = query.strip()

	params={

		"default-graph": "",

		"should-sponge": "soft",

		"query": query,

		"debug": "on",

		"timeout": "",

		"format": format,

		"save": "display",

		"fname": ""

	}

	querypart=urllib.urlencode(params)

	response = urllib.urlopen(baseURL,querypart).read()

	return json.loads(response)


def Sparql(word, concept):


	#dsn="http://10.0.1.9:8890/sparql"
	#dsn="http://dbpedia.org/sparql"
	#dsn="http://live.dbpedia.org/sparql"
	dsn="http://brainforks.com:8890/sparql"

	# does not have personal things dsn="http://brainforks.com:8890/sparql"

	urilist= []

	if concept == "Category":


		query = """
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where {?result <http://www.w3.org/2000/01/rdf-schema#label> \"""" +word.replace("_"," ")+"""\"@en; rdf:type skos:Concept
		Filter( regex(?result, "Category"))} LIMIT 100"""


	elif concept == "Thing":

		#removed filters to have personal objects

		query="""

		prefix dbo: <http://dbpedia.org/ontology/>
		select ?result
		where {

		?result <http://www.w3.org/2000/01/rdf-schema#label> \""""+word.replace("_"," ")+"""\"@en }"""

		"""
		#commented this out this include all linkedata

		Filter(! regex(?result, "Category"))
		Filter(! regex(?result, "property"))
		filter not exists { ?result rdf:type dbo:TelevisionShow }
		filter not exists { ?result rdf:type dbo:Album }
		filter not exists { ?result rdf:type dbo:Book }
		Filter(! regex(?result, "wikidata"))
		}"""
		
	elif concept == "Ambiguous":


		query = """
		prefix dbo: <http://dbpedia.org/ontology/>
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

		select ?result where {<http://dbpedia.org/resource/"""+word+"""> dbpedia-owl:wikiPageDisambiguates ?result
		filter not exists { ?result rdf:type dbo:TelevisionShow }
		filter not exists { ?result rdf:type dbo:Album }
		filter not exists { ?result rdf:type dbo:Book }
		filter not exists { ?result rdf:type dbo:work }
		} LIMIT 100"""


	elif concept == "disambi":

		query = """
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

		select ?result where {?result dbpedia-owl:wikiPageDisambiguates <http://dbpedia.org/resource/"""+word+""">} LIMIT 100"""

	elif concept == "redirect":

		query = """PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbo: <http://dbpedia.org/ontology/>

		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where {
		<http://dbpedia.org/resource/"""+word+"""> dbo:wikiPageRedirects ?result.

		} LIMIT 100"""
	
	elif concept == "primarytopic":

		query = """
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>

		select ?result where {<http://dbpedia.org/resource/"""+word+"""> foaf:isPrimaryTopicOf ?result} LIMIT 100"""



	elif concept == "abstract":

		query = """
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

		select ?result where {<http://dbpedia.org/resource/"""+word+"""> dbpedia-owl:abstract ?result. FILTER langMatches( lang(?result), 'en')} LIMIT 100"""


	elif concept == "subject":

		query = """	
		PREFIX dcterms: <http://purl.org/dc/terms/>
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where { ?x <http://www.w3.org/2000/01/rdf-schema#label> \""""+word.replace("_"," ")+"""\"@en.
		?x dcterms:subject ?result

		} LIMIT 500"""


		
	elif concept == "subjectof":

		query = """	
		PREFIX dcterms: <http://purl.org/dc/terms/>
		PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where { ?x <http://www.w3.org/2000/01/rdf-schema#label> \""""+word.replace("_"," ")+"""\"@en.
		?result dcterms:subject ?x

		} LIMIT 500"""



	
	elif concept == "broader":


		query="""PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where { ?x <http://www.w3.org/2000/01/rdf-schema#label> \""""+word.replace("_"," ")+"""\"@en.
		?x skos:broader ?result

		} LIMIT 100"""
		
		

	elif concept == "broaderof":

		query="""PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
		PREFIX dbpprop: <http://dbpedia.org/property/>
		PREFIX  dc: <http://purl.org/dc/elements/1.1/>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

		select ?result where { ?x <http://www.w3.org/2000/01/rdf-schema#label> \""""+word.replace("_"," ")+"""\"@en.
		?result skos:broader ?x

		} LIMIT 100"""


	'''
	query for all things
	SELECT Distinct ?s {?s rdf:type dbo:Book}
	SELECT Distinct ?s {?s rdf:type owl:Thing}
	'''

	#print query

	try:
		data=sparqlQuery(query, dsn)
	except KeyboardInterrupt:
		pass

	
	#print data


	if len(data['results']['bindings']) > 0:

		jsonStr = json.dumps(data, sort_keys=True, indent=4)

		#print "Result Retrieved: "
		x = data['results']['bindings']

		for i in range(0, len(x)):
			urilist.append(x[i]['result']['value'])

		#print str(urilist)

		
	return urilist



def tagme(text):

	payload = {'key': 'a83422612f1d2deb425b09a9a5db4b6a', 'text': text, 'lang':'en'}
	print payload
	r = requests.post("http://tagme.di.unipi.it/tag", data=payload)
	print r
	x = json.loads(r.text)

	tags = []

	for i in range(0, len(x['annotations'])):
		evalu = float(x['annotations'][i]['rho'])
		spot = x['annotations'][i]['spot']
		if evalu > .20:

			if spot not in tags:
				tags.append(spot)
	
	# using different rho for more results
	if len(tags) < 10:

		for i in range(0, len(x['annotations'])):
			evalu = float(x['annotations'][i]['rho'])
			spot = x['annotations'][i]['spot']
			#print spot
			if evalu > .10 and evalu < .21:
				tags.append(spot)
	



	# remove weird words for queries (and maybe people in the future)

	annoyingwikipediawords = ["search", "navigation", "wikipedia", "citation needed", "improve this article", "adding citations to reliable sources"]
	for word in tags:
		for it in annoyingwikipediawords:
			if word.strip().lower() == it.strip().lower():
				tags.remove(word)
				break
	#print "WJDJDJDJDJDJDJD" + str(tags)
	return tags



def wikipediaTags(uri):

	# for ambiguous pages, they turn out to be a list
	if type(uri) is list:
		return uri
	

	elif uri is None:

		return None

	else:

		if "Category" in uri:
			wikipedialink = Sparql(uri[37:], "primarytopic")[0]
			# getting first paragraph
			print "ABSTRACTING"
			resabstract = Sparql(uri[37:], "abstract")
			
			if len(resabstract) > 0:
				fulltext = resabstract[0]
		else:
			fulltext = ""
			wikipedialink = Sparql(uri[28:], "primarytopic")[0]
			print "ABSTRACTING"
			resabstract = Sparql(uri[28:], "abstract")
			
			if len(resabstract) > 0:
				fulltext = resabstract[0]

		print "WIKI"
		wikipage_html = requests.get(str(wikipedialink.strip()))


		if "<span class=\"mw-headline\" id=\"In_fiction\">In fiction</span>" in wikipage_html.content:
			wikipage_text = wikipage_html.content[0:wikipage_html.content.find("id=\"In_fiction\"")]

		elif "<span class=\"mw-headline\" id=\"See_also\">See also</span>" in wikipage_html.content: 
			wikipage_text = wikipage_html.content[0:wikipage_html.content.find("id=\"See_also\"")]
		else:
			wikipage_text = wikipage_html.content[0:wikipage_html.content.find("id=\"References\"")]



		wikisoup = BeautifulSoup(wikipage_text)

		wikitext = []

		wikili = wikisoup.findAll("li") 
		wikidi = wikisoup.findAll("dd")

		
		wikili = filter(lambda x: x.attrs == {}, wikili)
		for item in wikili:
			
			if len(item.findAll("a")) > 0:
				y = item.findAll("a")[0].findAll(text = True)
				
				if len(y[0]) > 2:

					if y[0] not in wikitext:

						wikitext.append(y[0].strip())


		#dd tag is for description list, learned in Spearfishing article
		wikidi = filter(lambda x: x.attrs == {}, wikidi)
		for item in wikidi:
			
			if len(item.findAll("a")) > 0:
				y = item.findAll("a")[0].findAll(text = True)
				
				if len(y[0]) > 2:

					if y[0] not in wikitext:

						wikitext.append(y[0].strip())
		

		
		
	
		# tag me of first paragraph

		if len(resabstract) > 0:
			tagmewords = tagme(fulltext)
			for item in tagmewords:

				# there were weird results like "Magic, religion"

				if "," in item:
					for el in item.split(","):
							#print el
							if el not in wikitext:
								wikitext.append(el.strip().capitalize())
				else:
					if item not in wikitext:
						wikitext.append(item)

		countries = ["Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo"," Republic of the","Congo"," Democratic Republic of the","Costa Rica","Cote d'Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar"," Burma","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","St. Kitts and Nevis ","St. Lucia","St. Vincent and The Grenadines ","Samoa","San Marino","Sao Tome and Principe ","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","UK"," United Kingdom"," USA"," United States of America"," United States"," America"," Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]
		nationalities = ["Afghan","Albanian","Algerian","American","Andorran","Angolan","Antiguans","Argentinean","Armenian","Australian","Austrian","Azerbaijani","Bahamian","Bahraini","Bangladeshi","Barbadian","Barbudans","Batswana","Belarusian","Belgian","Belizean","Beninese","Bhutanese","Bolivian","Bosnian","Brazilian","British","Bruneian","Bulgarian","Burkinabe","Burmese","Burundian","Cambodian","Cameroonian","Canadian","Cape Verdean","Central African","Chadian","Chilean","Chinese","Colombian","Comoran","Congolese","Costa Rican","Croatian","Cuban","Cypriot","Czech","Danish","Djibouti","Dominican","Dutch","East Timorese","Ecuadorean","Egyptian","Emirian","Equatorial Guinean","Eritrean","Estonian","Ethiopian","Fijian","Filipino","Finnish","French","Gabonese","Gambian","Georgian","German","Ghanaian","Greek","Grenadian","Guatemalan","Guinea-Bissauan","Guinean","Guyanese","Haitian","Herzegovinian","Honduran","Hungarian","Icelander","Indian","Indonesian","Iranian","Iraqi","Irish","Israeli","Italian","Ivorian","Jamaican","Japanese","Jordanian","Kazakhstani","Kenyan","Kittian and Nevisian","Kuwaiti","Kyrgyz","Laotian","Latvian","Lebanese","Liberian","Libyan","Liechtensteiner","Lithuanian","Luxembourger","Macedonian","Malagasy","Malawian","Malaysian","Maldivan","Malian","Maltese","Marshallese","Mauritanian","Mauritian","Mexican","Micronesian","Moldovan","Monacan","Mongolian","Moroccan","Mosotho","Motswana","Mozambican","Namibian","Nauruan","Nepalese","Netherlander","New Zealander","Ni-Vanuatu","Nicaraguan","Nigerian","Nigerien","North Korean","Northern Irish","Norwegian","Omani","Pakistani","Palauan","Panamanian","Papua New Guinean","Paraguayan","Peruvian","Polish","Portuguese","Qatari","Romanian","Russian","Rwandan","Saint Lucian","Salvadoran","Samoan","San Marinese","Sao Tomean","Saudi","Scottish","Senegalese","Serbian","Seychellois","Sierra Leonean","Singaporean","Slovakian","Slovenian","Solomon Islander","Somali","South African","South Korean","Spanish","Sri Lankan","Sudanese","Surinamer","Swazi","Swedish","Swiss","Syrian","Taiwanese","Tajik","Tanzanian","Thai","Togolese","Tongan","Trinidadian or Tobagonian","Tunisian","Turkish","Tuvaluan","Ugandan","Ukrainian","Uruguayan","Uzbekistani","Venezuelan","Vietnamese","Welsh","Yemenite","Zambian","Zimbabwean"]
		wikitext = [word for word in wikitext if word not in countries]
		wikitext = [word for word in wikitext if word not in nationalities]
		return wikitext





def ScrapePage(word):

	
	if "http" in word:
		uri = word
	
	else:
		#uri = word.lower().capitalize().replace(" ", "_")
		uri = word
	
	urilist = Sparql(uri, "Thing")

	#for kept caps like Environment of California
	'''
	if len(urilist) == 0:
		uri = word.replace(" ", "_")
		urilist = Sparql(uri, "Thing")

	# for weird hyphens

	if len(urilist) == 0:
		uri = word.replace("-", "_")
		urilist = Sparql(uri, "Thing")
	

	if len(urilist) == 0:
		print "THERE IS NOT SUCH PAGE"
		return None
	'''
		# if page is ambiguous

	

	# for issues like Turnover_(employment) that are already disambiguated
	if urilist:
		if "(" not in urilist[0]:
			
			ambiguousterms = Sparql(urilist[0][28:], "Ambiguous")
			
			if len(ambiguousterms) > 0:
				print "AMBIGUOUS" + str(ambiguousterms)
			
				return ambiguousterms

			else:

				return urilist[0]
		else:

			return urilist[0]


	else:
	
		return None


def ScrapeCategoryPage(word):

	if "http" in word:
		uri = word[37:]
	else:
		#uri = word.replace(" ", "_").lower().capitalize()+"s"
		uri = word
	
	urilist = Sparql(uri, "Category")


	if len(urilist) == 0:
		return False
	else:
		#print "ScrapeCategoryPage result:" + str(urilist[0])
		return urilist[0]




def ScrapeCategoryOf(uri):
	
	print "ScrapeCategoryOf"
	print uri
	
	# for empty pages
	if uri is None:

		return None

		# for ambiguous results

	elif type(uri) is list:

		return uri
		
	else:

		if "http" in uri:
			
			urilist = Sparql(uri[28:], "subject")

		else:

			urilist = Sparql(uri, "subject")

		categories = []

		for i in range(0,len(urilist)):

			categories.append( urilist[i][37:].replace("_", " ") )	
		

		return categories



def conceptScrapeSubjectOf(caturi):


	subjects = []

	
	if type(caturi) is not bool:

		uri = caturi.replace(" ", "_")
		 
		subjectlist = Sparql(uri[37:], "subjectof")

		for i in range(0,len(subjectlist)):

			subjects.append( subjectlist[i][28:].replace("_"," ") )
	
	return subjects

def conceptScrapeBroaderOf(caturi):

	
	subjects = []


	if type(caturi) is not bool:

		uri = caturi.replace(" ", "_")

		subjectlist = Sparql(uri[37:], "broaderof")

		for i in range(0,len(subjectlist)):

			subjects.append( subjectlist[i][37:].replace("_"," ") )

	
	return subjects


def conceptScrapeBroader(caturi):

	subjects = []


	if type(caturi) is not bool:

		uri = caturi.replace(" ", "_")
		
		subjectlist = Sparql(uri[37:], "broader")

		for i in range(0,len(subjectlist)):

			subjects.append(subjectlist[i][37:].replace("_"," "))

	
	return subjects



def nerFilter(resultlist):
				

	# tried to use the website at some point
	newlist = []
	#print "NER PROCESSING"
	#print "NERFILTER"
	#print len(resultlist)
	#print "BEFORE" +str(resultlist)
	discard = []
	for word in resultlist:
		#print "BEFORE" + word

		if len(word.split()) > 1:
			wordsplit = word.split()
			common = set(wordsplit)&set(countriesnat)
			if len(common)>0:
				continue

			#print "WOOOOOOOOOOORDSPLT"
			#print wordsplit
			#print word

			if not word.replace(" ","").isalpha():
				#print "lost this word isalpha"
				#print word
				continue

			for item in wordsplit:
				if item.lower() in uselesswords:
					#print "lost this word useless"
					discard.append(word)
			if word in discard:
				continue


			#removing capitalised things
			#print "removing cap items" 
			#print wordsplit
			wordlist = [item for item in wordsplit if (item.lower() not in stopwords and (wordsplit.index(item) is not 0 and not item[0].isupper()))]
			#print "after cap items"
			#print wordlist
			
			#print "AFTER" + str(wordlist)
			if len(wordlist) is not 0:
				#print "heyoooooooo"
				newlist.append(word)
			
		else:
			newlist.append(word)
		
		#print "AFTER" + wordtemp

		if word not in newlist:
			#print "PEOPLE AND ORG" + word
			peopleandorgs.append(word)

	#print "After" + str(newlist)

	return newlist

def semanticScore(word):

	if "(" in word:
		#removed word = mainword.split(...)[0]
		word = word.split("_(")[0]

	resp = requests.get("http://localhost:3333/semanticscore/"+word)
	ret = json.loads(resp.text)

	if ret:

		syns = ret[0]
		#print syns
		for i in range(0, len(syns)-1):
			
			# the replace was for start_up to startup
			syns[i] = urllib.unquote(syns[i]).decode('utf8').replace("_", "")
		
		abstracts = ret[1]
		for i in range(0, len(abstracts)-1):
			
			abstracts[i] = urllib.unquote(abstracts[i]).decode('utf8').replace("_", "")

		#print "WORDNET RESULTS SYNS" + str(ret)
		#print "WORDNET RESULTS ABSRACTS" + str(abstracts)
		
		return [syns, abstracts]

	else:
		return [[],[]]


def antonym(word):

	resp = requests.get("http://localhost:3333/antonym/"+word)
	ret = json.loads(resp.text)
	for i in range(0, len(ret)-1):
		
		ret[i] = urllib.unquote(ret[i]).decode('utf8').replace("_", "")

	return ret


def actual(word):

	#print "ACTUAL FUNCTION"


	if "by" in word.split():
		#print "CATEGORY .by. MATCH" + str(word)
		split = word.split()
		if "type" in split:
			word = split[0]
			#print "NEW WORD" + word
		elif "People" in split:
			word = split[2]
			#print "NEW WORD" + word
		else:
			word = word[0:word.find("by")]
			#print "NEW WORD" + word

	return word

def stopwordify(listy):
	#print "STOP WORDIFYING"
	
	newlisty = []
	if type(listy) is list:
		for it in listy:
			newlisty.append(actual(it))

	else:
		newlisty = actual(listy)
		
	#print "RESULT STOPWORD" + str(newlisty)
	return newlisty

def prerelate(query, catlist, querysyns, alluris, othercats, relatedcats):

	if catlist is not None:
		for cat in catlist:

			print "START RELATE"
			print cat
			
			query = query.replace("_"," ")
			if cat.strip() not in alluris:
				

				if cat in relatedcats:
					return


				elif cat.lower() in query.lower():
					#print "EVALUATING" + str(cat)
					relatedcats.append(cat)

				elif query.lower() in cat.lower():
					#print "EVALUATING" + str(cat)
					relatedcats.append(cat)
			
				elif len(query.split()) == 1:

					#print "EVALUATING" + str(cat)
					relate(cat.replace("_", " "), query, querysyns, relatedcats, othercats, True)
				else:


					#print "MULTIWORD"
					# had to this because categories would be two words like "Educational Institution"
					
					# for cases like First-aid, and first-aid-kit
					
			
					for q in query.split():
						#print q
						#print "EVALUATING Query part" + str(q)
						#print "EVALUATING cat" + str(cat)
						if q.lower() not in stopwords:
							relate(cat.replace("_", " "), q, querysyns, relatedcats, othercats, False)



def relate(cat, q, querysyns, relatedcats, othercats, full):


	
	total = []

	cat = stopwordify(cat)

	#print cat.strip().lower()
	#print q.strip().lower()
	#plu is actually singular, duh

	# dont want toinclude the same turn or its variations in related cats
	if cat.strip().lower() == q.strip().lower():
		if full == True:

			return
		else:
			if cat not in relatedcats:
				relatedcats.append(cat)
				return
		

	# for cases like Freediving, Free-divng
	
	elif cat.replace("-","").strip().lower() == q.strip().lower() and cat not in relatedcats:
		relatedcats.append(cat)
		return

	#added this to catch more related cats, maybe too broad
	#ex human resource in human resource management
	elif q.strip().lower() in cat.strip().lower() and cat not in relatedcats:
		relatedcats.append(cat)
		return


	# comparing all the wordnet synonyms
	
	sem = semanticScore(cat)
	temp = sem[0] + sem[1] + [cat]

	#print "CAT SYNS" + str(temp)
	#print querysyns 



	for el in temp:
		for it in querysyns:
			
			if it.lower().strip() in el.lower().strip().split() and cat not in relatedcats:
				
				relatedcats.append(cat)
				break

		if cat in relatedcats:
			break

	if cat not in othercats and cat not in relatedcats:
		othercats.append(cat)
	

	#print "DONE RELATE"


# cleaning out useless dbpedia words, NER results and duplicates or other forms of the query


def popularWord(wordlist):

	popwords = {"wordlist":str(wordlist)}

	
	resp = requests.post("http://localhost:3333/getfreq/", data=popwords)
	print "FREEEEEEEQ" 
	#ret = json.loads(resp.text)
	print resp.content
	popwords = json.loads(resp.content)

	return popwords




def lemmatize(word, querysyns):

	#endings = ["ble, ing, ly, er, ble, ed, ally"]
	lemmas = []
	for el in querysyns:
		if el[0:3].lower() == word[0:3].lower():

			# going to assume nouns are being added by below lemma search
			#for end in endings:
			#	???

			lemmas.append(el.lower())

	lemmas = noDup(lemmas)
	#print "this is my lemmatizer"
	if len(lemmas) > 14:
		lemmas = lemmas[0:20]
		
	#print lemmas

	return lemmas



def synonyms(word):

	querysyns = semanticScore(word)[0] + [word]

	return querysyns


def swoogle(query, termbool):

	extraselectors = []
	if termbool is True:
		conceptSim = requests.get('http://swoogle.umbc.edu/SimService/GetSimilarity?operation=top_sim&word='+query.lower()+'&pos=NN&N=100&sim_type=concept&corpus=webbase&query=Get+Top-N+Most+Similar+Words'+query.lower())
	else:
		conceptSim = requests.get('http://swoogle.umbc.edu/SimService/GetSimilarity?operation=top_sim&word='+query.lower()+'&pos=NN&N=30&sim_type=concept&corpus=webbase&query=Get+Top-N+Most+Similar+Words'+query.lower())

	#relationSim = requests.get('http://swoogle.umbc.edu/SimService/GetSimilarity?operation=top_sim&word='+sys.argv[1]+'&pos=NN&N=100&sim_type=relation&corpus=webbase&query=Get+Top-N+Most+Similar+Words'+sys.argv[1])

	conceptSoup = BeautifulSoup(conceptSim.text)
	conceptTextArea = conceptSoup.findAll("textarea")
	conceptText = conceptTextArea[0].contents[0]


	lines = conceptText.split(",")
	for line in lines:
		line = line.strip()
		parts = line.split("_")

		extraselectors.append(parts[0])

	return extraselectors

def singplu(word):
	
	resp = requests.get("http://localhost:3333/singplu/"+word)
	ret = json.loads(resp.text)
	for i in range(0, len(ret)):
		ret[i] = urllib.unquote(ret[i]).decode('utf8') 
		
	return ret

def noDup(listy):
	
	return list(set(listy))

# all lemmas is whether you want to search for all lemmas to find the URI
# related is if you want to find related categories and their results in your scrape
# subqueries is if you want to find "subjectof" entries
# scrape pages that are not Category pages
def explore(query, subquery=True, findNoncats=True, allLemmas=True, related=False):

	subqueries = []
	wikipediaterms = []
	subcats = []
	abstract = []
	othercats = []
	relatedcontextsubqueries = {}
	relatedcontextcats = {}
	subcatsubqueries = {}
	results = {}
	category = False
	wikipediad = False
	relatedcats = []
	expansions = []


	wordnet = semanticScore(query)
	querysyns = wordnet[0]


	#do the fullfledged lemma search only on first keyword search
	if allLemmas:
		lemmas = lemmatize(query, querysyns) + [query]
		lemmas = noDup(lemmas)
	else:
		resp = requests.get("http://localhost:3333/singplu/"+query)
		ret = list(json.loads(resp.text))
		#print "singplu results"
		#print ret
		# get the plural first
		if type(ret) is not None and len(ret[0]) != 0:
			ret.reverse()
			lemmas = ret
		else:
			lemmas = [query]
	
	#print lemmas

	caturis = []
	pageuris = []
	alluris = []



	for lemma in lemmas:

		#print "FIND CATURI FOR LEMMA: " + str(lemma)

		caturi = ScrapeCategoryPage(lemma.capitalize())
		if caturi:
			#print "CATURI FOUND"
			caturis.append(urllib.unquote(caturi).decode('utf8'))
			alluris.append(caturi[37:])

			# don't look for singular if not all lemmas (just the plural)
			if not allLemmas:
				break


		if findNoncats:

			#print "FIND PAGEURI FOR LEMMA" + str(lemma)

			pageuri = ScrapePage(lemma.capitalize())

			#if pageuri:
				#print "FOUND"
			redirect = Sparql(lemma.capitalize().replace(" ","_"), "redirect")
			#print redirect
			if len(redirect) > 0 or redirect is None:
				#print "REDIRECT FOUND" + str(redirect[0])
				pageuri = ScrapePage(urllib.unquote(redirect[0][28:]).decode('utf8'))
			if pageuri and type(pageuri) is not list:
				#print "PAGEURI FOUND"
				pageuris.append(pageuri)
				alluris.append(pageuri[28:])



	caturis = noDup(caturis)
	#print "TOTAL CATURIS" + str(caturis) 
	pageuris = noDup(pageuris)
	#print "TOTAL pageuris" + str(pageuris)
	alluris = noDup(alluris)
	


	if caturis or pageuris:	
		for caturi in caturis:
			#print  "CAT URI" + str(caturi)
			uri = caturi
			#print "THIS IS A CATEGORY PAGE"
			if subquery:
				subjectof = conceptScrapeSubjectOf(uri)
				subqueries = subqueries + subjectof
				expansions = expansions + subqueries
				#print "ADDED SUBQUERIES FOR"  + str(query)
				#print subqueries

			broaderof = conceptScrapeBroaderOf(uri)

			
			caty = conceptScrapeBroader(uri)
			print "caty"
			print caty

			
			#print "subqueries" + str(subqueries)
	
			
			subcats = subcats + broaderof 
			expansions = expansions + subcats + caty
			#print "subcats" + str(subcats)
			
			catquery = conceptScrapeBroader(caturi)
			if related:
				prerelate(uri[37:], catquery, querysyns + wordnet[1], alluris, othercats, relatedcats)



	
		for pageuri in pageuris:

			print  "Page URI" + str(pageuri)
			uri = pageuri

			#print "PROBLEEEEM"
			#print type(uri)
			# dont want to add uri of the results are disambiguate (Cycling - Cycle)
			if type(uri) is list:

				#print "ambigous"
				for el in uri:
					results["disambiguate"].append(el[28:].replace("_", " "))
			
			else:
				catquery = ScrapeCategoryOf(uri)
				if catquery is not None and related:
				
					prerelate(uri[28:], catquery, querysyns + wordnet[1], alluris, othercats, relatedcats)

				'''
				#dont want to use wikipediaterms unless need to, less accurate
				if len(subqueries) < 4: 

					wikipediaterms = wikipediaterms + wikipediaTags(uri)
				'''
				expansions = expansions + catquery
		# If there are no results at all
	else:

		print "THERE ARE NO RESULTS AT ALL"

		results["subqueries"] = []
		results["subcats"] = []
		results["relatedcats"] = []
		results["othercats"] = []
		results["subcatsubqueries"] = []
		results["relatedcontextsubqueries"] = {}
		results["relatedcontextcats"] = {}
		#results["wikipediaterms"] = []
		results["disambiguate"] = []
		results["abstract"] = []

		return [results, expansions]


		# adding related category subcategories

	#print "RELATED CAT SUBQUERIES"
	if related:
		expansions = expansions + relatedcats
		for item in relatedcats:
			if "list" not in item and "terminology" not in item:
				uri = ScrapeCategoryPage(item.strip())
				#print uri

				if subquery:
					subjectof = conceptScrapeSubjectOf(uri)
					subjectof = subjectof
					relatedcontextsubqueries[item] = subjectof
					expansions = expansions + relatedcontextsubqueries[item]

				#print item + str(subjectof)
				broaderof = conceptScrapeBroaderOf(uri)
				cati= conceptScrapeBroader(uri)
				#print item + str(subjectof)
				temp = subjectof + broaderof
				
				relatedcontextcats[item] = cati + broaderof
				
				expansions = expansions + relatedcontextcats[item]
		#print "DONE"

	expansions = nerFilter(noDup(expansions))


	# removing dups in othercats

	othercontext1 = [item for item in othercats if item not in relatedcats]



	results["subqueries"] = subqueries
	#results["wikipediaterms"] = wikipediaterms
	results["subcats"] = subcats
	results["relatedcats"] = relatedcats
	results["othercats"] = othercontext1
	results["subcatsubqueries"] = subcatsubqueries
	results["relatedcontextsubqueries"] = relatedcontextsubqueries
	results["relatedcontextcats"] = relatedcontextcats

	results["peopleandorgs"] = peopleandorgs
	#results["abstract"] = wikipediaterms[1]

	
	#print "RESULTS FOR " + query
	#print results
	#print "the expansions"
	#print expansions
	return [results, expansions]
'''
processing full list
def ngramFilter(expansions, level):



	frequencies = {}

	resp = requests.get("http://localhost:3333/getfreq/"+str(expansions))
	
	ret = json.loads(resp.text)


	print ret 
	print "this is the json return"
	key = ret.keys()[0]
	frequencies[key] = ret[key]
	print "frequencies is now this"
	print frequencies


	if level == "low":
		print "low"

	elif level == "medium":
		print "medium"


	elif level == "high":
		print "high"

	
	print frequencies
	frequencies = sorted(x.items(), key=operator.itemgetter(1))
'''


def ngramFilter(query, qty, abstrlevel):

	#creativebook sends the expansions already
	if type(query) is list:
		expansions = query

	else:
		expansions = explore(query, False, False, True, False)[1]

	expansionlist = []

	for word in expansions:

		wordsplit = word.split(" ")

		
		#### removing words longer than two words
		if len(wordsplit) > 2:
			continue
		else:
		
			expansionlist.append(wordsplit)

	#print expansionlist

	resp = requests.post("http://localhost:3333/getfreq",{"list":urllib.quote(str(expansionlist))})
	
	ret = json.loads(resp.text)
	#print ret 
	#print "this is the json return"
	
	sortedexp = sorted(ret, key=lambda tup: tup[1],reverse=True)
	
	# only removes 0 frequency
	
	sortedexp = filter(lambda x: x[1] > 0 and x[1] < abstrlevel, sortedexp)
	print "filtered return" 
	print sortedexp


	if len(sortedexp) > qty:
		filtered =[i[0] for i in sortedexp][0:qty]
	else:
		filtered = [i[0] for i in sortedexp]

	print "ngram result"
	print filtered

	return filtered

#fashion marketing, technical support, urban planning and transporation
#for interdisciplinary studies, innovation centers, tackling today's biggest problems - exploratory

#def explore(query, subquery=True, findNoncats=True, allLemmas=True, related=False):
def expand(query, freq="5", distance="1", findsubquery = True, findrelated = False):
	

	# writing this for the serendipity example
	result = []
	distdict = {}
	childparent = {}
	newadds = []
	scraped = []
	i = 0
	while i < int(distance):
		
		print "this is round" + str((i+1))

		if i == 0:
			print "query is " + query
			sortedexp = explore(query, findsubquery, True, True, findrelated)[1]
			sortedexp = ngramFilter(sortedexp, int(freq)*3, 2000000)
			scraped.append(query)

			newadds = sortedexp
		
		#the last one
		elif i == (int(distance) - 1):
			print "last round"
			for el in sortedexp:
				print "query is " + el

				# don't do the ones that have already been analyses

				if el not in scraped:
					x = explore(el, findsubquery, False, False, False)[1]
					x = ngramFilter(x, int(freq), 2000000/(i+1))
					newadds = newadds + x


			sortedexp = newadds

		else:
			for el in sortedexp:

				print "query is " + el
				if el not in scraped:
					x = explore(el, findsubquery, False, False, False)[1]
					x = ngramFilter(x, int(freq), 2000000/(i+1))
					newadds = newadds + x
			scraped = scraped + sortedexp

			sortedexp = newadds
				
		if i != 0:
			distdict["distance "+str(i+1)] = noDup([x for x in newadds if x not in distdict["distance "+str(i)]])
		else:
			distdict["distance "+str(i+1)] = noDup(newadds)

		newadds = []
		
		result = noDup(sortedexp + result)

		print "this is result for round" + str((i+1))  
		print result
		print distdict


		if i == (int(distance) -1) and len(result) < 30:
			print "added a round"
			i = i
		else:
			i = i + 1
	
	
	#result = ngramFilter(result, 30, 2000000)


	return [result, distdict]


def creativeSearch(query):

	return expand(query, "5", "2")

def creativeSearchnosub(query):

	return expand(query, "5", "2", False, False)

def creativeBook(query):

	return expand(query, "5", "3", False, False)
# for yureeka

def creativeMaker(query):

	return expand(query, "5", "3")


def relatedFilter(query):
	return expand(query, "10", "1", True, True)


#consider removing subquery scrape for this (findNontCat = False)
def foreignLingo(query):
	
	return expand(query, "3", "2", False, False)



#print ngramFilter(sys.argv[1])

#creativeBook(sys.argv[1])

#creativeBook("fashion_design")
#print relatedFilter("Ring")
