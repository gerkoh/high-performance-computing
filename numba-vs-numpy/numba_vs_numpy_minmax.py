"""
Findings: A single-pass Numba implementation does not necessarily outperform NumPy
- With a 10,000,000-element float64 array:
    - Numba single-pass loop: ~0.0131 s
    - NumPy min() + max():   ~0.0033 s
"""

import numpy as np
from numba import njit

from profiling.py.timer_decorator import timer


@timer(
    num_iterations=5,
    print_fn_metadata=True,
    metadata=lambda arr: {"arr_length": arr.size},
)
@njit
def get_min_and_max(arr: np.typing.NDArray):
    _max = arr[0]
    _min = arr[0]
    for i in arr:
        _max = max(_max, i)
        _min = min(_min, i)
    return _min, _max


@timer(
    num_iterations=5,
    print_fn_metadata=True,
    metadata=lambda arr: {"arr_length": arr.size},
)
def get_min_and_max_numpy(arr: np.typing.NDArray):
    _max = arr.max()
    _min = arr.min()
    return _min, _max


def main():
    arr = np.random.random(10_000_000)
    get_min_and_max.__wrapped__(
        arr
    )  # bypass timer decorator, compile to machine code first
    get_min_and_max(arr)
    get_min_and_max_numpy(arr)


if __name__ == "__main__":
    main()
