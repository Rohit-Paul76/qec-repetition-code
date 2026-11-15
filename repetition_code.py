import pennylane as qml

data_q = [0, 1, 2]
anc_q = [3, 4]

dev = qml.device("default.mixed", wires=data_q + anc_q)


def encode():
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def measure_syn():
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    return qml.measure(3), qml.measure(4)


def correct(s_01, s_12):
    qml.cond(s_01 & ~s_12, qml.PauliX)(wires=0)
    qml.cond(s_01 & s_12, qml.PauliX)(wires=1)
    qml.cond(~s_01 & s_12, qml.PauliX)(wires=2)


@qml.qnode(dev)
def bitflip_bare(p):
    qml.BitFlip(p, wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def bitflip_code(p):
    encode()
    for q in data_q:
        qml.BitFlip(p, wires=q)
    s_01, s_12 = measure_syn()
    correct(s_01, s_12)
    encode()
    return qml.probs(wires=0)


@qml.qnode(dev)
def phaseflip_bare(p):
    qml.Hadamard(wires=0)
    qml.PhaseFlip(p, wires=0)
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def phaseflip_code(p):
    qml.Hadamard(wires=0)
    encode()
    for q in data_q:
        qml.PhaseFlip(p, wires=q)
    s_01, s_12 = measure_syn()
    correct(s_01, s_12)
    encode()
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


def bitflip_formula(p):
    return 3 * p**2 * (1 - p) + p**3


def phaseflip_formula(p):
    return (1 - (1 - 2 * p) ** 3) / 2
