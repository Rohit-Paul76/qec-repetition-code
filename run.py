from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import repetition_code as rc

p_vals = np.linspace(0, 0.6, 31)


def logical_err(circuit):
    return np.array([circuit(p)[1] for p in p_vals])


res = {
    "bit flip": (logical_err(rc.bitflip_bare), logical_err(rc.bitflip_code), rc.bitflip_formula(p_vals)),
    "phase flip": (logical_err(rc.phaseflip_bare), logical_err(rc.phaseflip_code), rc.phaseflip_formula(p_vals)),
}

for name, (bare, coded, formula) in res.items():
    assert np.allclose(bare, p_vals, atol=1e-9), f"{name}: bare qubit != p"
    assert np.allclose(coded, formula, atol=1e-9), f"{name}: circuit != formula"
    print(f"{name}: circuit matches 3-qubit formula (max diff {np.abs(coded - formula).max():.1e})")

bare, coded, _ = res["bit flip"]
helps = p_vals[(coded < bare - 1e-12)]
print(f"bit flip: encoding lowers the error for p in ({helps.min():.2f}, {helps.max():.2f}); break-even at p = 0.5")

bare, coded, _ = res["phase flip"]
print(f"phase flip: encoded error is higher than bare for every p in (0, 0.5): {bool(np.all(coded[1:-6] > bare[1:-6]))}")

fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (name, (bare, coded, formula)) in zip(axs, res.items()):
    ax.plot(p_vals, bare, "k--", label="one bare qubit (= p)")
    ax.plot(p_vals, coded, "o", ms=4, label="3-qubit code, simulated")
    ax.plot(p_vals, formula, "-", lw=1, label="3-qubit code, formula")
    ax.axvline(0.5, color="grey", lw=0.5)
    ax.set_title(f"{name} noise")
    ax.set_xlabel("physical error rate p")
    ax.grid(alpha=0.3)
axs[0].set_ylabel("logical error rate")
axs[0].legend()
fig.suptitle("Repetition code: corrects bit flips below p = 0.5, makes phase flips worse")
fig.tight_layout()
Path("figures").mkdir(exist_ok=True)
fig.savefig("figures/logical_vs_physical.png", dpi=150)
print("saved figures/logical_vs_physical.png")
