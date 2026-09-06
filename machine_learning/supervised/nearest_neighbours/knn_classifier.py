import marimo

__generated_with = "0.16.2"
app = marimo.App(width="columns")


@app.cell(column=0, hide_code=True)
def _(mo):
    mo.md(r"""## Algorithm hyperparameters""")
    return


@app.cell
def _(mo):
    k = mo.ui.slider(start=1, stop=10, step=1)
    k
    return (k,)


@app.cell
def _(k):
    print(f"{k.value=}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Create dataset""")
    return


@app.cell
def _(ScatterWidget):
    scatter_widget = ScatterWidget()
    scatter_widget
    return (scatter_widget,)


@app.cell
def _(np, scatter_widget):
    dataset = scatter_widget.data_as_pandas

    X_train = np.array(dataset.loc[dataset["label"] != "c", ["x", "y"]].values.tolist())
    y_train = np.array(dataset.loc[dataset["label"] != "c", "label"].values.tolist())

    X_predict = np.array(dataset.loc[dataset["label"] == "c", ["x", "y"]].values.tolist())
    return X_predict, X_train, y_train


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Imports""")
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from collections import Counter
    from drawdata import ScatterWidget
    return Counter, ScatterWidget, mo, np


@app.cell(column=1)
def _(Counter, np):
    class KNNClassifier:
        """Class for classification according to the KNN-algorithm."""
        def __init__(
            self,
            k: int,
            distance_metric: str = "euclidean"
        ) -> None:
            """Initialising the KNNClassifier class."""
            self.k = k
            self.distance_metric = distance_metric

            self.X_train = None
            self.y_train = None

        def _compute_distance(
            self,
            x1: list[float],
            x2: list[float]
        ) -> float:
            if self.distance_metric == "euclidean":
                return np.sqrt(np.sum((x1 - x2) ** 2))
            else:
                raise NotImplementedError

        def _get_neighbors(
            self,
            x
        ) -> list[int]:
            """"""
            distances = [self._compute_distance(x, xt) for xt in self.X_train]
            neighbors_idx = np.argsort(distances)[:self.k]

            return neighbors_idx

        def fit(
            self,
            X: list[float],
            y: list[float],
        ) -> None:
            """Get training data."""
            self.X_train = X
            self.y_train = y

        def predict(
            self,
            X: list[float]
        ) -> np.array:
            """Predict"""
            results = []
        
            for x in X:
                idx = self._get_neighbors(x)
                labels = self.y_train[idx]
                most_common_class = Counter(labels).most_common(1)
                results.append(most_common_class[0][0])

            return np.array(results)
    return (KNNClassifier,)


@app.cell
def _(KNNClassifier, X_predict, X_train, y_train):
    knn_classifier = KNNClassifier(k=3)

    knn_classifier.fit(
        X=X_train,
        y=y_train
    )

    knn_classifier.predict(X=X_predict)
    return


if __name__ == "__main__":
    app.run()
