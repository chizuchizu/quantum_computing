"""Imports for the notebook."""
import fractions
import math
import random

import numpy as np
import sympy
from typing import Callable, List, Optional, Sequence, Union

import cirq

"""Function to compute the elements of Z_n."""


def multiplicative_group(n: int) -> List[int]:
    """Returns the multiplicative group modulo n.

    Args:
        n: Modulus of the multiplicative group.
    """
    assert n > 1
    group = [1]
    for x in range(2, n):
        if math.gcd(x, n) == 1:
            group.append(x)
    return group


"""Example of a multiplicative group."""
n = 15
print(f"The multiplicative group modulo n = {n} is:")
print(multiplicative_group(n))

"""Function for classically computing the order of an element of Z_n."""


def classical_order_finder(x: int, n: int) -> Optional[int]:
    """Computes smallest positive r such that x**r mod n == 1.

    Args:
        x: Integer whose order is to be computed, must be greater than one
           and belong to the multiplicative group of integers modulo n (which
           consists of positive integers relatively prime to n),
        n: Modulus of the multiplicative group.

    Returns:
        Smallest positive integer r such that x**r == 1 mod n.
        Always succeeds (and hence never returns None).

    Raises:
        ValueError when x is 1 or not an element of the multiplicative
        group of integers modulo n.
    """
    # Make sure x is both valid and in Z_n.
    if x < 2 or x >= n or math.gcd(x, n) > 1:
        raise ValueError(f"Invalid x={x} for modulus n={n}.")

    # Determine the order.
    r, y = 1, x
    while y != 1:
        y = (x * y) % n
        r += 1
    return r


"""Example of (classically) computing the order of an element."""
n = 15  # The multiplicative group is [1, 2, 4, 7, 8, 11, 13, 14].
x = 8
r = classical_order_finder(x, n)

# Check that the order is indeed correct.
print(f"x^r mod n = {x}^{r} mod {n} = {x ** r % n}")
"""Example of defining an arithmetic (quantum) operation in Cirq."""


class Adder(cirq.ArithmeticOperation):
    """Quantum addition."""

    def __init__(self, target_register, input_register):
        self.input_register = input_register
        self.target_register = target_register
        print(self.input_register)
        print(self.target_register)
        print("ased")

    def registers(self):
        return self.target_register, self.input_register

    def with_registers(self, *new_registers):
        return Adder(*new_registers)

    def apply(self, target_value, input_value):
        # print(target_value, input_value, target_value + input_value)
        return target_value + input_value


"""Example of using an Adder in a circuit."""
# Two qubit registers.
qreg1 = cirq.LineQubit.range(2)
qreg2 = cirq.LineQubit.range(2, 4)

# Define the circuit.
circ = cirq.Circuit(
    cirq.ops.X.on(qreg1[1]),
    cirq.ops.X.on(qreg2[0]),
    Adder(input_register=qreg1, target_register=qreg2),
    cirq.measure_each(*qreg1),
    cirq.measure_each(*qreg2)
)

# Display it.
print("Circuit:\n")
print(circ)

# Print the measurement outcomes.
print("\n\nMeasurement outcomes:\n")
print(cirq.sample(circ, repetitions=5).data)

"""Example of the unitary of an Adder operation."""
print(
    cirq.unitary(
        Adder(target_register=cirq.LineQubit.range(2),
              input_register=1)
    ).real
)
"""Defines the modular exponential operation used in Shor's algorithm."""


class ModularExp(cirq.ArithmeticOperation):
    """Quantum modular exponentiation.

    This class represents the unitary which multiplies base raised to exponent
    into the target modulo the given modulus. More precisely, it represents the
    unitary V which computes modular exponentiation x**e mod n:

        V|y⟩|e⟩ = |y * x**e mod n⟩ |e⟩     0 <= y < n
        V|y⟩|e⟩ = |y⟩ |e⟩                  n <= y

    where y is the target register, e is the exponent register, x is the base
    and n is the modulus. Consequently,

        V|y⟩|e⟩ = (U**e|y)|e⟩

    where U is the unitary defined as

        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y
    """

    def __init__(
            self,
            target: Sequence[cirq.Qid],
            exponent: Union[int, Sequence[cirq.Qid]],
            base: int,
            modulus: int
    ) -> None:
        if len(target) < modulus.bit_length():
            raise ValueError(f'Register with {len(target)} qubits is too small '
                             f'for modulus {modulus}')
        self.target = target
        self.exponent = exponent
        self.base = base
        self.modulus = modulus

    def registers(self) -> Sequence[Union[int, Sequence[cirq.Qid]]]:
        return self.target, self.exponent, self.base, self.modulus

    def with_registers(
            self,
            *new_registers: Union[int, Sequence['cirq.Qid']],
    ) -> cirq.ArithmeticOperation:
        if len(new_registers) != 4:
            raise ValueError(f'Expected 4 registers (target, exponent, base, '
                             f'modulus), but got {len(new_registers)}')
        target, exponent, base, modulus = new_registers
        if not isinstance(target, Sequence):
            raise ValueError(
                f'Target must be a qubit register, got {type(target)}')
        if not isinstance(base, int):
            raise ValueError(
                f'Base must be a classical constant, got {type(base)}')
        if not isinstance(modulus, int):
            raise ValueError(
                f'Modulus must be a classical constant, got {type(modulus)}')
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
                    wire_symbols.append(
                        f'ModularExp(t*{self.base}**{e_str} % {self.modulus})')
                else:
                    wire_symbols.append('t' + str(t))
                t += 1
            if isinstance(self.exponent, Sequence) and qubit in self.exponent:
                wire_symbols.append('e' + str(e))
                e += 1
        return cirq.CircuitDiagramInfo(wire_symbols=tuple(wire_symbols))

"""Create the target and exponent registers for phase estimation,
and see the number of qubits needed for Shor's algorithm.
"""
n = 15
L = n.bit_length()

# The target register has L qubits.
target = cirq.LineQubit.range(L)

# The exponent register has 2L + 3 qubits.
exponent = cirq.LineQubit.range(L, 3 * L + 3)

# Display the total number of qubits to factor this n.
print(f"To factor n = {n} which has L = {L} bits, we need 3L + 3 = {3 * L + 3} qubits.")

"""Function to make the quantum circuit for order finding."""


def make_order_finding_circuit(x: int, n: int) -> cirq.Circuit:
    """Returns quantum circuit which computes the order of x modulo n.

    The circuit uses Quantum Phase Estimation to compute an eigenvalue of
    the unitary

        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y

    Args:
        x: positive integer whose order modulo n is to be found
        n: modulus relative to which the order of x is to be found

    Returns:
        Quantum circuit for finding the order of x modulo n
    """
    L = n.bit_length()
    target = cirq.LineQubit.range(L)
    exponent = cirq.LineQubit.range(L, 3 * L + 3)
    return cirq.Circuit(
        cirq.X(target[L - 1]),
        cirq.H.on_each(*exponent),
        ModularExp(target, exponent, x, n),
        cirq.qft(*exponent, inverse=True),
        cirq.measure(*exponent, key='exponent'),
    )
"""Example of the quantum circuit for period finding."""
n = 15
x = 7
circuit = make_order_finding_circuit(x, n)
print(circuit)