"""Sweep the physical error rate p, check every circuit against its closed form,
and plot logical error rate against physical error rate for both noise types.

Run: uv run python run.py   ->  figures/logical_vs_physical.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import repetition_code as rc

ps = np.linspace(0, 0.6, 31)


def logical_error(circuit):
    # probs(wires=0) is [P(0), P(1)]; the logical qubit started as 0 (or |+>), so P(1) is the error.
    return np.array([circuit(p)[1] for p in ps])


results = {
    "bit flip": (logical_error(rc.bit_flip_unencoded), logical_error(rc.bit_flip_encoded), rc.bit_flip_theory(ps)),
    "phase flip": (logical_error(rc.phase_flip_unencoded), logical_error(rc.phase_flip_encoded), rc.phase_flip_theory(ps)),
}

# Check 1: the simulated circuits match the closed forms. If the syndrome wiring or the
# lookup table were wrong, the encoded curve would leave the formula.
for name, (bare, encoded, theory) in results.items():
    assert np.allclose(bare, ps, atol=1e-9), f"{name}: unencoded qubit should fail with probability p"
    assert np.allclose(encoded, theory, atol=1e-9), f"{name}: encoded circuit disagrees with the formula"
    print(f"{name}: circuit matches 3-qubit formula (max diff {np.abs(encoded - theory).max():.1e})")

# Check 2: where encoding helps against bit flips. 3p^2 - 2p^3 < p holds for 0 < p < 1/2.
bare, encoded, _ = results["bit flip"]
helps = ps[(encoded < bare - 1e-12)]
print(f"bit flip: encoding lowers the error for p in ({helps.min():.2f}, {helps.max():.2f}); break-even at p = 0.5")

# Check 3: against phase flips, encoding is worse than doing nothing (about 3p instead of p).
bare, encoded, _ = results["phase flip"]
print(f"phase flip: encoded error is higher than bare for every p in (0, 0.5): {bool(np.all(encoded[1:-6] > bare[1:-6]))}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (name, (bare, encoded, theory)) in zip(axes, results.items()):
    ax.plot(ps, bare, "k--", label="one bare qubit (= p)")
    ax.plot(ps, encoded, "o", ms=4, label="3-qubit code, simulated")
    ax.plot(ps, theory, "-", lw=1, label="3-qubit code, formula")
    ax.axvline(0.5, color="grey", lw=0.5)
    ax.set_title(f"{name} noise")
    ax.set_xlabel("physical error rate p")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("logical error rate")
axes[0].legend()
fig.suptitle("Repetition code: corrects bit flips below p = 0.5, makes phase flips worse")
fig.tight_layout()
Path("figures").mkdir(exist_ok=True)
fig.savefig("figures/logical_vs_physical.png", dpi=150)
print("saved figures/logical_vs_physical.png")
