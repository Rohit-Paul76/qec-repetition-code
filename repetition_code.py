"""Three-qubit repetition code on default.mixed.

Data qubits 0-2 hold a|000> + b|111>, ancillas 3-4 measure the parities Z0Z1 and Z1Z2.
Each circuit returns probs of the logical qubit, so probs[1] is the logical error rate.
"""
import pennylane as qml

DATA = [0, 1, 2]
ANCILLAS = [3, 4]

dev = qml.device("default.mixed", wires=DATA + ANCILLAS)


def encode():
    # CNOTs are self-inverse, so this also decodes
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def measure_syndrome():
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    return qml.measure(3), qml.measure(4)


def correct(s01, s12):
    # (1,0) -> qubit 0, (1,1) -> qubit 1, (0,1) -> qubit 2
    qml.cond(s01 & ~s12, qml.PauliX)(wires=0)
    qml.cond(s01 & s12, qml.PauliX)(wires=1)
    qml.cond(~s01 & s12, qml.PauliX)(wires=2)


@qml.qnode(dev)
def bit_flip_unencoded(p):
    qml.BitFlip(p, wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def bit_flip_encoded(p):
    encode()
    for w in DATA:
        qml.BitFlip(p, wires=w)
    s01, s12 = measure_syndrome()
    correct(s01, s12)
    encode()
    return qml.probs(wires=0)


@qml.qnode(dev)
def phase_flip_unencoded(p):
    qml.Hadamard(wires=0)
    qml.PhaseFlip(p, wires=0)
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def phase_flip_encoded(p):
    # Z errors don't change any parity, so the syndrome is always (0, 0)
    qml.Hadamard(wires=0)
    encode()
    for w in DATA:
        qml.PhaseFlip(p, wires=w)
    s01, s12 = measure_syndrome()
    correct(s01, s12)
    encode()
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


def bit_flip_theory(p):
    # fails when 2 or 3 qubits flip
    return 3 * p**2 * (1 - p) + p**3


def phase_flip_theory(p):
    # fails on an odd number of Z's
    return (1 - (1 - 2 * p) ** 3) / 2
