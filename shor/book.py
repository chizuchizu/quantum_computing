import cirq
import matplotlib.pyplot as plt

n = 2 ** 5
s = 4
a = 5
L = n.bit_length()
inp = cirq.LineQubit.range(L)
work = cirq.LineQubit.range(L, 2 * L)


class F(cirq.ArithmeticOperation):
    """Quantum addition."""
    def __init__(self, target_register, input_register):
        self.input_register = input_register
        self.target_register = target_register

    def registers(self):
        return self.target_register, self.input_register

    def with_registers(self, *new_registers):
        return F(*new_registers)

    def apply(self, target_value, input_value):
        return (target_value * x ** input_value) % s


circuit = cirq.Circuit(
    cirq.ops.H.on_each(inp),
    F(work, inp),
    cirq.measure(*work, key="work"),
    cirq.qft(*inp),
    cirq.measure(*inp, key="target")
)
print(circuit)
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1000)
# result = cirq.sample(circuit, repetitions=1000)
# print(result)
# print(result.data['target'])
df = result.data["target"]
print(df.value_counts())
result.data["target"].hist()
plt.show()
# eigenphase = read_eigenphase(result)
