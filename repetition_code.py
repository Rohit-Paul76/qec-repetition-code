"""Three-qubit repetition code in PennyLane.

One logical qubit is stored in three data qubits (wires 0, 1, 2) as a|000> + b|111>.
Two extra qubits (wires 3, 4), the ancillas, record parities of the data qubits
without reading the stored state. Those two parity bits are the syndrome; a lookup
table turns the syndrome into a correction.

Every circuit returns the probability that the logical qubit comes out wrong
(the logical error rate), so it can be compared with the physical error rate p.
"""
import pennylane as qml

DATA = [0, 1, 2]
ANCILLAS = [3, 4]

# default.mixed tracks the density matrix, so noise channels give exact
# probabilities instead of sampled estimates.
dev = qml.device("default.mixed", wires=DATA + ANCILLAS)


def encode():
    """Copy the basis value of wire 0 onto wires 1 and 2: a|0> + b|1> -> a|000> + b|111>.

    Applying it a second time undoes it (CNOT is its own inverse), so the same
    function also decodes.
    """
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def measure_syndrome():
    """Measure the parities Z0 Z1 and Z1 Z2 onto the two ancillas.

    Each ancilla flips once for every data qubit in its pair that is |1>, so it ends
    up as 1 exactly when the two qubits disagree. In a|000> + b|111> every pair
    agrees in both branches, so the ancillas learn nothing about a and b.
    """
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    return qml.measure(3), qml.measure(4)


def correct(s01, s12):
    """Lookup-table decoder: flip the one data qubit the syndrome points to.

    syndrome (s01, s12) | most likely single flip
    (0, 0)              | none
    (1, 0)              | qubit 0  (only the 0-1 pair disagrees)
    (1, 1)              | qubit 1  (it sits in both pairs)
    (0, 1)              | qubit 2  (only the 1-2 pair disagrees)
    """
    qml.cond(s01 & ~s12, qml.PauliX)(wires=0)
    qml.cond(s01 & s12, qml.PauliX)(wires=1)
    qml.cond(~s01 & s12, qml.PauliX)(wires=2)


# ---- Bit-flip noise: the error this code is built for --------------------------

@qml.qnode(dev)
def bit_flip_unencoded(p):
    """One bare qubit in |0>, flipped with probability p. Returns P(reads 1) = p."""
    qml.BitFlip(p, wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def bit_flip_encoded(p):
    """|0> encoded as |000>, each data qubit flipped independently with probability p,
    then syndrome, correction and decoding. Returns P(logical qubit reads 1)."""
    encode()
    for w in DATA:
        qml.BitFlip(p, wires=w)
    s01, s12 = measure_syndrome()
    correct(s01, s12)
    encode()  # decode
    return qml.probs(wires=0)


# ---- Phase-flip noise: the error this code cannot see ---------------------------

@qml.qnode(dev)
def phase_flip_unencoded(p):
    """|+> with a Z applied with probability p. Measured in the X basis (H, then Z),
    so P(reads 1) is the probability that |+> became |->."""
    qml.Hadamard(wires=0)
    qml.PhaseFlip(p, wires=0)
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


@qml.qnode(dev)
def phase_flip_encoded(p):
    """|+> encoded as (|000> + |111>)/sqrt(2), each data qubit hit by Z with probability p.

    A Z changes no parity, so the syndrome stays (0, 0) and nothing is corrected.
    Any odd number of Z's flips the sign between |000> and |111>, which is a
    logical phase flip.
    """
    qml.Hadamard(wires=0)
    encode()
    for w in DATA:
        qml.PhaseFlip(p, wires=w)
    s01, s12 = measure_syndrome()
    correct(s01, s12)
    encode()  # decode
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)


# ---- Closed forms, used to check the circuits -----------------------------------

def bit_flip_theory(p):
    """Wrong only if 2 or 3 of the 3 qubits flip: 3 p^2 (1 - p) + p^3."""
    return 3 * p**2 * (1 - p) + p**3


def phase_flip_theory(p):
    """Wrong if an odd number of the 3 qubits get Z: (1 - (1 - 2p)^3) / 2."""
    return (1 - (1 - 2 * p) ** 3) / 2
