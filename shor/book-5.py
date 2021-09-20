import cirq
import math
import fractions
import random

s = 256

L = s.bit_length()
sq_s = int(math.sqrt(s)) + 1
num_workbit = 1
num_mainbit = sq_s.bit_length()
work = cirq.LineQubit.range(num_workbit)
inp = cirq.LineQubit.range(num_workbit, num_workbit + num_mainbit)


def read_eigenphase(result: cirq.Result) -> float:
    exponent_as_integer = result.data['target'][0]
    exponent_num_bits = result.measurements['target'].shape[1]
    return float(exponent_as_integer / 2 ** exponent_num_bits)


class F(cirq.ArithmeticOperation):
    def __init__(self, target_register, input_register):
        self.input_register = input_register
        self.target_register = target_register

    def registers(self):
        # applyの引数に関する情報
        return self.target_register, self.input_register,

    def with_registers(self, *new_registers):
        return F(*new_registers)

    def apply(self, target_value, input_value):
        # ここはinpで表現できるbit数に依る
        # 今の実装だとsqrt(s)にしたほうがいいのかもしれない
        if target_value > s:
            return target_value

        # target_valueは本来0
        # target_valueに下の演算の結果を上書きするイメージ
        return (target_value + x ** input_value) % s


circuit = cirq.Circuit(
    cirq.ops.H.on_each(inp),  # 初期化
    F(work, inp),  # オラクル
    cirq.measure(*work, key="work"),  # ここの測定必要か？
    cirq.qft(*inp, inverse=True),  # 逆フーリエ変換
    cirq.measure(*inp, key="target")
)
print(circuit)
# simulator = cirq.Simulator()
flag = True
ans = 0
iter = 0

# 見つかるまでwhile
while flag:
    x = random.randint(2, s - 1)
    print(x)
    """もし適当に選んだxが素因数だったら終了"""
    c = math.gcd(x, s)
    if math.gcd(x, s) != 1:
        ans = c
        flag = False
    """"""
    iter += 1
    """量子計算"""
    result = cirq.sample(circuit)
    """"""
    """分数に直す"""
    eigenphase = read_eigenphase(result)
    f = fractions.Fraction.from_float(eigenphase).limit_denominator(s)
    r = f.denominator
    """
    分子がゼロ　→　分母は必ず1になって意味がない
    分母が偶数　→　因数分解できない
    """
    if f.numerator != 0 and r % 2 == 0:
        y = x ** (r // 2) % s

        c = math.gcd(y + 1, s)
        if 1 < c < s:
            ans = c
            flag = False

        c = math.gcd(y - 1, s)
        if 1 < c < s:
            ans = c
            flag = False
    """"""
    # print(f)
print(f"{s}の素因数は{ans}")
# print("素因数は", ans)
print("iter: ", iter)
