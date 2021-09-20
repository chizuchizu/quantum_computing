import cirq

# Number of qubits n.
nqubits = 3
# Grover's operatorを何回作用させるか
num_loop = 2
# 正解のbit
target_bits = [
    1, 0, 0
]
repetitions = 1000
qubits = cirq.LineQubit.range(nqubits)
ancilla = cirq.NamedQubit("Ancilla")


def make_oracle(input_qubits, output_qubit, x_bits):
    return [
        [cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit],
        cirq.X.controlled(len(input_qubits))(*input_qubits, output_qubit),
        [cirq.X(q) for (q, bit) in zip(input_qubits, x_bits) if not bit]
    ]


def make_grover_operator(input_qubits, output_qubit, oracle):
    return [
        oracle,
        cirq.H.on_each(*input_qubits),
        cirq.X.on_each(*input_qubits),
        cirq.Z.controlled(len(input_qubits) - 1)(*input_qubits),
        cirq.X.on_each(*input_qubits),
        cirq.H.on_each(*input_qubits)
    ]


def make_grover_circuit(input_qubits, output_qubit, oracle, grover_operator):
    c = cirq.Circuit()

    # 初期設定
    c.append(
        [
            cirq.X(output_qubit),
            cirq.H(output_qubit),
            cirq.H.on_each(*input_qubits),
        ]
    )

    # Grover's operatorを適当な回数、作用させる
    [c.append(grover_operator) for _ in range(num_loop)]

    # 結果を測定
    c.append(cirq.measure(*input_qubits, key='result'))
    c.append(cirq.measure(output_qubit, key="work_bit"))

    return c


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)


circuit = cirq.Circuit()

oracle = make_oracle(qubits, ancilla, target_bits)
grover_operator = make_grover_operator(qubits, ancilla, oracle)

circuit = make_grover_circuit(qubits, ancilla, oracle, grover_operator)
# 　量子回路
print(circuit)

"""-------------"""
print("-" * 30)
print("parameters")
print(f"Target bits: {bitstring(target_bits)}")
print(f"num_loop: {num_loop}")
print(f"repetitions: {repetitions}")
print("-" * 30)
print()
"""-------------"""

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=repetitions)
frequencies = result.histogram(key='result', fold_func=bitstring)
print(f'Sampled results:\n{frequencies}')
frequencies_ = result.histogram(key='work_bit', fold_func=bitstring)
print(f'Sampled work bit:\n{frequencies_}')

# Check if we actually found the secret value.
most_common_bitstring = frequencies.most_common(1)[0][0]
most_common_bitstring_prob = frequencies.most_common(1)[0][1] / repetitions * 100
print(f'Most common bitstring: {most_common_bitstring} ({most_common_bitstring_prob} %)')

equal_flag = bitstring(target_bits) == most_common_bitstring
print("Found a match:", equal_flag)
