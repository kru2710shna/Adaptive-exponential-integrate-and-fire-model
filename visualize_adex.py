"""
visualize_adex.py

Run a few standard AdEx experiments and generate plots.

This script will create a 'plots' directory (if it does not exist)
and save PNG figures for:
    - Non-adapting EIF-like spiking
    - Adapting regular spiking
    - Example bursting regime (parameter exploration)
"""

import os
import matplotlib.pyplot as plt

from simulate_adex import simulate_adex


def ensure_dirs():
    """Create plots directory if it doesn't exist."""
    os.makedirs("plots", exist_ok=True)


def plot_trace(t, V, w, title, filename):
    """
    Helper to plot V and w over time and save as a PNG.
    """
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axes[0].plot(t, V)
    axes[0].set_ylabel("V (mV)")
    axes[0].set_title(title)

    axes[1].plot(t, w)
    axes[1].set_ylabel("w (pA)")
    axes[1].set_xlabel("Time (ms)")

    plt.tight_layout()
    out_path = os.path.join("plots", filename)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def experiment_non_adapting():
    """
    Non-adapting EIF-like spiking (a = 0, b = 0).
    Should show roughly constant firing rate.
    """
    print("Running non-adapting EIF experiment...")
    t, V, w, spikes = simulate_adex(
        T=1000.0,
        dt=0.1,
        I_ext=250.0,
        a=0.0,
        b=0.0,
    )
    print(f"Non-adapting: {len(spikes)} spikes")

    plot_trace(
        t,
        V,
        w,
        title="AdEx: Non-adapting EIF (a=0, b=0)",
        filename="adex_non_adapting.png",
    )


def experiment_adapting():
    """
    Adapting regular spiker.
    Should show spike-frequency adaptation (ISI increases over time).
    """
    print("Running adapting regular spiker experiment...")
    t, V, w, spikes = simulate_adex(
        T=1000.0,
        dt=0.1,
        I_ext=250.0,
        a=2.0,
        tau_w=200.0,
        b=60.0,
    )
    print(f"Adapting: {len(spikes)} spikes")

    plot_trace(
        t,
        V,
        w,
        title="AdEx: Spike-Frequency Adaptation",
        filename="adex_adapting.png",
    )


def experiment_bursting():
    """
    Example bursting regime.
    Parameters are a starting point; feel free to tune.
    """
    print("Running bursting-like experiment...")
    t, V, w, spikes = simulate_adex(
        T=1500.0,
        dt=0.1,
        I_ext=200.0,
        a=4.0,
        tau_w=300.0,
        b=120.0,
        DeltaT=2.0,
    )
    print(f"Bursting-like: {len(spikes)} spikes")

    plot_trace(
        t,
        V,
        w,
        title="AdEx: Example bursting regime (tune parameters!)",
        filename="adex_bursting.png",
    )


if __name__ == "__main__":
    ensure_dirs()
    experiment_non_adapting()
    experiment_adapting()
    experiment_bursting()
    print("All experiments completed.")
