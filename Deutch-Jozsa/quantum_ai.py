import cirq

q0, q1, q2 = cirq.LineQubit.range(3)

constant = (
    [],
    [cirq.X(q2)]
)

balanced = (
    [cirq.CNOT(q0, q2)],
    [cirq.CNOT(q1, q2)],
    [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2)],
    [cirq.CNOT(q0, q2), cirq.X(q2)],
    [cirq.CNOT(q1, q2), cirq.X(q2)],
    [cirq.CNOT(q0, q2), cirq.CNOT(q1, q2), cirq.X(q2)]
)
"""Creating the circuit used in Deutsch's algorithm."""


def deutsch_algorithm(oracle):
    """Returns the circuit for Deutsch's algorithm given an input
    oracle, i.e., a sequence of operations to query a particular function.
    """
    yield cirq.X(q2)
    yield cirq.H(q0), cirq.H(q1), cirq.H(q2)
    yield oracle
    yield cirq.H(q0), cirq.H(q1)
    """-----"""
    yield cirq.H(q2)  # Hで戻して1にする
    # q0, q1が両方共0だったらq2を反転, 1が存在すればそのまま
    yield cirq.X(q0), cirq.X(q1), cirq.CCX(q0, q1, q2)
    """---"""
    yield cirq.measure(q2)


simulator = cirq.Simulator()

print("\nYour result on constant functions:")
for oracle in constant:
    result = simulator.run(cirq.Circuit(deutsch_algorithm(oracle)), repetitions=10)
    print(result)

print("\nYour result on balanced functions:")
for oracle in balanced:
    result = simulator.run(cirq.Circuit(deutsch_algorithm(oracle)), repetitions=10)
    print(result)
print(cirq.Circuit(deutsch_algorithm(oracle)))