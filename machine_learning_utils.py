from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer

from sklearn import svm
from pickle import load
from database_utils import normalize_text
from sklearn.cross_validation import KFold
from nltk.stem import RSLPStemmer, SnowballStemmer
from sklearn.base import TransformerMixin, BaseEstimator
from database_utils import DatabaseConnector, build_dataframe
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score

import nltk
import numpy as np

class MLWrapper:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def split_data(self, input_data, ratio):
        labels = input_data['labels'].unique().tolist()
        full_data = {label: input_data[input_data['labels'] == label] for label in labels}
        train_data = {label: input_data[input_data['labels'] == label] for label in labels}


    def train(self, data, n_classes):
        """

        :param data:  dataframe with columns text, label
        :return:
        """
        k_fold = KFold(n=len(data), n_folds=6)
        scores = []
        accuracies = []
        confusion = []#numpy.zeros([n_classes, n_classes])
        for train_indices, test_indices in k_fold:
            train_text = data.iloc[train_indices]['texts'].values
            train_y = data.iloc[train_indices]['labels'].values

            test_text = data.iloc[test_indices]['texts'].values
            test_y = data.iloc[test_indices]['labels'].values

            self.pipeline.fit(train_text, train_y)
            predictions = self.pipeline.predict(test_text)

            # confusion += confusion_matrix(test_y, predictions)
            if confusion == []:
                confusion = confusion_matrix(test_y, predictions)
            else:
                confusion += confusion_matrix(test_y, predictions)

            score = f1_score(test_y, predictions)
            accuracy = accuracy_score(test_y, predictions, normalize=True)

            scores.append(score)
            accuracies.append(accuracy)

        print('Total news classified:', len(data))
        print('Score:', sum(scores) / len(scores))
        print('Accuracy:', sum(accuracies) / len(accuracies))
        print('Confusion matrix:')
        print(confusion)

class AdjectiveVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, adj_list):
        self. adj_list = adj_list

    def fit(self, X, y=None, **fit_params):
        return np.matrix([self.adjective_vectorizer(s, self.adj_list) for s in X])

    def fit_transform(self, X, y=None, **fit_params):
        return np.matrix([self.adjective_vectorizer(s, self.adj_list) for s in X])

    def transform(self, X, **fit_params):
        return np.matrix([self.adjective_vectorizer(s, self.adj_list) for s in X])

    def adjective_vectorizer(self, sentence, base_adjectives, form="vector"):
        normalized_sentence = normalize_text(sentence)
        v = {adjective: normalized_sentence.split().count(adjective) for adjective in base_adjectives}
        if form == "dict":
            return v
        if form == "vector":
            return list(v.values())
class Stemmer():
    def __init__(self):
        f = open('bigram_tagger.pkl','rb')
        self.tagger = load(f)
        f.close()
        pass

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **fit_params):
        stemmer = RSLPStemmer()

        listParagraphs = X.tolist()
        stemmed_paragraphs = []

        for paragraph in listParagraphs:
            words = paragraph.split()
            stemmed_words = []
            for word in words:
                tag = self.tagger.tag([word])
                if tag[0][1] == "NPROP":
                    continue
                stemmed_words.append(stemmer.stem(word))
            text = ''.join(w + ' ' for w in stemmed_words).strip()
            stemmed_paragraphs.append(text)

        return stemmed_paragraphs

class Tagger():
    def __init__(self, filename):
        f = open(filename, 'rb')
        self.tagger = load(f)
        f.close()

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **fit_params):
        pass


def get_data_from_db(sentiment = None):
    db_connector = DatabaseConnector('localhost', 'root', '12345', 'CORPUS_VIES')
    if sentiment != None:
        retrieved_data = db_connector.getDataBySentiment(sentiment)
    else:
        retrieved_data = db_connector.getDataTextAndLabel()

    return retrieved_data

def load_tagger():
    f = open('bigram_tagger.pkl', 'rb')
    tagger = load(f)
    f.close()
    return tagger

def get_all_adjectives():
    corpus = get_data_from_db()
    corpus = corpus['texts'].tolist()
    tagger = load_tagger()

    adjectives = set()
    for text in corpus:
        adjectives_found = set([word for (word, tag) in tagger.tag(text.split()) if tag[:3] == 'ADJ'])
        adjectives = adjectives.union(adjectives_found)

    print("Numero de adjetivos encontrados: ", len(adjectives))
    return adjectives
# if __name__ == "__main__":
    # print("Recuperando os textos")
    # db_connector = DatabaseConnector('localhost', 'root', '12345', 'CORPUS_VIES')
    # retrieved_data = build_dataframe(db_connector.getDataTextAndLabel())
    #
    # print("Treinando o modelo")
    # ml_wrapper = MLWrapper(svm.SVC(C=316))
    # # ml_wrapper = MLWrapper(MultinomialNB())
    # ml_wrapper.train(retrieved_data)