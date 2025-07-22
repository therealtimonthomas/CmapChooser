import matplotlib.pyplot as plt
import h5py
import pickle

sn = h5py.File("../data/image.hdf5", "r")
data = sn["image"][:,:]
sn.close()

with open("cmap_norm.pkl", "rb") as f:
    cmap = pickle.load(f)
    norm = pickle.load(f)

plt.imshow(data, cmap=cmap, norm=norm)
plt.show()