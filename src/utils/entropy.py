import math
from collections import Counter


def calculate_shannon_entropy(data: str) -> float:
    """
    Calculate the Shannon entropy of a string.

    Args:
        data: Input string

    Returns:
        Entropy value (float). Higher values indicate more randomness.
    """
    if not data:
        return 0.0

    entropy = 0.0
    length = len(data)

    # Calculate frequency of each character
    counts = Counter(data)

    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy
