import cirq
import numpy as np

a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")


def basic_circuit(measure=True):
    yield cirq.H(a)
    yield cirq.CNOT(a, b)
    if measure:
        yield cirq.measure(a)
        yield cirq.measure(b)


circuit = cirq.Circuit(basic_circuit(measure=True))
print(circuit)
"""
波動関数を用いてシミュレート
デバッグがしやすい
"""
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1000)
print(result)
print(result.histogram(key="a"))
print(result.histogram(key="b"))
"""
実際の量子デバイスと同じようなサンプリング
出力はビット文字列
simulator.run(circuit)
"""
