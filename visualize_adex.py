"""
visualize_adex.py

Run a few standard AdEx experiments and generate plots.

This script will create a 'plots' directory (if it does not exist)
and save PNG figures for:
    - Non-adapting EIF-like spiking
    - Adapting regular spiking
    - Example bursting regime (parameter exploration)
    - F–I curve (firing rate vs injected current)
"""

import os
import numpy as np
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


# ---------------------------------------------------------------------
#  Experiments: non-adapting, adapting, bursting
# ---------------------------------------------------------------------

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
    (With current values you may or may not get clean bursts; this
    is mainly a playground for parameter exploration.)
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


# ---------------------------------------------------------------------
#  F–I curve (firing rate vs injected current)
# ---------------------------------------------------------------------

def compute_firing_rate(spike_times_ms, T_ms, steady_window_ms=500.0):
    """
    Compute steady-state firing rate in Hz from spike times.

    Parameters
    ----------
    spike_times_ms : 1D array-like
        Spike times in ms.
    T_ms : float
        Total simulation time in ms.
    steady_window_ms : float
        Window length (ms) at the *end* of the simulation used to
        estimate the steady-state rate.

    Returns
    -------
    rate_hz : float
        Firing rate in Hz (spikes per second) in the chosen window.
    """
    spike_times_ms = np.asarray(spike_times_ms, dtype=float)
    if spike_times_ms.size == 0:
        return 0.0

    # Use spikes only in the last steady_window_ms of the simulation
    window_start = T_ms - steady_window_ms
    mask = (spike_times_ms >= window_start) & (spike_times_ms <= T_ms)
    n_spikes_window = mask.sum()

    if steady_window_ms <= 0:
        return 0.0

    rate_hz = n_spikes_window / (steady_window_ms / 1000.0)
    return rate_hz


def experiment_fi_curve():
    """
    Generate an F–I curve (firing rate vs injected current).

    We sweep a range of constant input currents I_ext and measure the
    steady-state firing rate of an *adapting* AdEx neuron.
    """
    print("Running F–I curve experiment...")

    # Range of currents to test (pA)
    # You can tweak this range based on your neuron parameters.
    currents = np.linspace(0.0, 400.0, 21)  # 0, 20, 40, ..., 400 pA

    T_ms = 2000.0       # simulate 2 seconds to let adaptation settle
    dt = 0.1
    steady_window_ms = 500.0  # use last 500 ms for steady-state rate

    rates = []

    for I in currents:
        print(f"  I_ext = {I:.1f} pA ...", end="", flush=True)
        t, V, w, spikes = simulate_adex(
            T=T_ms,
            dt=dt,
            I_ext=I,
            # Use same parameters as adapting regular spiker
            a=2.0,
            tau_w=200.0,
            b=60.0,
        )
        rate_hz = compute_firing_rate(spikes, T_ms, steady_window_ms)
        rates.append(rate_hz)
        print(f" rate = {rate_hz:.2f} Hz")

    rates = np.array(rates)

    # Plot F–I curve
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(currents, rates, marker="o")
    ax.set_xlabel("Injected current I_ext (pA)")
    ax.set_ylabel("Steady-state firing rate (Hz)")
    ax.set_title("AdEx F–I Curve (adapting neuron)")
    ax.grid(True, alpha=0.3)

    out_path = os.path.join("plots", "adex_fi_curve.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved F–I curve: {out_path}")

    # Optional: also dump raw data for future analysis
    data_out = os.path.join("plots", "adex_fi_curve_data.txt")
    np.savetxt(
        data_out,
        np.column_stack([currents, rates]),
        header="I_ext_pA  firing_rate_Hz",
        fmt="%.3f"
    )
    print(f"Saved F–I data: {data_out}")


# ---------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------

if __name__ == "__main__":
    ensure_dirs()
    experiment_non_adapting()
    experiment_adapting()
    experiment_bursting()
    experiment_fi_curve()
    print("All experiments completed.")
