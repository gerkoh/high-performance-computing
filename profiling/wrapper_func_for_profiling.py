import timeit
from functools import wraps
import numpy as np

def timer(num_iterations: int = 1, print_precision: int = 10):
    """
    Decorator to calculate the wall clock time of a function.
        :param num_iterations: Number of iterations to execute the function.
        :param print_precision: Decimal places to display in the timing output of the wall clock time.
        :return: Wrapped function with timing functionality.
    """
    def decorator(func):
        @wraps(func)  # retain original function metadata
        def wrapper(*args, **kwargs):
            time_lst = np.empty(num_iterations)  # creates an empty numpy array of the number of iterations
            
            for i in range(num_iterations):
                time_start = timeit.default_timer()
                result = func(*args, **kwargs)
                time_end = timeit.default_timer()
                time_lst[i] = time_end - time_start
                print(f"Iteration {i + 1} of {func.__name__}: {time_lst[i]:.{print_precision}f} seconds")

            print("Average wall clock time: " + f"{np.mean(time_lst):.{print_precision}f}")

            return result

        return wrapper

    return decorator


# Example usage 1
@timer(num_iterations=10)
def create_list(size: int):
    lst = []
    for i in range(size):
        lst.append(i)

create_list(1000)


# # Example usage 2
# def create_list(size: int):
#     lst = []
#     for i in range(size):
#         lst.append(i)
# timer(num_iterations=10)(create_list)(1000)