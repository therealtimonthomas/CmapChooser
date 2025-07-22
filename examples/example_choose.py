import cmap_chooser
import h5py

sn = h5py.File("../data/image.hdf5", "r")
data = sn["image"][:,:]
sn.close()

cmap, norm = cmap_chooser.choose(data)

import pickle
with open("cmap_norm.pkl", "wb") as f:
    pickle.dump(cmap, f)
    pickle.dump(norm, f)