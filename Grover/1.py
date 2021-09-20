import cirq
import random
import matplotlib.pyplot as plt
import numpy as np

"""Get qubits to use in the circuit for Grover's algorithm."""
# Number of qubits n.
nqubits = 3
num_iter = 2

# Get qubit registers.
qubits = cirq.LineQubit.range(nqubits)
ancilla = cirq.NamedQubit("Ancilla")


def make_oracle(qubits, ancilla, xprime):
    """Implements the function {f(x) = 1 if x == x', f(x) = 0 if x != x'}."""
    # For x' = (1, 1), the oracle is just a Toffoli gate.
    # For a general x', we negate the zero bits and implement a Toffoli.

    # Negate zero bits, if necessary.
    # yield (cirq.X(q) for (q, bit) in zip(qubits, xprime) if not bit)
    #
    # # Do the Toffoli.
    # yield (cirq.TOFFOLI(qubits[0], qubits[1], ancilla))
    #
    # # Negate zero bits, if necessary.
    # yield (cirq.X(q) for (q, bit) in zip(qubits, xprime) if not bit)
    yield cirq.CCZ(qubits[1], qubits[2], qubits[0])
    #


circuit = cirq.Circuit()


def grover_iteration(qubits, ancilla, oracle):
    """Performs one round of the Grover iteration."""
    # Create an equal superposition over input qubits.
    circuit.append(cirq.H.on_each(*qubits))

    # Put the output qubit in the |-⟩ state.
    circuit.append([cirq.X(ancilla), cirq.H(ancilla)])

    # Query the oracle.
    circuit.append(oracle)

    # Construct Grover operator.
    circuit.append(cirq.H.on_each(*qubits))
    circuit.append(cirq.X.on_each(*qubits))
    circuit.append(cirq.CZ(qubits[0], qubits[1]))
    # circuit.append(cirq.H.on(qubits[1]))
    # circuit.append(cirq.CNOT(qubits[0], qubits[1]))
    # circuit.append(cirq.H.on(qubits[1]))
    circuit.append(cirq.X.on_each(*qubits))
    circuit.append(cirq.H.on_each(*qubits))

    # Measure the input register.
    return circuit


"""Select a 'marked' bitstring x' at random."""
xprime = [random.randint(0, 1) for _ in range(nqubits)]
print(f"Marked bitstring: {xprime}")

"""Create the circuit for Grover's algorithm."""
# Make oracle (black box)
circuit.append(cirq.H.on_each(*qubits))
oracle = make_oracle(qubits, ancilla, xprime)
circuit.append(oracle)

# Embed the oracle into a quantum circuit implementing Grover's algorithm.

# circuit = grover_iteration(qubits, ancilla, oracle)
for _ in range(num_iter):
    circuit = grover_iteration(qubits, ancilla, oracle)

circuit.append(cirq.measure(*qubits, key="result"))

print("Circuit for Grover's algorithm:")
print(circuit)

"""Simulate the circuit for Grover's algorithm and check the output."""


# Helper function.
def bitstring(bits):
    return "".join(str(int(b)) for b in bits)


# Sample from the circuit a couple times.
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=100)

# Look at the sampled bitstrings.
frequencies = result.histogram(key="result", fold_func=bitstring)
print('Sampled results:\n{}'.format(frequencies))

# Check if we actually found the secret value.
most_common_bitstring = frequencies.most_common(1)[0][0]
print("\nMost common bitstring: {}".format(most_common_bitstring))
print("Found a match? {}".format(most_common_bitstring == bitstring(xprime)))
