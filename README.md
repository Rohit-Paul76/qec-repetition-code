# qec-repetition-code

3-qubit repetition code in PennyLane (`default.mixed`): encode, add bit- or phase-flip noise, measure the syndrome with ancillas, correct with a lookup table, compare logical vs physical error rate.

![logical vs physical error rate](figures/logical_vs_physical.png)

- Bit flips: logical error goes from p to 3p^2 - 2p^3, so encoding helps for all p < 0.5.
- Phase flips: Z doesn't change any parity, so the code can't see them, and 3 qubits fail about 3x as often as 1. That's why the surface code checks both X and Z parities (next repo: qec-vqc-decoder).

Simulated curves match the closed forms, 3p^2(1-p) + p^3 and (1 - (1-2p)^3)/2, to about 1e-14.

Next steps
- Noise on the ancillas and CNOTs (circuit-level), and repeated syndrome rounds.
- The 9-qubit Shor code, which handles both bit and phase flips.

```
uv run python run.py
```
