import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import json
import random
from .train_chatbot import train_chat
import tensorflow as tf

lemmatizer = WordNetLemmatizer()


def bot_reply(msg, dir_name):
    intents = json.loads(open(dir_name+'fil.json').read())
    words = pickle.load(open(dir_name+'words.pkl', 'rb'))
    classes = pickle.load(open(dir_name+'classes.pkl', 'rb'))

    def clean_up_sentence(sentence):
        # tokenize the pattern - split words into array
        sentence_words = nltk.word_tokenize(sentence)
        # stem each word - create short form for word
        sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

    def bow(sentence, words, show_details=True):
        # tokenize the pattern
        sentence_words = clean_up_sentence(sentence)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        return(np.array(bag))

    def predict_class(sentence, model):
        # filter out predictions below a threshold
        p = bow(sentence, words,show_details=False)
        print('sentence: ', sentence)
        print('p: ', p)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.7
        print(res)
        results = [[i, r] for i, r in enumerate(res) if r >= ERROR_THRESHOLD]
        print(results)
        # sort by strength of probability
        return_list = []
        if len(results) != 0:
            results.sort(key=lambda x: x[1], reverse=True)
            for r in results:
                return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

        return return_list

    def getResponse(ints, intents_json):
        tag = ints[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if(i['tag']== tag):
                result = random.choice(i['answer'])
                break
        return result

    def chatbot_response(msg):
        model = tf.keras.models.load_model(dir_name+'chatbot_model.h5')
        ints = predict_class(msg, model)
        if len(ints) != 0:
            res = getResponse(ints, intents)
        else:
            res = 'System can not answer this question. Would you like to talk to our customer care service.'
        return res

    return chatbot_response(msg)


