import timeit
from functools import wraps
from typing import Callable, Optional


def timer(
    func: Optional[Callable] = None,
    *,
    num_iterations: int = 1,
    print_precision: int = 10,
    quiet: bool = False,
):
    """
    Decorator to calculate the wall clock time of a function.

    Can be used as @timer or @timer() or @timer(num_iterations=5, print_precision=3)

    Args:
        func: The function to be decorated (when used without parentheses)
        num_iterations: Number of iterations to execute the function.
        print_precision: Decimal places to display in the timing output of the wall clock time.
        quiet: If True, suppress the print output for each iteration.

    Returns:
        Wrapped function with timing functionality.
    """

    if num_iterations < 1:
        raise ValueError("num_iterations must be a positive integer greater than 0.")

    def decorator(f: Callable):
        @wraps(f)  # retain original function metadata
        def wrapper(*args, **kwargs):
            if num_iterations == 1:
                time_start = timeit.default_timer()
                result = f(*args, **kwargs)
                time_end = timeit.default_timer()
                time_taken = time_end - time_start
                print(
                    f"Iteration 1 of {f.__name__}: {time_taken:.{print_precision}f} seconds"
                )

            else:
                import numpy as np

                time_lst = np.empty(
                    num_iterations
                )  # creates an empty numpy array of the number of iterations

                for i in range(num_iterations):
                    time_start = timeit.default_timer()
                    result = f(*args, **kwargs)
                    time_end = timeit.default_timer()
                    time_lst[i] = time_end - time_start
                    if not quiet:
                        print(
                            f"Iteration {i + 1} of {f.__name__}: {time_lst[i]:.{print_precision}f} seconds"
                        )
                print(
                    "Average wall clock time: "
                    + f"{np.mean(time_lst):.{print_precision}f}"
                )
            return result

        return wrapper

    # If called without parentheses (@timer), func will be the actual function
    if func is not None:
        return decorator(func)

    # If called with parentheses (@timer() or @timer(args)), func will be None
    return decorator
