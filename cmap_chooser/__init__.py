import sys
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mpl_colors



class HistogramNorm(mpl_colors.Normalize):
    def __init__(self, used_norm, x, y, clip=False):
        self.base_norm = used_norm
        self.x = x
        self.y = y
        mpl_colors.Normalize.__init__(self, None, None, clip)

    def __call__(self, value, clip=None):
        return np.interp(self.base_norm(value), self.x, self.y)

    def inverse(self, value):
        return self.base_norm.inverse(np.interp(value, self.y, self.x))


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

class Colorbar(QLabel):
    def __init__(self, cmap):
        super().__init__()
        super().setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        super().setMinimumSize(400, 30)

        self.trange = np.linspace(0., 1., 512)

        self.colors = cmap(self.trange)

        self.data = np.zeros((2, 512, 4), dtype=np.uint8)
        self.data[0,:,:] = self.colors * 255
        self.data[1,:,:] = self.colors * 255

        height, width = self.data.shape[:2]
        qimage = QImage(self.data, width, height, QImage.Format_RGBA8888)

        self.pixmap = QPixmap(QPixmap.fromImage(qimage))
        super().setPixmap(self.pixmap)
        super().setScaledContents(True)

class ColormapItem(QWidget):
    def __init__(self, app, figure, img, name, cmap):
        super().__init__()

        self.app = app
        self.img = img
        self.figure = figure
        self.vbox = QVBoxLayout()
        self.label = QLabel(name)
        self.colobar = Colorbar(cmap)

        super().setLayout(self.vbox)

        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.colobar)

        super().setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.name = name
        self.name_lowercase = name.lower()

        self.is_selected = False

    def paintEvent(self, event):
        if self.is_selected:
            painter = QPainter(self)
            pen = QPen()
            pen.setWidth(3)
            pen.setBrush(Qt.gray)
            painter.setPen(pen)
            painter.drawRect(1, 1, self.width() - 1, self.height() - 1)
            painter.end()

    def mousePressEvent(self, event):
        self.app.set_colormapitem(self)

    def select(self):
        self.is_selected = True

    def unselect(self):
        self.is_selected = False

class ApplicationWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()

        self.data = data

        self.setWindowTitle("Colomap Chooser")

        self.main = QWidget()
        self.setCentralWidget(self.main)

        hlayout = QHBoxLayout(self.main)
        hlayout_lwidget = QWidget()
        hlayout_lwidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        hlayout_lwidget.setMinimumSize(800, 800)
        hlayout_rwidget = QWidget()
        hlayout_rwidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        hlayout_rwidget.setMinimumSize(400, 0)

        hlayout.addWidget(hlayout_lwidget)
        hlayout.addWidget(hlayout_rwidget)

        plot_layout = QVBoxLayout(hlayout_lwidget)

        self.figure = Figure(figsize=(5, 5))
        self.figure.tight_layout()
        self.figure_canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(NavigationToolbar(self.figure_canvas, self))
        plot_layout.addWidget(self.figure_canvas)

        self.img = self.plot(self.figure, [[0,0,0,1], [1,1,1,1]])

        self.control_layout = QVBoxLayout(hlayout_rwidget)

        self.add_layout_label("Normalization")
        self.combo = QComboBox()
        self.combo.addItems(["Linear", "Logarithmic", "SymLog"])
        self.combo.currentIndexChanged.connect(self.normalization_changed)
        self.control_layout.addWidget(self.combo)


        self.normalization_name = "Linear"
        self.linear_vmin = np.min(self.data)
        self.linear_vmax = np.max(self.data)

        self.log_vmin = self.linear_vmin
        self.log_vmax = self.linear_vmax

        self.symlog_vmin = -np.max([np.abs(self.linear_vmin), np.abs(self.linear_vmax)])
        self.symlog_vmax = +np.max([np.abs(self.linear_vmin), np.abs(self.linear_vmax)])

        self.symlog_linthresh = 1e-2 * self.symlog_vmax
        self.symlog_linscale = 1.


        ###################################################################################
        # linear
        ###################################################################################
        self.norm_box_linear = QWidget()
        norm_vbox = QVBoxLayout()

        # vmin
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmin")
        norm_hbox.addWidget(label_text)
        self.linear_vmin_edit = QLineEdit()
        self.linear_vmin_edit.textChanged.connect(self.linear_vmin_edit_changed)        
        self.linear_vmin_edit.setText(str(self.linear_vmin))
        norm_hbox.addWidget(self.linear_vmin_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        # vmin
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmax")
        norm_hbox.addWidget(label_text)
        self.linear_vmax_edit = QLineEdit()
        self.linear_vmax_edit.textChanged.connect(self.linear_vmax_edit_changed)     
        self.linear_vmax_edit.setText(str(self.linear_vmax))
        norm_hbox.addWidget(self.linear_vmax_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        self.norm_box_linear.setLayout(norm_vbox)
        self.control_layout.addWidget(self.norm_box_linear)

        ###################################################################################
        # logarithmic
        ###################################################################################
        self.norm_box_log = QWidget()
        norm_vbox = QVBoxLayout()

        # vmin
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmin")
        norm_hbox.addWidget(label_text)
        self.log_vmin_edit = QLineEdit()
        self.log_vmin_edit.textChanged.connect(self.log_vmin_edit_changed)        
        self.log_vmin_edit.setText(str(self.log_vmin))
        norm_hbox.addWidget(self.log_vmin_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        # vmax
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmax")
        norm_hbox.addWidget(label_text)
        self.log_vmax_edit = QLineEdit()
        self.log_vmax_edit.textChanged.connect(self.log_vmax_edit_changed)     
        self.log_vmax_edit.setText(str(self.log_vmax))
        norm_hbox.addWidget(self.log_vmax_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        self.norm_box_log.setLayout(norm_vbox)
        self.control_layout.addWidget(self.norm_box_log)

        ###################################################################################
        # sym-log
        ###################################################################################

        self.norm_box_symlog = QWidget()
        norm_vbox = QVBoxLayout()

        # vmin
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmin")
        norm_hbox.addWidget(label_text)
        self.symlog_vmin_edit = QLineEdit()
        self.symlog_vmin_edit.textChanged.connect(self.symlog_vmin_edit_changed)        
        self.symlog_vmin_edit.setText(str(self.symlog_vmin))
        norm_hbox.addWidget(self.symlog_vmin_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        # vmin
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("vmax")
        norm_hbox.addWidget(label_text)
        self.symlog_vmax_edit = QLineEdit()
        self.symlog_vmax_edit.textChanged.connect(self.symlog_vmax_edit_changed)     
        self.symlog_vmax_edit.setText(str(self.symlog_vmax))
        norm_hbox.addWidget(self.symlog_vmax_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        # lintresh
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("linthresh")
        norm_hbox.addWidget(label_text)
        self.symlog_linthresh_edit = QLineEdit()
        self.symlog_linthresh_edit.textChanged.connect(self.symlog_linthresh_edit_changed)     
        self.symlog_linthresh_edit.setText(str(self.symlog_linthresh))
        norm_hbox.addWidget(self.symlog_linthresh_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        # linscale
        item = QWidget()
        norm_hbox = QHBoxLayout()
        label_text = QLabel("linscale")
        norm_hbox.addWidget(label_text)
        self.symlog_linscale_edit = QLineEdit()
        self.symlog_linscale_edit.textChanged.connect(self.symlog_linscale_edit_changed)     
        self.symlog_linscale_edit.setText(str(self.symlog_linscale))
        norm_hbox.addWidget(self.symlog_linscale_edit)
        item.setLayout(norm_hbox)
        norm_vbox.addWidget(item)

        self.norm_box_symlog.setLayout(norm_vbox)
        self.control_layout.addWidget(self.norm_box_symlog)


        ###################################################################################
        # histogram normalization
        ###################################################################################
        self.histogram_normalization = False
        self.histogram_normalization_checkbox = QCheckBox("Histogram Normalization")
        self.histogram_normalization_checkbox.stateChanged.connect(self.histogram_normalization_checkbox_changed)
        self.control_layout.addWidget(self.histogram_normalization_checkbox)

        self.sym_histogram_normalization = False
        self.sym_histogram_normalization_checkbox = QCheckBox("Symmetric Histogram Normalization")
        self.sym_histogram_normalization_checkbox.stateChanged.connect(self.sym_histogram_normalization_checkbox_changed)
        self.control_layout.addWidget(self.sym_histogram_normalization_checkbox)

        ###################################################################################
        # select default norm
        ###################################################################################

        self.select_normalization("Linear")

        ###################################################################################
        # colormap box
        ###################################################################################

        self.add_layout_label("Colormap")
        self.searchbox = QLineEdit()
        self.searchbox.setPlaceholderText("Colormap search...") 
        self.searchbox.textChanged.connect(self.searchbox_textChanged)
        self.control_layout.addWidget(self.searchbox)

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        self.widget.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.control_layout.addWidget(self.scroll)

        try:
            import matplotlib as mpl

            self.add_group_label("matplotlib")
            for key in mpl.colormaps.keys():
                self.add_colormap(key, mpl.colormaps[key])
        except:
            pass

        try:
            import cmocean
            self.add_group_label("cmocean")
            for name in cmocean.cm.cmapnames:
                self.add_colormap(name, getattr(cmocean.cm,name))
                self.add_colormap(name + "_r", getattr(cmocean.cm,name + "_r"))
        except:
            pass
            
        try:
            import cmasher
            self.add_group_label("cmasher")
            for name in cmasher.get_cmap_list():
                self.add_colormap(name, getattr(cmasher,name))
        except:
            pass

        self.vbox.addStretch(1)

        self.selected_colormapitem = None

    def add_layout_label(self, name):
        label_widget = QWidget()
        label_hbox = QHBoxLayout()

        label_text = QLabel(name)
        label_hbox.addWidget(label_text)

        label_hbar = QHLine()
        label_hbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        label_hbox.addWidget(label_hbar)

        label_widget.setLayout(label_hbox)
        self.control_layout.addWidget(label_widget)

    def add_group_label(self, name):
        label_widget = QWidget()
        label_hbox = QHBoxLayout()

        label_text = QLabel(name)
        label_hbox.addWidget(label_text)

        label_hbar = QHLine()
        label_hbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        label_hbox.addWidget(label_hbar)

        label_widget.setLayout(label_hbox)
        self.vbox.addWidget(label_widget)

    def add_colormap(self, name, cmap):
        item = ColormapItem(self, self.figure_canvas, self.img, name, cmap)
        self.vbox.addWidget(item)

    def searchbox_textChanged(self, text):
        if len(text) == 0:
            for item in self.vbox.parentWidget().findChildren(ColormapItem):
                item.show()
        else:
            text = text.lower()

            for item in self.vbox.parentWidget().findChildren(ColormapItem):
                if text in item.name_lowercase:
                    item.show()
                else:
                    item.hide()

    def set_colormapitem(self, item):
        mymap = LinearSegmentedColormap.from_list("", item.colobar.colors)
        self.img.set_cmap(mymap)

        self.colorbar.set_xlabel(item.name)

        self.figure_canvas.draw()

        if not self.selected_colormapitem is None:
            self.selected_colormapitem.unselect()
            self.selected_colormapitem.repaint()
        item.select()
        item.repaint()

        self.selected_colormapitem = item



    def update_normalization(self):

        if self.normalization_name == "Linear":
            self.img.norm = mpl_colors.Normalize(vmin=self.linear_vmin, vmax=self.linear_vmax)

        if self.normalization_name == "Logarithmic":
            self.img.norm = mpl_colors.LogNorm(vmin=self.log_vmin, vmax=self.log_vmax)

        if self.normalization_name == "SymLog":
            self.img.norm = mpl_colors.SymLogNorm(vmin=self.symlog_vmin, vmax=self.symlog_vmax, linthresh=self.symlog_linthresh, linscale=self.symlog_linscale)

        if self.histogram_normalization:

            norm_data = self.img.norm(self.data)
            x = None
            y = None

            if self.sym_histogram_normalization:
                x = np.linspace(0., 1., 10000)

                ym, xm = np.histogram(norm_data[norm_data < 0.5], bins=x[x<0.5])
                ym = np.append(ym, 0)

                yp, xp = np.histogram(norm_data[norm_data > 0.5], bins=x[x>0.5])
                yp = np.append(yp, 0)

                x = np.concatenate((xm, xp))
                y = np.concatenate((ym, yp))
            else:
                x = np.linspace(0., 1., 10000)
                y, x = np.histogram(norm_data, bins=x)
                y = np.append(y, 0)

            y = np.cumsum(y, dtype=np.float64)
            y /= y[-1]

            self.img.norm = HistogramNorm(self.img.norm, x, y)


        self.figure_canvas.draw()


    def linear_vmin_edit_changed(self, text):
        try:
            self.linear_vmin = float(text)
            self.update_normalization()
        except:
            pass

    def linear_vmax_edit_changed(self, text):
        try:
            self.linear_vmax = float(text)
            self.update_normalization()
        except:
            pass


    def log_vmin_edit_changed(self, text):
        try:
            self.log_vmin = float(text)
            self.update_normalization()
        except:
            pass

    def log_vmax_edit_changed(self, text):
        try:
            self.log_vmax = float(text)
            self.update_normalization()
        except:
            pass

    def symlog_vmin_edit_changed(self, text):
        try:
            self.symlog_vmin = float(text)
            self.update_normalization()
        except:
            pass

    def symlog_vmax_edit_changed(self, text):
        try:
            self.symlog_vmax = float(text)
            self.update_normalization()
        except:
            pass

    def symlog_linthresh_edit_changed(self, text):
        try:
            self.symlog_linthresh = float(text)
            self.update_normalization()
        except:
            pass

    def symlog_linscale_edit_changed(self, text):
        try:
            self.symlog_linscale = float(text)
            self.update_normalization()
        except:
            pass

    def histogram_normalization_checkbox_changed(self, state):
        self.histogram_normalization = self.histogram_normalization_checkbox.isChecked()

        try:
            self.update_normalization()
        except:
            pass


    def sym_histogram_normalization_checkbox_changed(self, state):
        self.sym_histogram_normalization = self.sym_histogram_normalization_checkbox.isChecked()

        try:
            self.update_normalization()
        except:
            pass

    def select_normalization(self, name):
        self.norm_box_linear.hide()
        self.norm_box_log.hide()
        self.norm_box_symlog.hide()

        if name == "Linear":
            self.norm_box_linear.show()
            self.normalization_name = name

        if name == "Logarithmic":
            self.norm_box_log.show()
            self.normalization_name = name

        if name == "SymLog":
            self.norm_box_symlog.show()
            self.normalization_name = name

        self.update_normalization()
        print(f"Selected: {name}")

    def normalization_changed(self, index):
        self.select_normalization(self.combo.currentText())


    def plot(self, fig, colors):
        fig.clear()

        mymap = LinearSegmentedColormap.from_list("", colors)

        static_ax = fig.add_axes((0.025, 0.025, 0.95, 0.875))
        img = static_ax.imshow(self.data, cmap=mymap, norm=mpl_colors.Normalize(vmin=-5.0, vmax=-2.5))
        static_ax.set_xticks([])
        static_ax.set_yticks([])

        cax = fig.add_axes([0.025, 0.95, 0.95, 0.05])
        fig.colorbar(img, cax=cax, orientation='horizontal')
        cax.set_xlabel("None")
        self.colorbar = cax

        return img

def choose(data):
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)

    app = ApplicationWindow(data)
    app.show()
    qapp.exec()

    return app.img.get_cmap(), app.img.norm