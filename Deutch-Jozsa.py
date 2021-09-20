import cirq
import numpy as np
import matplotlib.pyplot as plt

qubit = cirq.GridQubit(0, 0)
n_qubits = 2
circuit = cirq.Circuit()
qubits = [
    cirq.GridQubit(i, 0)
    for i in range(n_qubits)
]
# 補助bit
ancilla = cirq.GridQubit(n_qubits, 0)


def scheme1(circuit, qubits, ancilla):
    circuit.append([
        cirq.X(ancilla)
    ])
    return circuit


def scheme2(circuit, qubits, ancilla):
    circuit.append([
        cirq.H.on_each(qubits),
        cirq.H(ancilla)
    ])
    return circuit


def scheme4(circuit, qubits, ancilla):
    circuit.append([
        cirq.H.on_each(qubits),
    ])
    return circuit


def scheme5(circuit, qubits, ancilla):
    circuit.append([
        cirq.measure(*qubits, key="m")
    ])
    print("Circuit:")
    print(circuit)

    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=50000)
    print("Results:")
    print(result.histogram(key="m"))

    # list = get_result_list(result)
    #
    # plt.figure(figsize=(4,3))
    # plt.bar(list[:,0],list[:,1])
    return circuit


def seiri(i, n):
    X = str(bin(i)[2:])
    X = X.zfill(n)
    index = []
    for i in range(n):
        if X[i] == "0":
            index.append(i)
    return index


def scheme3(circuit, qubits, ancilla):
    circuit.append(
        [
            # cirq.TOFFOLI(qubits[0], qubits[1], ancilla),
            cirq.CNOT(qubits[0], ancilla),
            cirq.CNOT(qubits[1], ancilla)
        ]
    )
    # for i in range(len(bits)):
    #
    #     p = seiri(i, n_qubits)
    #     if bits[i] == "1":
    #         for j in p:
    #             circuit.append([
    #                 cirq.X(qubits[j])
    #             ])
    #         circuit.append([
    #             cirq.TOFFOLI(qubits[0], qubits[1], ancilla)
    #         ])
    #         for j in p[::-1]:
    #             circuit.append([
    #                 cirq.X(qubits[j])
    #             ])
    return circuit


bits = "0000"

circuit = scheme1(circuit, qubits, ancilla)
circuit = scheme2(circuit, qubits, ancilla)
circuit = scheme3(circuit, qubits, ancilla)
circuit = scheme4(circuit, qubits, ancilla)
circuit = scheme5(circuit, qubits, ancilla)
