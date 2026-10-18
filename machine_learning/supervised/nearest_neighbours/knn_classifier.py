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

    from drawdata import ScatterWidget
    from knn.knn_classifier import KNNClassifier
    return KNNClassifier, ScatterWidget, mo, np


@app.cell(column=1)
def _(KNNClassifier, X_predict, X_train, k, y_train):
    knn_classifier = KNNClassifier(k=k.value)

    knn_classifier.fit(
        X=X_train,
        y=y_train
    )

    knn_classifier.predict(X=X_predict)
    return


if __name__ == "__main__":
    app.run()
