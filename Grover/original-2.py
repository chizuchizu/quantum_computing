import cirq
import random
import matplotlib.pyplot as plt
import numpy as np

"""Get qubits to use in the circuit for Grover's algorithm."""
# Number of qubits n.
nqubits = 2
num_loop = 1

# Get qubit registers.
qubits = cirq.LineQubit.range(nqubits)
ancilla = cirq.NamedQubit("Ancilla")


def make_oracle(input_qubits, output_qubit, x_bits):
    """Implement function {f(x) = 1 if x==x', f(x) = 0 if x!= x'}."""
    # Make oracle.
    # for (1, 1) it's just a Toffoli gate
    # otherwise negate the zero-bits.
    # yield (cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)
    # yield (cirq.TOFFOLI(input_qubits[0], input_qubits[1], output_qubit))
    # yield (cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit)
    yield cirq.X.controlled(len(input_qubits))(*input_qubits, output_qubit)


def make_grover_circuit(input_qubits, output_qubit, oracle):
    """Find the value recognized by the oracle in sqrt(N) attempts."""
    # For 2 input qubits, that means using Grover operator only once.
    c = cirq.Circuit()

    # Initialize qubits.
    c.append(
        [
            cirq.X(output_qubit),
            cirq.H(output_qubit),
            cirq.H.on_each(*input_qubits),
        ]
    )

    # Query oracle.
    # c.append(oracle)

    # Construct Grover operator.
    for _ in range(num_loop):
        c.append(cirq.Z.controlled(len(input_qubits) - 1)(*input_qubits))
        c.append(cirq.H.on_each(*input_qubits))

        # c.append(cirq.H.on_each(*input_qubits))
        c.append(cirq.X.controlled(len(input_qubits) - 1)(*input_qubits))
        # c.append(cirq.X.controlled(len(input_qubits))(*input_qubits, output_qubit))
        c.append(cirq.Z.controlled(len(input_qubits) - 1)(*input_qubits))
        c.append(cirq.X.on_each(*input_qubits))
        c.append(cirq.H.on_each(*input_qubits))

    # Measure the result.
    c.append(cirq.measure(*input_qubits, key='result'))

    return c


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)


circuit = cirq.Circuit()

oracle = make_oracle(qubits, ancilla, None)

circuit = make_grover_circuit(qubits, ancilla, oracle)
print(circuit)

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=100)
frequencies = result.histogram(key='result', fold_func=bitstring)
print(f'Sampled results:\n{frequencies}')

# Check if we actually found the secret value.
most_common_bitstring = frequencies.most_common(1)[0][0]
print(f'Most common bitstring: {most_common_bitstring}')
