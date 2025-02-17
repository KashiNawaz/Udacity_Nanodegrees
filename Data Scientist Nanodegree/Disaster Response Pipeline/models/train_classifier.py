import sys
import nltk
nltk.download('punkt')
nltk.download('wordnet')

import pickle
import pandas as pd
from sqlalchemy import create_engine, inspect
from sklearn.externals import joblib
import re

from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import AdaBoostClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def load_data(database_filepath):
    engine = create_engine('sqlite:///' + database_filepath)
    inspector = inspect(engine)
    table=inspector.get_table_names()
    df = pd.read_sql_table(table[0], engine)
    print(df.columns)
    X = df.message
    y = df.iloc[:,4:]
    categories = y.columns.tolist()
    return X,y,categories


def tokenize(text):
    sentence = re.sub('\W',' ',text)
    tokens = word_tokenize(sentence.lower().strip())
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(i,'n') for i in tokens]
    tokens = [lemmatizer.lemmatize(i,'v') for i in tokens]
    return tokens


def build_model():
    adaboost_pipeline = Pipeline([
        ('vect',CountVectorizer(tokenizer = tokenize, stop_words = None)),
        ('tfidf',TfidfTransformer(use_idf = True)),
        ('clf', MultiOutputClassifier(AdaBoostClassifier(n_estimators=70, learning_rate = 0.5)))
	])
    return adaboost_pipeline


def evaluate_model(model, X_test, Y_test, category_names):
    y_pred = model.predict(X_test)
    for i, col in enumerate(category_names): 
        print('**********:',col,':***********')
        print(classification_report(Y_test.iloc[:,i], y_pred[:,i]))


def save_model(model, model_filepath):
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()