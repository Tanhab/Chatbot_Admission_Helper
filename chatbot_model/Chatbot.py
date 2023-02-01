import tensorflow as tf
from nltk.stem import WordNetLemmatizer
import nltk
from abc import ABCMeta, abstractmethod

import random
import json
import pickle
import numpy as np
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# from tf.keras.models import Sequential
# from tensorflow.keras.layers import Dense, Dropout
# from tensorflow.keras.optimizers import gradient_descent_v2
# from tensorflow.keras.models import load_model

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)


class IAssistant(metaclass=ABCMeta):

    @abstractmethod
    def train_model(self):
        """ Implemented in child class """

    @abstractmethod
    def request_tag(self, message):
        """ Implemented in child class """

    @abstractmethod
    def get_tag_by_id(self, id):
        """ Implemented in child class """

    @abstractmethod
    def request_method(self, message):
        """ Implemented in child class """

    @abstractmethod
    def request(self, message):
        """ Implemented in child class """


class GenericAssistant(IAssistant):

    def __init__(self, load=False, model_name="test_model"):
        self.root_directory = "D:\deep learning\Chatbot_Admission_Helper\chatbot_model"
        self.intents = os.path.join(self.root_directory, "intents.json")
        self.model_name = model_name

        self.load_json_intents(self.intents)
        self.lemmatizer = WordNetLemmatizer()

        if load:
            self.load_model()
        else:
            self.train_model()
            self.save_model()

    def load_json_intents(self, intents):
        self.intents = json.loads(open(intents).read())

    def train_model(self):

        self.words = []
        self.classes = []
        documents = []
        ignore_letters = ['!', '?', ',', '.']

        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                word = nltk.word_tokenize(pattern)
                self.words.extend(word)
                documents.append((word, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = [self.lemmatizer.lemmatize(
            w.lower()) for w in self.words if w not in ignore_letters]
        self.words = sorted(list(set(self.words)))

        self.classes = sorted(list(set(self.classes)))

        training = []
        output_empty = [0] * len(self.classes)

        for doc in documents:
            bag = []
            word_patterns = doc[0]
            word_patterns = [self.lemmatizer.lemmatize(
                word.lower()) for word in word_patterns]
            for word in self.words:
                bag.append(1) if word in word_patterns else bag.append(0)

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training)

        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        self.model = tf.keras.models.Sequential()
        self.model.add(tf.keras.layers.Dense(
            128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(tf.keras.layers.Dropout(0.5))
        self.model.add(tf.keras.layers.Dense(64, activation='relu'))
        self.model.add(tf.keras.layers.Dropout(0.5))
        self.model.add(tf.keras.layers.Dense(
            len(train_y[0]), activation='softmax'))

        sgd = tf.keras.optimizers.legacy.SGD(
            lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer=sgd, metrics=['accuracy'])

        self.hist = self.model.fit(np.array(train_x), np.array(
            train_y), epochs=200, batch_size=5, verbose=1)

    def save_model(self, model_name=None):
        if model_name is None:
            self.model.save(os.path.join(
                self.root_directory, "test_model.h5"), self.hist)
            pickle.dump(self.words, open(os.path.join(
                self.root_directory, 'test_model_words.pkl'), 'wb'))
            pickle.dump(self.classes, open(
                os.path.join(self.root_directory, 'test_model_classes.pkl'), 'wb'))
        else:
            self.model.save(f"{model_name}.h5", self.hist)
            pickle.dump(self.words, open(f'{model_name}_words.pkl', 'wb'))
            pickle.dump(self.classes, open(f'{model_name}_classes.pkl', 'wb'))

    def load_model(self, model_name=None):
        if model_name is None:
            self.words = pickle.load(
                open(os.path.join(self.root_directory, 'test_model_words.pkl'), 'rb'))
            self.classes = pickle.load(
                open(os.path.join(self.root_directory, 'test_model_classes.pkl'), 'rb'))
            self.model = tf.keras.models.load_model(
                os.path.join(self.root_directory, "test_model.h5"))
        else:
            self.words = pickle.load(
                open(os.path.join(self.root_directory, 'test_model_words.pkl'), 'rb'))
            self.classes = pickle.load(
                open(os.path.join(self.root_directory, 'test_model_classes.pkl'), 'rb'))
            self.model = tf.keras.models.load_model(
                os.path.join(self.root_directory, "test_model.h5"))

    def _clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(
            word.lower()) for word in sentence_words]
        return sentence_words

    def _bag_of_words(self, sentence, words):
        sentence_words = self._clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, word in enumerate(words):
                if word == s:
                    bag[i] = 1
        return np.array(bag)

    def _predict_class(self, sentence):
        p = self._bag_of_words(sentence, self.words)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.1
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append(
                {'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def _get_response(self, ints, intents_json):
        try:
            tag = ints[0]['intent']
            list_of_intents = intents_json['intents']
            for i in list_of_intents:
                if i['tag'] == tag:
                    result = {
                        'tag': tag,
                        'probability': ints[0]['probability'],
                        'reply': random.choice(i['responses'])}
                    break
        except IndexError:
            result = "I don't understand!"
        return result

    def request_tag(self, message):
        pass

    def get_tag_by_id(self, id):
        pass

    def request_method(self, message):
        pass

    def request(self, message):
        ints = self._predict_class(message)
        # print(ints)
        return self._get_response(ints, self.intents)
