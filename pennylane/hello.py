import pennylane as qml

shots_list = [5, 10, 1000]
"""
wires:
shots: 回路の試行回数
"""
dev = qml.device("default.qubit", wires=2, shots=shots_list)


@qml.qnode(dev)
def circuit(x):
    qml.RX(x, wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0) @ qml.PauliX(1)), qml.expval(qml.PauliZ(0))


print(circuit(1))
