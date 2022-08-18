import numpy as np
import matplotlib.pyplot as plt
from scope_readers import GwInstekReader

fp = r"GW_instek_scope_test_data/GW_instek_scope_test_1.csv"

x = GwInstekReader(fp)

x.plot_data()
