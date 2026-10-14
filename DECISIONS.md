# Decisions

Every choice in this project, the other options, why this one was picked, and what would change with a different pick.

## 1. Which code: the 3-qubit repetition code

| Option | What it protects against | Qubits |
|---|---|---|
| **Repetition code (chosen)** | bit flips (X) only | 3 data + 2 ancillas |
| Phase-flip code (same code, in the Hadamard basis) | phase flips (Z) only | 3 + 2 |
| Shor code | any single-qubit error (X, Z or both) | 9 |
| Steane code | any single-qubit error | 7 |
| Surface code | any error, scales to large distances | 9 data at distance 3 (see `qec-vqc-decoder`) |

**Why:** it has every part of error correction (encode, measure a syndrome, decode, correct) with the fewest moving parts, and its weakness (blind to phase flips) is the reason the bigger codes exist. The phase-flip panel of the figure shows that weakness.

**With another pick:** Shor or Steane would correct both error types, but with 7–9 qubits and 6–8 syndrome bits the lookup table and the circuit are no longer readable at a glance.

## 2. How many data qubits: 3

**Options:** 3, 5, 7, … (any odd number; the count is the code distance d, the number of flips needed to change the logical value).

**Why 3:** the smallest d that corrects one error. With d qubits the code fails when more than half of them flip, so the logical error rate falls roughly like p^((d+1)/2) for small p. Every odd d breaks even at p = 0.5.

**With a larger d:** the curve below p = 0.5 drops faster, but the syndrome has d − 1 bits and the lookup table grows to 2^(d−1) rows.

## 3. Noise model: independent flips on data qubits, after encoding

**Options:**
- **Code capacity (chosen):** each data qubit flips with probability p, once, after encoding. Encoding, syndrome measurement and correction are perfect.
- Phenomenological: also lets the syndrome measurement itself be wrong.
- Circuit-level: every gate and measurement can fail, including the CNOTs into the ancillas.
- Depolarizing: X, Y or Z, each with probability p/3, instead of only X.

**Why:** it has a closed form, 3p²(1 − p) + p³, so the circuit can be checked exactly (`run.py`, check 1). It isolates the question "does the code idea work" from "does the hardware work".

**With a more realistic model:** the ancillas can report a wrong syndrome, so one round of measurement is no longer enough; the syndrome is repeated over several rounds and the decoder looks at all of them. The break-even point moves below 0.5.

## 4. Simulator: `default.mixed` (density matrix)

**Options:**
- **`default.mixed` (chosen):** stores the full density matrix, so noise channels (`qml.BitFlip`, `qml.PhaseFlip`) give exact probabilities.
- `default.qubit` with shots: sample random runs and count failures (Monte Carlo). The answer has sampling noise.
- `stim`: a dedicated simulator for this class of circuits, fast to thousands of qubits.

**Why:** 5 qubits is a 32 × 32 density matrix, so exact simulation is cheap, and exact numbers make the check against the formula a strict equality (differences around 1e-14).

**With another pick:** shots would need error bars. `stim` is the right tool once codes get large (the surface-code project uses a NumPy sampler instead, see its DECISIONS).

## 5. Reading the syndrome: ancillas plus mid-circuit measurement

**Options:**
- **Ancillas (chosen):** CNOT each pair of data qubits into an ancilla, measure only the ancillas (`qml.measure`), then apply a correction conditioned on the result (`qml.cond`).
- Measure the data qubits directly and take a majority vote.
- No measurement: correct with Toffoli gates controlled by the ancillas (coherent correction).

**Why:** measuring the data qubits collapses a|000> + b|111> to one branch, which destroys the stored state; the code would only work for classical bits. The ancillas record whether pairs agree, which is the same in both branches, so a and b survive. Mid-circuit measurement is how real hardware does it.

**With coherent correction:** same result in this simulation, but the ancillas end up entangled with the error and must be reset before the next round.

## 6. Decoder: lookup table

**Options:** lookup table (chosen), majority vote on measured data, a learned decoder.

**Why:** with 2 syndrome bits there are only 4 cases, and for p < 0.5 a single flip is more likely than two, so "flip the one qubit the syndrome points to" is the best possible decoder here.

**With another pick:** majority vote needs the data measured (see 5). A learned decoder has nothing to learn at this size; it becomes interesting when the syndrome is large and errors are correlated, which is the question of `qec-vqc-decoder`.

## 7. What "logical error rate" means here

**Options:**
- **Prepare one fixed state (chosen):** |0> for bit flips, |+> for phase flips. Decode and read P(wrong).
- Average fidelity over all input states.

**Why:** under bit-flip noise the whole process acts on the logical qubit as "apply a logical X with probability p_L", whatever the input, so one input that X changes (|0>) measures p_L exactly. The same holds for phase flips with |+> (Z changes |+> to |->, but leaves |0> alone, which is why the phase test uses |+> and an X-basis readout).

**With average fidelity:** a single number per p that mixes in states the error does not affect; it would hide where p_L comes from.

## 8. Sweep range: p from 0 to 0.6

**Why:** to show both sides of the break-even point at 0.5. Above it, flips are more likely than not, the lookup table "corrects" in the wrong direction, and the code is worse than a bare qubit. Nothing depends on the exact grid (31 points).
