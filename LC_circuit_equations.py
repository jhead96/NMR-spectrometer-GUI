import numpy as np

"""
LC circuit equations:
    f - Frequency [Hz]
    L - Inductance [H]
    C - Capacitance [C]
"""

def L_circuit(f, C):
    L = 1/(((2*np.pi*f) ** 2) * C)
    return L

def f_circuit(C, L):
    f = 1/(2*np.pi*np.sqrt(L*C)) / 1e6
    return f

def C_circuit(f, L):
    C = 1/((2*np.pi*f) ** 2 * L)
    return C


"""
Coil inductance equations:
    L - Inductance (H)
    l - Length (m)
    N - Number of turns
    r - Coil radius (m)
"""

def N_coil(L, r, l):
    mu0 = 4*np.pi*1e-7
    A = np.pi*r**2

    N = np.sqrt((l*L) / (mu0*A))
    return N

def L_coil(r, N, l):
    mu0 = 4 * np.pi * 1e-7
    A = np.pi * r ** 2

    L = mu0 * ((N**2) * A) / l
    return L


Cmin = 1e-12
Cmax = 50e-12
f0 = 213e6

Lmin = L_circuit(f0, Cmax)
Lmax = L_circuit(f0, Cmin)

print('Required L range: {:.3} H to {:.3} H'.format(Lmin, Lmax))

r = 7e-3
length = 13e-3

Nmin = N_coil(Lmin, r, length)
Nmax = N_coil(Lmax, r, length)

print('Required N range: {:.3} turns to {:.3} turns'.format(Nmin, Nmax))


