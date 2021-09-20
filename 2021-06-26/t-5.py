import cirq
import numpy as np
import sympy as sp

a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")

val = sp.Symbol("s")

"""Create a circuit with a depolarizing channel."""
circuit = cirq.Circuit(cirq.depolarize(0.2)(a), cirq.measure(a))
print(circuit)

"""Example of simulating a noisy circuit with the density matrix simulator."""
# Circuit to simulate.
circuit = cirq.Circuit(cirq.depolarize(0.2)(a))
print('Circuit:\n{}\n'.format(circuit))

# Get the density matrix simulator.
simulator = cirq.DensityMatrixSimulator()

# Simulate the circuit and get the final density matrix.
matrix = simulator.simulate(circuit).final_density_matrix
print('Final density matrix:\n{}'.format(matrix))
