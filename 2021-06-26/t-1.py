import cirq

# 量子ビットの定義
a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")
c = cirq.NamedQubit("c")

ops = [
    cirq.H(a),
    cirq.H(b),
    cirq.CNOT(b, c),
    cirq.H(b)
]

circuit = cirq.Circuit(ops)
print("Circuit: \n")
print(circuit)

# Momentごとに表示
print("\nMoments in the circuit:\n")
for i, moment in enumerate(circuit):
    print(f"Moment {i}: \n {moment}")
