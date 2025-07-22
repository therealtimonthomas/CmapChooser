# CmapChooser
A python gui program to choose and play around with `matplotlib` colormaps and normalizations. 


## How To Install
First, you have to download or clone this repository 
```
git clone https://github.com/therealtimonthomas/CmapChooser.git
```
and then go into the folder that contains this file and the `setup.py` file
```
cd CmapChooser
```
You can then simply install the library into your current python enviroment via

```bash
pip3 install .
```

which will ensure that the required libraries (`numpy`, `matplotlib`, and `PySide6`) are also present and aviable in your current python enviroment; if not they are installed automatically. Note that the `PySide6` pack is not super leightweight: it consumes ~600Mb disk space on my machine - be aware of this if you are on a machine with tight quotas.

## Supported Colormaps

The program  supports colormaps from `matplotlib`, `cmasher`, and `cmocean` currently. The later two are used if they are present in your python enviroment and are not automatically installed in the setup process. If you wish to use them (**---which I highly recommend---**), then simply run
```bash
pip3 install cmasher cmocean
```

## How To Use

The envisioned workflow is that you have a 2d numpy-array (in the following this will be called `data`) that represents an image, and you want to play around with different colormaps and normalization options for this image. You can pass this image to CmapChooser in python like `cmap_chooser.choose(data)` and will be prompted with the gui. You may be in a situation where you already saved the image in an hdf5 file, then a simple code snippet to load the image and call CmapChooser is:

```python
import cmap_chooser
import h5py

sn = h5py.File("data/image.hdf5", "r")
data = sn["image"][:,:]
sn.close()

cmap_chooser.choose(data)
```

The a similar code snippet can be used with the `numpy.load` function:

```python
import cmap_chooser
import numpy

data = numpy.load("data/image.npy")

cmap_chooser.choose(data)
```


If you want to save your chosen colormap and the normalization for later use, then simply save the return values from the `choose` function which returns the colormap and normalizations as python objects. This can be accomplished with the `pickle` library. An example code snippet for this pickling workflow is:

```python
cmap, norm = cmap_chooser.choose(data)

import pickle
with open("cmap_norm.pkl", "wb") as f:
    pickle.dump(cmap, f)
    pickle.dump(norm, f)
```

Both the colormap and the normalization can then be read via:

```python
import pickle
with open("cmap_norm.pkl", "rb") as f:
    cmap = pickle.load(cmap, f)
    norm = pickle.load(cmap, f)

import matplotlib.pyplot as plt
plt.imshow(data, cmap=cmap, norm=norm)
plt.show()
```

This two-step process is implemented in the example scripts:

```bash
cd examples
python3 example_choose.py
python3 example_plot.py
```
where `example_choose.py` is calling `CmapChooser` and later saving the colormap and normalization while `example_plot.py` is loading both and using them to do a standard matplotlib `plt.imshow` plot.


## Histogram Normalization

This feature is intended to provide an easy way to instantly get a high-contrast image with no try-and-error fiddling around with the normalization. It works by constructing a normalization such that the pixel-values of the image are uniformly sampling the colorbar (this is done by calculating the CDF of pixel-values and using the CDF as the new normalization function). NOTE: While this process is deterministic, the resulting normalization is probably highly non-linear and its (puristic) scientific interpretation becomes hard. It should be used for illustrative and exploratory purposes.

Symmetric Histogram Normalization is not working right now.

## Planned Features
- Save info about the normalization and cmap in an human-readable way
- Save images from within the program
- Save / load buttons to load colormaps and normalizations from previous sessions
- Expose a way to adjust axis / figure labels etc.

Other wishes for possible modifications are greatly appreciated and can be send to Timon Thomas. 