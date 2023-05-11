import numpy as np

f = 213e6
TX_phase = 0
RX_phase = 0
p1 = 1e3
p2 = np.arange(1.5, 2.6, 0.1) * 1e3
p3 = 0
g1 = 5e3
g2 = 0
rec = 10e3

names = [f"1us-5us-{p[0]}pt{p[1]}us_CoSpinEcho.seq" for p in p2.astype(str)]


for idx, name in enumerate(names):
    data = (f, TX_phase, RX_phase, p1, g1, p2[idx], g2, p3, rec)
    np.savetxt(name, data)



