import numpy as np

sigma_0 = np.array(
    [
        [1, 0],
        [0, 1]
    ],
    dtype="complex"
)

sigma_1 = np.array(
    [
        [0, 1],
        [1, 0]
    ],
    dtype="complex"
)

sigma_2 = np.array(
    [
        [0, -1j],
        [1j, 0]
    ], dtype="complex"
)

sigma_3 = np.array(
    [
        [1, 0],
        [0, -1]
    ],
    dtype="complex"
)

density = np.array(
    [
        [1, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 1]
    ]
) * 0.5

# state = np.array(
#     [[1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)]]
# )
# # state = np.array(
# #     [[0, 1, 0, 0]]
# # )
# density = np.dot(state.T, state)
print("=" * 10, "Density Matrix", "=" * 10)
print(density)
print("=" * 10, "Bloch Matrix", "="* 10)
bloch = np.zeros_like(density)

sigmas = [sigma_0, sigma_1, sigma_2, sigma_3]

for i in range(bloch.shape[0]):
    for j in range(bloch.shape[1]):
        D = np.kron(sigmas[i], sigmas[j])
        r = np.trace(np.dot(density, D)).real
        bloch[i, j] = r

print(bloch)
