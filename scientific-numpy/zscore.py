import numpy as np


def z_score(arr: np.typing.NDArray):
    row_mean = np.mean(arr, axis=1, keepdims=True)
    row_std = np.std(arr, axis=1, keepdims=True)
    z = (arr - row_mean) / row_std
    return z

if __name__ == "__main__":
    rng = np.random.default_rng(seed=42)  # allows local random-number state
    arr = rng.integers(0, 10, size=(3, 4))
    print("Original array:\n" + str(arr))
    z = z_score(arr)
    print("After z-score standardisation:\n" + str(z))