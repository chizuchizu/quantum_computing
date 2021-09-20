import cirq
import numpy as np

a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")


def basic_circuit(measure=True):
    yield cirq.H(a)
    yield cirq.CNOT(a, b)
    if measure:
        yield cirq.measure(a)


circuit = cirq.Circuit(basic_circuit(measure=False))
print(circuit)
"""
波動関数を用いてシミュレート
デバッグがしやすい
"""
simulator = cirq.Simulator()
result = simulator.simulate(circuit)
"""
実際の量子デバイスと同じようなサンプリング
出力はビット文字列
simulator.run(circuit)
"""

print("\n Dirac notation:")
print(result.dirac_notation())

print("State vector:")
print(np.around(result.final_state_vector, 3))

