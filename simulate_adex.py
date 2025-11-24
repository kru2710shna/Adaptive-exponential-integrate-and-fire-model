import numpy as np

def stimulate_adex(
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
    
    if np.isscaler(I_ext):
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
        