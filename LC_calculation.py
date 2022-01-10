import numpy as np

def calc_L(f0, C):
    L = 1/(((2*np.pi*f0) ** 2) * C)

    return L

def calc_N(L, r, length):
    mu0 = 4*np.pi*1e-7
    A = np.pi*r**2
    N = np.sqrt((length*L) / (mu0*A))
    return N

Cmin = 2e-12
Cmax = 120e-12
f0 = 213e6

Lmin = calc_L(f0, Cmax)
Lmax = calc_L(f0, Cmin)

print('Required L range: {:.3} H to {:.3} H'.format(Lmin, Lmax))

r = 7e-3
length = 13e-3

Nmin = calc_N(Lmin, r, length)
Nmax = calc_N(Lmax, r, length)

print('Required N range: {:.3} turns to {:.3} turns'.format(Nmin, Nmax))


