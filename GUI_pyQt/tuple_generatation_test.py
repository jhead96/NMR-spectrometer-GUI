import numpy as np


x = np.array([1, 2, 3, 4, 5])
y = np.array([[1,2,3,4,5],[5,6,7,8,9]])
print(y)
y_cols = np.size(y, axis=0)
tuple_array = np.empty((x.size, y_cols), dtype=tuple)
for i in range(x.size):
    for j in range(y_cols):
        pair = (x[i], y[j, i])
        tuple_array[i, j] = pair
print(tuple_array)


