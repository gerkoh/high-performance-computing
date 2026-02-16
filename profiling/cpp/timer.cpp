#include <chrono>
#include <iostream>
#include <unistd.h>

int main()
{
    const std::chrono::time_point<std::chrono::steady_clock> start = std::chrono::steady_clock::now();

    // simulate program running
    usleep(70000);

    const std::chrono::time_point<std::chrono::steady_clock> end = std::chrono::steady_clock::now();
    const std::chrono::steady_clock::duration elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);

    std::cout << "Elapsed time (ns): " << elapsed_ns.count() << std::endl;
}
