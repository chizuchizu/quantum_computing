import pennylane as qml
import numpy as np

shots_list = [5, 10, 1000]
"""
wires:
shots: 回路の試行回数
"""
dev = qml.device('default.qubit', wires=['wire1', 'wire2'], shots=1000)


# @qml.qnode(dev)
def my_quantum_function(x, y):
    qml.RZ(x, wires='wire1')
    qml.CNOT(wires=['wire1', 'wire2'])
    qml.RY(y, wires='wire2')
    return qml.expval(qml.PauliZ('wire2'))


circuit = qml.QNode(my_quantum_function, dev)
print(circuit(np.pi / 4, 0.7))
print(circuit.draw())
