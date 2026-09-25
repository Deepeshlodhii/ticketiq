import csv
import random
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report


class LogisticRegressionScratch:
    """
    Multiclass Logistic Regression implemented using NumPy.

    We use sklearn only for TF-IDF vectorization and evaluation metrics.
    """

    def __init__(self, learning_rate=0.1, epochs=500, reg_strength=0.01):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.reg_strength = reg_strength

        self.weights = None
        self.bias = None
        self.classes = None

    @staticmethod
    def _softmax(z):
        z = z - np.max(z, axis=1, keepdims=True)
        exp_z = np.exp(z)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    def fit(self, X, y):
        self.classes = np.unique(y)

        n_samples, n_features = X.shape
        n_classes = len(self.classes)

        class_to_index = {
            class_name: index for index, class_name in enumerate(self.classes)
        }

        y_encoded = np.array([class_to_index[label] for label in y])

        self.weights = np.zeros(
            (n_features, n_classes),
            dtype=np.float64,
        )

        self.bias = np.zeros(n_classes, dtype=np.float64)

        # One-hot encoded target matrix
        y_one_hot = np.zeros(
            (n_samples, n_classes),
            dtype=np.float64,
        )

        y_one_hot[
            np.arange(n_samples),
            y_encoded,
        ] = 1

        for _ in range(self.epochs):
            logits = X @ self.weights + self.bias
            probabilities = self._softmax(logits)

            # Cross-entropy gradient
            error = probabilities - y_one_hot

            grad_weights = X.T @ error / n_samples + self.reg_strength * self.weights

            grad_bias = np.mean(error, axis=0)

            self.weights -= self.learning_rate * grad_weights

            self.bias -= self.learning_rate * grad_bias

    def predict_proba(self, X):
        logits = X @ self.weights + self.bias
        return self._softmax(logits)

    def predict(self, X):
        probabilities = self.predict_proba(X)

        predicted_indices = np.argmax(
            probabilities,
            axis=1,
        )

        return self.classes[predicted_indices]


class TicketClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=3000,
        )

        self.model = LogisticRegressionScratch(
            learning_rate=0.5,
            epochs=700,
            reg_strength=0.01,
        )

        self.is_trained = False

    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)

        # Convert sparse TF-IDF matrix to dense NumPy array.
        X = X.toarray()

        self.model.fit(
            X,
            np.array(labels),
        )

        self.is_trained = True

    def predict(self, text):
        if not self.is_trained:
            raise RuntimeError("Classifier has not been trained.")

        X = self.vectorizer.transform([text]).toarray()

        prediction = self.model.predict(X)[0]

        probabilities = self.model.predict_proba(X)[0]

        confidence = float(np.max(probabilities))

        return prediction, confidence


def load_dataset(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    texts = [row["text"] for row in rows]
    labels = [row["category"] for row in rows]

    return texts, labels


def train_test_split(texts, labels, test_size=0.2):
    indices = list(range(len(texts)))

    random.Random(42).shuffle(indices)

    split_index = int(len(indices) * (1 - test_size))

    train_indices = indices[:split_index]
    test_indices = indices[split_index:]

    X_train = [texts[i] for i in train_indices]
    X_test = [texts[i] for i in test_indices]

    y_train = [labels[i] for i in train_indices]
    y_test = [labels[i] for i in test_indices]

    return X_train, X_test, y_train, y_test


def evaluate_classifier():
    dataset_path = Path(__file__).resolve().parents[2] / "data" / "tickets.csv"

    texts, labels = load_dataset(dataset_path)

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=3000,
    )

    X_train_vectorized = vectorizer.fit_transform(X_train).toarray()

    X_test_vectorized = vectorizer.transform(X_test).toarray()

    model = LogisticRegressionScratch(
        learning_rate=0.5,
        epochs=700,
        reg_strength=0.01,
    )

    model.fit(
        X_train_vectorized,
        np.array(y_train),
    )

    predictions = model.predict(X_test_vectorized)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print("\n=== TicketIQ Classifier Evaluation ===")
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
        )
    )

    return model, vectorizer


if __name__ == "__main__":
    evaluate_classifier()
