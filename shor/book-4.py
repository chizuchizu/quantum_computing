import cirq
import math
import fractions

import matplotlib.pyplot as plt
from math import gcd

# n = 2 ** 5
s = 3127
x = int(math.sqrt(s)) - 2
# x = 1000
print(x)
# a = 8
L = s.bit_length()
num_workbit = 5
work = cirq.LineQubit.range(num_workbit)
inp = cirq.LineQubit.range(num_workbit, L + num_workbit)


def read_eigenphase(result: cirq.Result) -> float:
    exponent_as_integer = result.data['target'][0]
    exponent_num_bits = result.measurements['target'].shape[1]
    return float(exponent_as_integer / 2 ** exponent_num_bits)


class F(cirq.ArithmeticOperation):
    def __init__(self, target_register, input_register):
        self.input_register = input_register
        self.target_register = target_register

    def registers(self):
        return self.target_register, self.input_register,

    def with_registers(self, *new_registers):
        return F(*new_registers)

    def apply(self, target_value, input_value):
        if target_value >= s:
            return target_value
        # return input_value % s + target_value + a
        return (target_value + x ** input_value) % s


circuit = cirq.Circuit(
    # cirq.X(work[-1]),  # 1
    cirq.ops.H.on_each(inp),  # 初期化
    F(work, inp),
    cirq.measure(*work, key="work"),
    cirq.qft(*inp, inverse=True),
    cirq.measure(*inp, key="target")
)
print(circuit)
simulator = cirq.Simulator()
flag = True
ans = 0
iter = 0
while flag:
    iter += 1
    result = simulator.run(circuit, repetitions=1)
    eigenphase = read_eigenphase(result)
    f = fractions.Fraction.from_float(eigenphase).limit_denominator(s)
    r = f.denominator
    if f.numerator != 0 and r % 2 == 0:
        y = x ** (r // 2) % s  # sいるか？
        c = math.gcd(y - 1, s)
        if 1 < c < s:
            ans = c
            flag = False

        c = math.gcd(y + 1, s)
        if 1 < c < s:
            ans = c
            flag = False

    print(f)
print(f"{s}の素因数は{ans}")
# print("素因数は", ans)
print("iter: ", iter)
