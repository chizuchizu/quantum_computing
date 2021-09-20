import pprint
import cirq
import numpy as np

inp = cirq.LineQubit.range(2)

circuit = cirq.Circuit(
    cirq.H(inp[0]),
    cirq.H(inp[1]),
    # cirq.CCNOT(*inp),
    cirq.measure(*inp, key="target")
)

# Display it.
print("Simulating circuit:")
print(circuit)
# Simulate with the density matrix simulator.
dsim = cirq.DensityMatrixSimulator()
rho = dsim.simulate(circuit).final_density_matrix

# print(rho)
pprint.pprint(rho)