# Differences

## Queue + Worker Pool Pattern

- Large / unbounded number of requests - only N coroutines exist, memory stays constant
- Work items arrive dynamically

## Semaphore Pattern

- Known, finite set of tasks upfront