import spacy
import math
import operator
import ast

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from summarizer import Summarizer
from spacy.lang.ru import Russian
from spacy.lang.it import Italian
from summarizer.sentence_handler import SentenceHandler
from pymorphy2 import MorphAnalyzer

from .models import Document, Note


nlp_it = spacy.load("it_core_news_md")
stop_words = set(stopwords.words('russian') + stopwords.words('italian'))
analyzer = MorphAnalyzer()


def read_and_save_file(file, theme):
    text = file.read().decode('utf-8')
    name = file.name
    lang = get_language(text)
    document = Document(name=name, text=text, theme=theme, language=lang)
    document.save()
    return document


def count_documents_with_word(word, theme, lang):
    count = 0
    documents = Document.objects.filter(theme=theme, language=lang)
    for item in documents:
        words_dict = ast.literal_eval(item.args)
        words = list(words_dict.keys())
        if word in words:
            count += 1
    return count


def tokenize(words_in_doc, theme, lang, word, count):
    max_value = int(get_max_value(words_in_doc))
    count_doc = int(Document.objects.filter(theme=theme, language=lang).count())
    count_doc_with_word = int(count_documents_with_word(word, theme, lang))
    idf = 0.5 * (1 + int(count)/max_value) * math.log(count_doc/count_doc_with_word)
    return idf


def get_language(text):
    ru_al = 'абвгдеёжзийклмопрстуфхцчшщъыьэюя'
    it_al = 'abcdefghijklmnopqrstuvwxyzìíòóú'
    count_ru = 0
    count_it = 0
    for k in text:
        for j in ru_al:
            if k == j:
                count_ru += 1
        for l in it_al:
            if k == l:
                count_it += 1
    if count_ru > count_it:
        lang = 'russian'
    else:
        lang = 'italian'
    return lang


def weight_sentence(sentence, sentences, doc):
    text = ''
    for sent in sentences:
        if sent == sentence:
            break
        text += sent
    text.replace(' ', '')
    n = len(doc.replace(' ', ''))
    m = len(text)
    return 1 - m / n


def weight_sentence_in_paragraph(sentence, document):
    doc = document.split('\n')
    for paragraph in doc:
        sentences = sent_tokenize(paragraph)
        for sent in sentences:
            if sent == sentence:
                return weight_sentence(sentence, sentences, document)


def get_sorted_sentence(sentences, nlp, text, args, theme, lang):
    dict_with_weight = {}
    for sentence in sentences:
        words = get_words(sentence, nlp)
        summ = 0
        for word in words:
            summ += words[word] * tokenize(args, theme, lang, word, words[word])
        weight1 = weight_sentence(sentence, sentences, text)
        weight2 = weight_sentence_in_paragraph(sentence, text)
        dict_with_weight.update({sentence: summ * weight1 * weight2})
    return sorted(dict_with_weight.items(), key=operator.itemgetter(1))


def get_sorted_sentence_for_ru(sentences, text, args, theme, lang):
    dict_with_weight = {}
    for sentence in sentences:
        words = get_words_for_ru(sentence)
        summ = 0
        for word in words:
            summ += words[word] * tokenize(args, theme, lang, word, words[word])
        weight1 = weight_sentence(sentence, sentences, text)
        weight2 = weight_sentence_in_paragraph(sentence, text)
        dict_with_weight.update({sentence: summ * weight1 * weight2})
    return sorted(dict_with_weight.items(), key=operator.itemgetter(1))


def generate(sentences, sorted_sentences):
    count_sent = 0
    note = ''
    for sent1 in sentences:
        for sent2, key in sorted_sentences:
            if sent1 == sent2:
                if count_sent == 9:
                    break
                else:
                    count_sent += 1
                    note += sent1
    return note


def get_weight_sentence(document):
    text = document.text
    theme = document.theme
    lang = document.language
    nlp = nlp_it
    if lang == 'italian':
        model = Summarizer(sentence_handler=SentenceHandler(language=Italian))
        args = get_words(text, nlp)
    else:
        model = Summarizer(sentence_handler=SentenceHandler(language=Russian))
        args = get_words_for_ru(text)
    document.args = str(args)
    document.save()
    sentences = sent_tokenize(text)
    if lang == 'italian':
        sorted_sentences = get_sorted_sentence(sentences, nlp, text, args, theme, lang)
    else:
        sorted_sentences = get_sorted_sentence_for_ru(sentences, text, args, theme, lang)
    note = generate(sentences, sorted_sentences)
    note_with_ml = model(text)
    note_item = Note(document_id=document, text=note, text_for_algo="", text_for_ml=note_with_ml)
    note_item.save()


def get_max_value(words):
    max_value_dict = {x: y for x, y in filter(lambda x: words[x[0]] == max(words.values()), words.items())}
    max_value = list(max_value_dict.values())
    max_value = max_value[0]
    return max_value


def get_words(text, nlp):
    words = {}
    for raw_word in text.split():
        if raw_word.endswith((',', '.', '-', '!', '?', ';', ':')):
            word = raw_word[:-1]
        else:
            word = raw_word
        try:
            int(word)
        except ValueError:
            if not word == '':
                token = nlp(word)
                word = token[0].lemma_
                if word not in stop_words:
                    if word in words:
                        words[word] += 1
                    else:
                        words[word] = 1
    return words


def get_words_for_ru(text):
    words = {}
    for raw_word in text.split():
        if raw_word.endswith((',', '.', '-', '!', '?', ';', ':')):
            word = raw_word[:-1]
        else:
            word = raw_word
        try:
            int(word)
        except ValueError:
            if not word == '':
                token = analyzer.parse(word)
                word = token[0].normal_form
                if word not in stop_words:
                    if word in words:
                        words[word] += 1
                    else:
                        words[word] = 1
    return words
