"""Imports for the notebook."""
import fractions
import math
import random

import numpy as np
import sympy
from typing import Callable, List, Optional, Sequence, Union, Collection

import cirq


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
        return target_value + input_value + 1

    def controlled_by(self, *control_qubits, control_values=None):
        # 制御するだけ
        # Operationのほうだとvaluesが先だったけどcontrolled_byの実装のようにqubitsが先にしたい
        return cirq.ops.ControlledOperation(control_qubits, self, control_values)



"""Example of using an Adder in a circuit."""
# Two qubit registers.
qreg1 = cirq.LineQubit.range(2)
qreg2 = cirq.LineQubit.range(2, 4)
qreg3 = cirq.LineQubit.range(4, 5)

# Define the circuit.
circ = cirq.Circuit(
    #  cirq.ops.X.on(qreg1[1]),
    cirq.ops.X.on(qreg3[0]),
    Adder(input_register=qreg1, target_register=qreg2).controlled_by(qreg3[0]),
    cirq.measure_each(*qreg1),
    cirq.measure_each(*qreg2)
)

# Display it.
print("Circuit:\n")
print(circ)

# Print the measurement outcomes.
print("\n\nMeasurement outcomes:\n")
print(cirq.sample(circ, repetitions=5).data)
