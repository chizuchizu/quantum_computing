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

state = np.array(
    [[1, 0, 0, 0, 0, 1, 1, 1]]
) * 0.5
# # state = np.array(
# #     [[0, 1, 0, 0]]
# # )
density = np.dot(state.T, state)
print("=" * 10, "Density Matrix", "=" * 10)
print(density)
print("=" * 10, "Bloch Matrix", "=" * 10)
bloch = np.zeros(
    (4, 4, 4)
)
#
sigmas = [sigma_0, sigma_1, sigma_2, sigma_3]

for i in range(bloch.shape[0]):
    for j in range(bloch.shape[1]):
        for k in range(bloch.shape[2]):
            D = np.kron(sigmas[i], sigmas[j])
            D = np.kron(D, sigmas[k])
            r = np.trace(np.dot(density, D)).real
            bloch[i, j, k] = r

print(bloch)

q_0 = bloch[0, 0, 1:]
q_1 = bloch[0, 1:, 0]
q_2 = bloch[1:, 0, 0]
print("=" * 10, "qubit 0のブロッホ球", "=" * 10)
print(q_0)
print("=" * 10, "qubit 1のブロッホ球", "=" * 10)
print(q_1)
print("=" * 10, "qubit 2のブロッホ球", "=" * 10)
print(q_2)
