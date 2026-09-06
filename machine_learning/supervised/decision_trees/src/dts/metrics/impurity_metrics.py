"""Module for impurity metric computations (Gini, entropy, variance, etc.)."""


def compute_gini(labels: list) -> float:
    """Compute Gini impurity for a group of class labels.

    Gini = 1 - Σ(p_i)², where p_i is the proportion of class i.

    Args:
        labels (list): Class labels for a group.

    Returns:
        gini (float): Gini impurity value (0 = pure, 1 = mixed).
    """
    if len(labels) == 0:
        return 0.0

    # Count occurrences of each class
    class_counts = {}
    for label in labels:
        class_counts[label] = class_counts.get(label, 0) + 1

    # Compute Gini: 1 - Σ(p_i)²
    gini = 1.0
    total = len(labels)
    for count in class_counts.values():
        proportion = count / total
        gini -= proportion**2

    return gini
