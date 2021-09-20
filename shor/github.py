import argparse
import fractions
import math
import random

from typing import Callable, List, Optional, Sequence, Union

import sympy

import cirq


def naive_order_finder(x: int, n: int) -> Optional[int]:
    """Computes smallest positive r such that x**r mod n == 1.
    Args:
        x: integer whose order is to be computed, must be greater than one
           and belong to the multiplicative group of integers modulo n (which
           consists of positive integers relatively prime to n),
        n: modulus of the multiplicative group.
    Returns:
        Smallest positive integer r such that x**r == 1 mod n.
        Always succeeds (and hence never returns None).
    Raises:
        ValueError when x is 1 or not an element of the multiplicative
        group of integers modulo n.
    """
    if x < 2 or n <= x or math.gcd(x, n) > 1:
        raise ValueError(f'Invalid x={x} for modulus n={n}.')
    r, y = 1, x
    while y != 1:
        y = (x * y) % n
        r += 1
    return r


class ModularExp(cirq.ArithmeticOperation):
    """Quantum modular exponentiation.
    This class represents the unitary which multiplies base raised to exponent
    into the target modulo the given modulus. More precisely, it represents the
    unitary V which computes modular exponentiation x**e mod n:
        V|y⟩|e⟩ = |y * x**e mod n⟩ |e⟩     0 <= y < n
        V|y⟩|e⟩ = |y⟩ |e⟩                  n <= y
    where y is the target register, e is the exponent register, x is the base
    and n is the modulus. Consequently,
        V|y⟩|e⟩ = (U**e|r⟩)|e⟩
    where U is the unitary defined as
        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y
    in the header of this file.
    Quantum order finding algorithm (which is the quantum part of the Shor's
    algorithm) uses quantum modular exponentiation together with the Quantum
    Phase Estimation to compute the order of x modulo n.
    """

    def __init__(
            self,
            target: Sequence[cirq.Qid],
            exponent: Union[int, Sequence[cirq.Qid]],
            base: int,
            modulus: int,
    ) -> None:
        if len(target) < modulus.bit_length():
            raise ValueError(
                f'Register with {len(target)} qubits is too small for modulus {modulus}'
            )
        self.target = target
        self.exponent = exponent
        self.base = base
        self.modulus = modulus

    def registers(self) -> Sequence[Union[int, Sequence[cirq.Qid]]]:
        return self.target, self.exponent, self.base, self.modulus

    def with_registers(
            self,
            *new_registers: Union[int, Sequence['cirq.Qid']],
    ) -> 'ModularExp':
        if len(new_registers) != 4:
            raise ValueError(
                f'Expected 4 registers (target, exponent, base, '
                f'modulus), but got {len(new_registers)}'
            )
        target, exponent, base, modulus = new_registers
        if not isinstance(target, Sequence):
            raise ValueError(f'Target must be a qubit register, got {type(target)}')
        if not isinstance(base, int):
            raise ValueError(f'Base must be a classical constant, got {type(base)}')
        if not isinstance(modulus, int):
            raise ValueError(f'Modulus must be a classical constant, got {type(modulus)}')
        return ModularExp(target, exponent, base, modulus)

    def apply(self, *register_values: int) -> int:
        assert len(register_values) == 4
        target, exponent, base, modulus = register_values
        if target >= modulus:
            return target
        return (target * base ** exponent) % modulus

    def _circuit_diagram_info_(
            self,
            args: cirq.CircuitDiagramInfoArgs,
    ) -> cirq.CircuitDiagramInfo:
        # 回路の描画を設定するやつ　あってもなくてもいい
        # https://github.com/quantumlib/Cirq/blob/4d956c57c309437a1e501cb170e8a57176e9f3de/cirq-core/cirq/protocols/circuit_diagram_info_protocol.py#L41
        assert args.known_qubits is not None
        wire_symbols: List[str] = []
        t, e = 0, 0
        for qubit in args.known_qubits:
            if qubit in self.target:
                if t == 0:
                    if isinstance(self.exponent, Sequence):
                        e_str = 'e'
                    else:
                        e_str = str(self.exponent)
                    wire_symbols.append(f'ModularExp(t*{self.base}**{e_str} % {self.modulus})')
                else:
                    wire_symbols.append('t' + str(t))
                t += 1
            if isinstance(self.exponent, Sequence) and qubit in self.exponent:
                wire_symbols.append('e' + str(e))
                e += 1
        return cirq.CircuitDiagramInfo(wire_symbols=tuple(wire_symbols))


def make_order_finding_circuit(x: int, n: int) -> cirq.Circuit:
    """Returns quantum circuit which computes the order of x modulo n.
    The circuit uses Quantum Phase Estimation to compute an eigenvalue of
    the unitary
        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y
    discussed in the header of this file. The circuit uses two registers:
    the target register which is acted on by U and the exponent register
    from which an eigenvalue is read out after measurement at the end. The
    circuit consists of three steps:
    1. Initialization of the target register to |0..01⟩ and the exponent
       register to a superposition state.
    2. Multiple controlled-U**2**j operations implemented efficiently using
       modular exponentiation.
    3. Inverse Quantum Fourier Transform to kick an eigenvalue to the
       exponent register.
    Args:
        x: positive integer whose order modulo n is to be found
        n: modulus relative to which the order of x is to be found
    Returns:
        Quantum circuit for finding the order of x modulo n
    """
    L = n.bit_length()
    target = cirq.LineQubit.range(L)
    exponent = cirq.LineQubit.range(L, 2 * L + 3)
    return cirq.Circuit(
        cirq.X(target[L - 1]),
        cirq.H.on_each(*exponent),
        ModularExp(target, exponent, x, n),
        cirq.qft(*exponent, inverse=True),
        cirq.measure(*exponent, key='exponent'),
    )


