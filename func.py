import pandas as pd
import pymorphy2
import nltk
import scipy
import string
import json

morph = pymorphy2.MorphAnalyzer()
nltk.download('popular')


def tokenise(data):
    tokens = nltk.word_tokenize(data)

    tokens = [i for i in tokens if (i not in string.punctuation)]

    ##stop_words = nltk.corpus.stopwords.words('russian')
    ##stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
    ##tokens = [i for i in tokens if ( i not in stop_words )]

    ##tokens = [i.replace("«", "").replace("»", "") for i in tokens]

    return tokens


def selectTopLemma(lemmaObjs):
    top = lemmaObjs[0]
    for lemmaObj in lemmaObjs:
        if lemmaObj.score > top.score:
            top = lemmaObj
    return top


def lemmatize(token):
    forms = []
    forms = list(morph.parse(token))
    return selectTopLemma(forms).normal_form


# Превращает текст в список слов в нормальной форме.
def tok_lem_single(text):
    res = []
    for token in tokenise(text):
        res.append(lemmatize(token))
    return res


# Превращает корпус текстов в корпус затокенизированных текстов.
def tok_lem_corpus(corpus):
    res = []
    for text in corpus:
        res.extend(tok_lem_single(text))
    return res


# Собирает мешок слов.
def counter_bag(sentences):
    tok_sentences = list({'sentence': sentence, 'tok_sentence': tok_lem_single(sentence)} for sentence in sentences)
    all_tokens = set(tok_lem_corpus(sentences))
    vectors = [[tok_s['tok_sentence'].count(token) for token in all_tokens] for tok_s in tok_sentences]
    return {'tokens': all_tokens, 'vectors': vectors, 'sentences': sentences}


# Считает лучшее косинусное расстояние от предложения до корпуса.
def cosinusize(sentence, bag):
    tok_s = tok_lem_single(sentence)
    vec_s = list(tok_s.count(token) for token in bag['tokens'])
    distances = list({'dist': scipy.spatial.distance.cosine(vec_s, bag['vectors'][i]), 'ind': i} for i, sen in enumerate(bag['sentences']))
    return top_dist(distances)


def top_dist(distances):
    top = distances[0]
    for dist in distances:
        if dist['dist'] < top['dist']:
            top = dist
    return top


# Узнать у бота самую подходящую вакансию.
# Выбирает самый близкий по косинусному рассстоянию текст и выдает название соответствующей вакансии.
def ask_bot(question, data_bag, raw_data):
    cosinusized = cosinusize(question, data_bag)
    vacansion = list(raw_data['name'].values())[cosinusized['ind']]
    descroption = list(raw_data['description'].values())[cosinusized['ind']]
    return [vacansion, cosinusized['ind'], descroption]


#Загрузить готовую модель (мешок) из файла.
def get_bag(filename='databag.txt'):
    with open(filename, 'r', encoding='utf-8') as file:
        res = json.loads(s=file.read(), encoding='utf-8')
        return res


#Загрузить изначальные данные.
def get_raw_data(filename='text_perm_it_job_description.csv'):
    return pd.read_csv(filename, sep=';').to_dict()

