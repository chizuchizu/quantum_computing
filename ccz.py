import cirq

# Number of qubits n.
nqubits = 3

repetitions = 1000
qubits = cirq.LineQubit.range(nqubits)


def make_oracle(input_qubits):
    yield cirq.H.on_each(*input_qubits)
    yield cirq.X(input_qubits[0])
    yield cirq.X(input_qubits[1])
    yield cirq.X(input_qubits[2])
    yield cirq.Z.controlled(len(input_qubits) - 1)(*input_qubits)
    yield cirq.X(input_qubits[0])
    yield cirq.X(input_qubits[1])
    yield cirq.X(input_qubits[2])

    yield cirq.H.on_each(*input_qubits)

    yield cirq.measure(*input_qubits, key='result')

def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)

circuit = cirq.Circuit()
circuit.append(make_oracle(qubits))

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=repetitions)
frequencies = result.histogram(key='result', fold_func=bitstring)
print(circuit)
print(f'Sampled results:\n{frequencies}')
