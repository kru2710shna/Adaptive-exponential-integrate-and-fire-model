"""
simulate_adex.py

Adaptive Exponential Integrate-and-Fire (AdEx) neuron simulator.

Implements:
    C dV/dt = -gL (V - EL)
              + gL * DeltaT * exp((V - VT)/DeltaT)
              - w
              + I_ext(t)

    tau_w dw/dt = a (V - EL) - w

with spike/reset rule:
    if V >= V_spike:
        V <- V_reset
        w <- w + b
"""

import numpy as np


def simulate_adex(
    T=1000.0,      # total simulation time (ms)
    dt=0.1,        # time step (ms)

    # Input current (scalar or array of length n_steps)
    I_ext=200.0,   # pA

    # Membrane / leak parameters
    C=200.0,       # pF
    gL=10.0,       # nS
    EL=-70.0,      # mV

    # Exponential spike-initiation parameters
    VT=-50.0,      # mV (effective threshold)
    DeltaT=2.0,    # mV (slope factor)

    # Adaptation parameters
    a=2.0,         # nS (subthreshold adaptation)
    tau_w=200.0,   # ms
    b=60.0,        # pA (spike-triggered increment)

    # Spike/reset parameters
    V_reset=-58.0, # mV
    V_spike=0.0,   # mV (cutoff to declare spike)

    # Initial conditions
    V0=None,       # if None, start at EL
    w0=0.0
):
    """
    Simulate a single AdEx neuron using Euler integration.

    Parameters
    ----------
    T : float
        Total simulation time in ms.
    dt : float
        Time step in ms.
    I_ext : float or array-like
        External current in pA. Scalar for constant current, or
        array of length T/dt for time-varying current.
    C, gL, EL, VT, DeltaT, a, tau_w, b, V_reset, V_spike :
        AdEx model parameters.
    V0 : float or None
        Initial membrane potential (mV). If None, uses EL.
    w0 : float
        Initial adaptation variable (pA).

    Returns
    -------
    t : ndarray, shape (n_steps,)
        Time array in ms.
    V : ndarray, shape (n_steps,)
        Membrane potential trace in mV.
    w : ndarray, shape (n_steps,)
        Adaptation variable trace in pA.
    spikes : ndarray, shape (n_spikes,)
        Spike times in ms.
    """
    # Number of time steps
    n_steps = int(np.round(T / dt))
    t = np.arange(n_steps) * dt

    # Handle input current as scalar or time-varying array
    if np.isscalar(I_ext):
        I = np.full(n_steps, I_ext, dtype=float)
    else:
        I = np.asarray(I_ext, dtype=float)
        if I.shape[0] != n_steps:
            raise ValueError(
                f"I_ext length {I.shape[0]} does not match n_steps {n_steps}"
            )

    # Allocate arrays for V and w
    V = np.zeros(n_steps, dtype=float)
    w = np.zeros(n_steps, dtype=float)

    # Initial conditions
    if V0 is None:
        V[0] = EL
    else:
        V[0] = float(V0)
    w[0] = float(w0)

    spike_times = []

    # Main Euler integration loop
    for i in range(n_steps - 1):
        # --- Spike event check ---
        if V[i] >= V_spike:
            # Clamp spike peak (for nicer plots)
            V[i] = V_spike

            # Reset voltage and update adaptation
            V[i + 1] = V_reset
            w[i + 1] = w[i] + b

            # Record spike time
            spike_times.append(t[i])
            continue

        # --- Continuous dynamics (no spike this step) ---

        # Exponential spike-initiation term
        exponential_term = np.exp((V[i] - VT) / DeltaT)

        # Voltage derivative dV/dt (mV/ms)
        # C dV/dt = -gL(V - EL) + gL * DeltaT * exp((V - VT)/DeltaT) - w + I
        dVdt = (
            -gL * (V[i] - EL)
            + gL * DeltaT * exponential_term
            - w[i]
            + I[i]
        ) / C

        # Adaptation derivative dw/dt
        # tau_w dw/dt = a(V - EL) - w
        dwdt = (a * (V[i] - EL) - w[i]) / tau_w

        # Euler update
        V[i + 1] = V[i] + dt * dVdt
        w[i + 1] = w[i] + dt * dwdt

    return t, V, w, np.array(spike_times)


if __name__ == "__main__":
    # Minimal smoke test when running this file directly
    import matplotlib.pyplot as plt

    t, V, w, spikes = simulate_adex(T=500.0, dt=0.1, I_ext=250.0)

    print(f"Simulated {t[-1]} ms with {len(spikes)} spikes.")
    print("Spike times (ms):", spikes)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].plot(t, V)
    axes[0].set_ylabel("V (mV)")
    axes[0].set_title("AdEx test run")

    axes[1].plot(t, w)
    axes[1].set_ylabel("w (pA)")
    axes[1].set_xlabel("Time (ms)")

    plt.tight_layout()
    plt.show()
