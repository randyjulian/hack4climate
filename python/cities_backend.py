from flask import Flask
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import json

import spacy
nlp = spacy.load("en_core_web_lg")

commitments = pd.read_pickle("commitments_translated.pkl")
commitments = commitments[commitments.entity_type == 'City']
cities = commitments.name.unique()

city = 'Paris'
commitment_info_keys = ['action_co2_reduction', 'action_end_year', 
                        'action_start_year', 'action_target_year', 
                        'baseline_emissions', 'baseline_year', 
                        'est_target_year_emissions', 'estimated_tonnes_reduced', 
                        'estimated_tons_reduced', 'ghg_reduction_target']

commitment_info_keys = [x for x in commitments.columns if commitments[x].dtype == 'float64']

def drop_useless_words(text):
    acceptedTokens = {'NN', 'NNS', 'JJ', 'VBG', 'VBP'}
    doc = nlp(text)
    results = []
    for token in doc:
        if token.tag_ in acceptedTokens:
            results.append(token.lemma_)
    return ' '.join(results)

#actions_corpus = [drop_useless_words(x) for x in commitments.action_description_en.dropna()]
#with open("actions_corpus.pkl", "wb") as f:
#    pickle.dump(actions_corpus, f)
with open("actions_corpus.pkl", "rb") as f:
    actions_corpus = pickle.load(f)
vectorizer = TfidfVectorizer()
vectorizer.fit(actions_corpus)
city_actions_keywords = {}

def get_cities():
    return cities

def get_commitments(city):
    return commitments[commitments.name == city]

def clean(x):
    out = x.replace("\n", " ").replace("\r", " ").replace("\\", "")
    while "  " in out:
        out = out.replace("  ", " ")
    return out


#for city in cities:
#    subset = get_commitments(city)
#    actions = list(drop_useless_words(clean(x)) for x in subset.action_description_en.dropna())
#    result = []
#    if len(actions) > 0:
#        X = vectorizer.transform(actions)
#        scores = pd.DataFrame(X.toarray())
#        scores.columns = vectorizer.get_feature_names()
#        scores = scores.aggregate(np.mean)
#        scores = scores[scores > 0].sort_values(ascending=False)
#        scores = pd.DataFrame(scores[:30]).reset_index()
#        scores.columns = ['word', 'score']
#        result = scores.to_json(orient='records')
#    city_actions_keywords[city] = result
#
#with open("city_actions_keywords.pkl", "wb") as f:
#    pickle.dump(city_actions_keywords, f)

with open("city_actions_keywords.pkl", "rb") as f:
    city_actions_keywords = pickle.load(f)

def get_city_info(city):
    results = {}
    results['info'] = {}
    results['actions'] = {}
    subset = get_commitments(city)
    for key in commitment_info_keys:
        results['info'][key] = subset[key].max()
    results['actions'] = list(clean(x) for x in subset.action_description_en.dropna())
    keywords = json.loads(city_actions_keywords[city])
    results['actions_keywords'] = keywords
    
    partnerActionCities = []
    
    for otherCity in cities:
        otherKeywords = city_actions_keywords[otherCity]
        if len(otherKeywords) == 0:
            continue
        otherKeywords = json.loads(otherKeywords)
        keywordScore = 0
        for pair in keywords:
            for otherPair in otherKeywords:
                if pair['word'] == otherPair['word']:
                    keywordScore += pair['score'] * otherPair['score']
        if keywordScore > 0:
            partnerActionCities.append([otherCity, keywordScore, sorted(otherKeywords, key=lambda x: -x['score'])[:10]])
    
    results['partnerActionCities'] = sorted(partnerActionCities, key=lambda x: -x[1])[:10]
    
    return results