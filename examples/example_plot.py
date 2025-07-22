import matplotlib.pyplot as plt
import numpy
import pickle

data = numpy.load("../data/image.npy")

with open("cmap_norm.pkl", "rb") as f:
    cmap = pickle.load(f)
    norm = pickle.load(f)

plt.imshow(data, cmap=cmap, norm=norm)
plt.show()