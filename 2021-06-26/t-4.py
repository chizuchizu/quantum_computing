import cirq
import numpy as np
import sympy as sp

a = cirq.NamedQubit("a")
b = cirq.NamedQubit("b")

val = sp.Symbol("s")

circuit = cirq.Circuit(cirq.X.on(a) ** val, cirq.X.on(b) ** val)

print("Circuit with parameterized gates: \n")
print(circuit)

simulator = cirq.Simulator()
num_params = 5
for y in range(num_params):
    result = simulator.simulate(circuit, param_resolver={"s": y / 4.0})
    print(f"s={y}: {np.around(result.final_state_vector, 2)}")
