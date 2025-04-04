"""Utility."""

from collections import namedtuple
from typing import Any, Callable, Dict, Hashable, Iterable, Set, Tuple, Union

import numpy as np
import pandas as pd
from strenum import StrEnum

Result = namedtuple("Result", ["score", "reg_alpha", "is_neg", "min_weights"])


class TaskType(StrEnum):
    """Solvable task types."""

    BIN: "TaskType" = "BIN"  # type: ignore
    REG: "TaskType" = "REG"  # type: ignore


def drop_keys(dict_: Dict, keys: Iterable[Hashable]) -> Dict:
    """Drop multiple keys from dict.

    Args:
        dict_: Dictionary.
        keys: Dropped keys.

    Returns:
        Filtered dictornary.

    """
    for key in keys:
        dict_.pop(key)
    return dict_


def flatten(d: dict, parent_key: str = "", sep: str = "_"):
    """Flatten Dictionary of dictionaries.

    Args:
        d: Dictionary with nested dictionaries.
        parent_key: Parent outer key.
        sep: Separator for merged keys.

    Returns:
        Expanded Dictionary.

    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_task_type(values: np.ndarray) -> TaskType:
    """Determine task type.

    Args:
        values: Array of values.

    Returns:
        task.

    """
    n_unique_values = np.unique(values).shape[0]

    task: str
    if n_unique_values == 1:
        raise RuntimeError("Only unique value in target")
    elif n_unique_values == 2:
        task = TaskType.BIN
    else:
        task = TaskType.REG

    return task


def feature_changing(
    feature_history: Dict[str, str],
    step_name: str,
    features_before: Union[Dict[str, str], Set[str]],
    func: Callable,
    *args,
    **kwargs,
) -> Tuple[Any, Any]:
    """Safe feature filtering.

    Args:
        feature_history: History changes of features processing.
        step_name: Name of step.
        features_before: Features before processing.
        func: Filtering function.
        args: Function positional arguments.
        kwargs: Function named arguments.

    Returns:
        output:
        filter_features:

    """
    # features_before: Set[str]
    if isinstance(features_before, dict):
        features_before = set(features_before.keys())
    else:
        features_before = set(features_before)

    output, filter_features = func(*args, **kwargs)
    if isinstance(filter_features, dict):
        features_after = set(filter_features.keys())
    elif isinstance(filter_features, pd.Series):
        features_after = set(filter_features.index)
    elif isinstance(filter_features, Iterable):
        features_after = set(filter_features)
    else:
        raise RuntimeError("Can't extract features after function call.")

    features_diff = features_before - features_after
    for feature in features_diff:
        feature_history[feature] = step_name

    return output, filter_features
