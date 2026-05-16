import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


def train_model():
    try:
        df = pd.read_csv("intents.csv")
    except FileNotFoundError:
        raise FileNotFoundError("intents.csv not found. Please make sure the file exists in the project root.")

    # Features & labels
    X = df["text"]
    y = df["label"]

    # Convert text → numbers
    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    # Train model
    model = MultinomialNB()
    model.fit(X_vec, y)

    # Save model
    pickle.dump(model, open("model.pkl", "wb"))
    pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

    print("Model trained successfully")


if __name__ == "__main__":
    train_model()