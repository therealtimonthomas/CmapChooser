import cmap_chooser
import numpy

data = numpy.load("../data/image.npy")

cmap, norm = cmap_chooser.choose(data)

import pickle
with open("cmap_norm.pkl", "wb") as f:
    pickle.dump(cmap, f)
    pickle.dump(norm, f)