def read_eigenphase(result: cirq.Result) -> float:
    """Interprets the output of the order finding circuit.
    Specifically, it returns s/r such that exp(2πis/r) is an eigenvalue
    of the unitary
        U|y⟩ = |xy mod n⟩  0 <= y < n
        U|y⟩ = |y⟩         n <= y
    described in the header of this file.
    Args:
        result: trial result obtained by sampling the output of the
            circuit built by make_order_finding_circuit
    Returns:
        s/r where r is the order of x modulo n and s is in [0..r-1].
    """
    exponent_as_integer = result.data['exponent'][0]
    exponent_num_bits = result.measurements['exponent'].shape[1]
    return float(exponent_as_integer / 2 ** exponent_num_bits)


def quantum_order_finder(x: int, n: int) -> Optional[int]:
    """Computes smallest positive r such that x**r mod n == 1.
    Args:
        x: integer whose order is to be computed, must be greater than one
           and belong to the multiplicative group of integers modulo n (which
           consists of positive integers relatively prime to n),
        n: modulus of the multiplicative group.
    Returns:
        Smallest positive integer r such that x**r == 1 mod n or None if the
        algorithm failed. The algorithm fails when the result of the Quantum
        Phase Estimation is inaccurate, zero or a reducible fraction.
    Raises:
        ValueError when x is 1 or not an element of the multiplicative
        group of integers modulo n.
    """
    if x < 2 or n <= x or math.gcd(x, n) > 1:
        raise ValueError(f'Invalid x={x} for modulus n={n}.')

    circuit = make_order_finding_circuit(x, n)
    print(circuit)
    result = cirq.sample(circuit)
    eigenphase = read_eigenphase(result)
    # 分数に直す
    # 結局大事なのは分母の情報
    f = fractions.Fraction.from_float(eigenphase).limit_denominator(n)
    if f.numerator == 0:
        return None  # coverage: ignore
    r = f.denominator
    if x ** r % n != 1:
        return None  # coverage: ignore
    return r


def find_factor_of_prime_power(n: int) -> Optional[int]:
    """Returns non-trivial factor of n if n is a prime power, else None."""
    for k in range(2, math.floor(math.log2(n)) + 1):
        c = math.pow(n, 1 / k)
        c1 = math.floor(c)
        if c1 ** k == n:
            return c1
        c2 = math.ceil(c)
        if c2 ** k == n:
            return c2
    return None


def find_factor(
        n: int, order_finder: Callable[[int, int], Optional[int]], max_attempts: int = 30
) -> Optional[int]:
    """Returns a non-trivial factor of composite integer n.
    Args:
        n: integer to factorize,
        order_finder: function for finding the order of elements of the
            multiplicative group of integers modulo n,
        max_attempts: number of random x's to try, also an upper limit
            on the number of order_finder invocations.
    Returns:
        Non-trivial factor of n or None if no such factor was found.
        Factor k of n is trivial if it is 1 or n.
    """
    # 素数排除
    if sympy.isprime(n):
        return None
    # # 偶数排除
    # if n % 2 == 0:
    #     return 2

    # 素数べきを排除
    # c = find_factor_of_prime_power(n)
    c = None

    if c is not None:
        return c
    for _ in range(max_attempts):
        x = random.randint(2, n - 1)
        c = math.gcd(x, n)
        # 適当なxを選び、nとの最大公約数をとる
        # 最大公約数が1なら続行、それ以外なら因数が見つかったということなので終わり
        if 1 < c < n:
            continue
#             return c  # coverage: ignore

        # nを法とするxの次数rを計算
        r = order_finder(x, n)
        # 見つからなければcontinue
        if r is None:
            continue  # coverage: ignore

        # rが奇数でもだめ
        if r % 2 != 0:
            continue  # coverage: ignore

        # 因数分解する
        y = x ** (r // 2) % n
        assert 1 < y < n
        c = math.gcd(y - 1, n)
        # 1だったりnだったりすることがあるが、特に意味はないので条件分岐
        if 1 < c < n:
            return c
    return None  # coverage: ignore


def main(
        n: int,
        order_finder: Callable[[int, int], Optional[int]] = naive_order_finder,
):
    if n < 2:
        raise ValueError(f'Invalid input {n}, expected positive integer greater than one.')

    d = find_factor(n, order_finder)

    if d is None:
        print(f'No non-trivial factor of {n} found. It is probably a prime.')
    else:
        print(f'{d} is a non-trivial factor of {n}')

        assert 1 < d < n
        assert n % d == 0


if __name__ == '__main__':
    # coverage: ignore
    ORDER_FINDERS = {
        'naive': naive_order_finder,
        'quantum': quantum_order_finder,
    }
    n = 77
    order_finder = "quantum"
    main(n=n, order_finder=ORDER_FINDERS[order_finder])
