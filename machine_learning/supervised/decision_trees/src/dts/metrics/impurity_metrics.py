"""Module for impurity metric computations (Gini, entropy, variance, etc.)."""


def compute_gini(target_labels: list) -> float:
    """Compute Gini impurity for a group of class target_labels.

    Gini = 1 - Σ(p_i)², where p_i is the proportion of class i.

    Args:
        target_labels (list): Class target_labels for a group.

    Returns:
        gini (float): Gini impurity value (0 = pure, 1 = mixed).
    """
    if len(target_labels) == 0:
        return 0.0

    # Count occurrences of each class
    class_counts = {}
    for label in target_labels:
        class_counts[label] = class_counts.get(label, 0) + 1

    # Compute Gini: 1 - Σ(p_i)²
    gini = 1.0
    total = len(target_labels)

    for count in class_counts.values():
        proportion = count / total
        gini -= proportion**2

    return gini


def compute_weighted_gini(
    gini_left: float, gini_right: float, n_left: int, n_right: int
) -> float:
    """Compute weighted Gini impurity for the split.

    Args:
        gini_left (float): Gini impurity of left child.
        gini_right (float): Gini impurity of right child.
        n_left (int): Number of samples in left child.
        n_right (int): Number of samples in right child.

    Returns:
        weighted_gini (float): Weighted Gini across both children.
    """
    n_total = n_left + n_right

    if n_total == 0:
        return 0.0

    weighted_gini = (n_left / n_total) * gini_left + (n_right / n_total) * gini_right

    return weighted_gini
