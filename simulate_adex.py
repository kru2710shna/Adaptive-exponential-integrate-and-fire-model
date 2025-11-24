import numpy as np

def simulate_adex(
    T=100,
    dt=0.1,
    I_ext = 200, # Input Current
    
    # Membrane
    C=200.00,
    gL= 10,
    EL = 70.0,
    
    # Exponential Spike
    VT = -20.0,
    DeltaT=2.0,
    
    # Adaptive Parameters
    a = 2.0,
    tau_w=200.0,
    b=60.0,
    
    # Spike Reset Paramters
    V_reset=-58.0,
    V_spike = 0.0,
    
    V0= None,
    w0 = 0.0
):
    n_steps = int(np.round(T/dt))
    t = np.arange(n_steps) * dt
    
    if np.isscalar(I_ext):
        I = np.full(n_steps, I_ext, dtype=float)
    else:
        I = np.asarray(I_ext, dtype=float)
        if I.shape[0] != n_steps:
            raise ValueError("length does not match")
    
    V = np.zeros(n_steps, dtype=float)
    w = np.zeros(n_steps, dtype=float)
    
    # INIT 
    if V0 is None:
        V[0]=EL
    else:
        V[0] = float(V0)
    
    w[0] = float(w0)
    
    spike_times = []
    
    for i in range(n_steps-1):
        if V[i] >= V_spike:
            V[i] = V_spike
            V[i+1] = V_reset
            w[i+1] = w[i] + b
            
            spike_times.append(V[i])
            continue 
    
        # EXPONENTIAL
        exponential_term = np.exp((V[i]-VT) / DeltaT)
        
        dvdt = (-gL * (V[i]- EL) + gL * DeltaT * exponential_term - w[i] + I[i] ) / C
        
        dwdt = (a*(V[i]-EL) - w[i]) / tau_w
        
        V[i + 1] = V[i] + dt * dvdt
        w[i + 1] = w[i] + dt * dwdt
        
        return t , V, w, np.array(spike_times)


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