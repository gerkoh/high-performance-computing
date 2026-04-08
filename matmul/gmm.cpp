#include <cstddef>
#include <array>
#include <concepts>
#include <iostream>

template <typename T, std::size_t M_rows, std::size_t M_cols, std::size_t N_rows, std::size_t N_cols>
    requires(M_cols == N_rows && (std::integral<T> || std::floating_point<T>))
std::array<std::array<T, N_cols>, M_rows> gmm_loop_optimized(
    const std::array<std::array<T, M_cols>, M_rows> &M,
    const std::array<std::array<T, N_cols>, N_rows> &N)
{
    std::array<std::array<T, N_cols>, M_rows> result{};

    for (std::size_t i = 0; i < M_rows; ++i)
    {
        std::array<T, N_cols> &result_row = result[i];
        for (std::size_t k = 0; k < M_cols; ++k)
        {
            const T m_ik = M[i][k];
            const std::array<T, N_cols> &n_row = N[k];
            for (std::size_t j = 0; j < N_cols; ++j)
            {
                result_row[j] += m_ik * n_row[j];
            }
        }
    }

    return result;
}

int main()
{
    // Example arrays
    std::array<std::array<double, 3>, 2> M{{{1, 2, 3}, {4, 5, 6}}};      // 2x3
    std::array<std::array<double, 2>, 3> N{{{1, 4}, {2, 5}, 3, 6}}; // 3x2

    const auto result = gmm_loop_optimized<double, 2, 3, 3, 2>(M, N);

    std::cout << "Result shape: " << result.size() << "x" << result.front().size() << "\n";
    for (const auto &row : result)
    {
        for (const auto value : row)
        {
            std::cout << value << ' ';
        }
        std::cout << '\n';
    }

    return 0;
}