"""Matplotlib-related widgets"""

from .widget import DOMWidget
from IPython.utils.traitlets import Unicode, Enum, Dict, Bool, List, Any
from collections import OrderedDict
from matplotlib.markers import MarkerStyle
from matplotlib.lines import Line2D
from numpy import linspace
import matplotlib.cm
from matplotlib.backends.backend_svg import RendererSVG, XMLWriter
from StringIO import StringIO
from threading import Lock
from IPython.utils.py3compat import unicode_type

def _marker_to_svg(m, size=12, linewidth=1.5, color=(0,0,0)):
    l = Line2D((size/2,), (size/2,), linestyle="None",
               marker=m,
               markersize=size/2, markeredgewidth=linewidth,
               markeredgecolor=color, markerfacecolor=(0.75, 0.75, 0.75))
    store = StringIO()
    rend = RendererSVG(width=size, height=size, svgwriter=store)
    l.draw(rend)
    rend.finalize()
    return store.getvalue()

_MARKER_CODES = MarkerStyle.markers.keys()
_MARKER_SVG = {m: _marker_to_svg(m) for m in _MARKER_CODES}
MARKER_SVG = lambda x: _MARKER_SVG[x] if x in _MARKER_SVG else _marker_to_svg(x)

def _linestyle_to_svg(ls, width=64, height=None, linewidth=2, color=(0,0,0)):
    if height is None: height = width/8
    l = Line2D((width/8, 7*width/8), (height/2, height/2),
               color=color, linewidth=linewidth, linestyle=ls)
    store = StringIO()
    rend = RendererSVG(width=width, height=height, svgwriter=store)
    l.draw(rend)
    rend.finalize()
    return store.getvalue()

_LINE_CODES = Line2D.lineStyles.keys()
_LINE_SVG = {l: _linestyle_to_svg(l) for l in _LINE_CODES}
LINE_SVG = lambda x: _LINE_SVG[x] if x in _LINE_SVG else _linestyle_to_svg(x)

def _cmap_to_svg(name, width=256, height=None):
    if height is None: height = width/32

    store = StringIO()
    writer = XMLWriter(store)
    writer.start("svg", width='%ipt' % width, height='%ipt' % height,
                 version='1.1', viewBox="0 0 %i %i" % (width, height),
                 xmlns="http://www.w3.org/2000/svg")
    writer.start("rect", width='%i'%width, height='%i'%height,
                 fill="url(#cmap_gradient_%s)" % name)
    writer.end() #rect
    writer.end() #svg
    return store.getvalue()

def _cmap_to_svg_defs(names):
    store = StringIO()
    writer = XMLWriter(store)
    writer.start("svg", width=0, height=0, version="1.1",
                 xmlns="http://www.w3.org/2000/svg")
    writer.start("defs")
    for name in names:
        rawdata = matplotlib.cm.datad[name]
        colormap = matplotlib.cm.cmap_d[name]

        if 'red' in rawdata:
            if isinstance(rawdata['red'], (list, tuple)):
                segpoints = set()
                for cc in ('red', 'green', 'blue'):
                    for p in rawdata[cc]:
                        segpoints.add(p[0])
                xpos = sorted(segpoints)
            else:
                xpos = linspace(0, 1, 100)
        else:
            xpos = [p[0] for p in rawdata]

        writer.start("linearGradient", id="cmap_gradient_%s" % name,
                     x1="0%", y1="0%", x2="100%", y2="0%")
        for i, pos in enumerate(xpos):
            color = map(lambda x: int(x*255), colormap(pos))
            red, green, blue, alpha = color
            offset = int(pos * 100)
            writer.start("stop", offset='%i%%' % offset,
                         style="stop-color:rgb(%i,%i,%i);stop-opacity:1" % (red, green, blue))
            writer.end() #stop
        writer.end() #linearGradient
    writer.end() #defs
    writer.end() #svg
    return store.getvalue()


# from http://matplotlib.org/examples/color/colormaps_reference.html
_CLASS_CMAP = {
    'Sequential': ('binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu',
                   'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn',
                   'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                   'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'bone', 'cool',
                   'copper', 'gist_gray', 'gist_heat', 'gray', 'hot', 'pink',
                   'spring', 'summer', 'winter'),
    'Diverging':  ('BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu',
                   'RdGy', 'RdYlBu', 'RdYlGn', 'seismic'),
    'Qualitative':('Accent', 'Dark2', 'hsv', 'Paired', 'Pastel1', 'Pastel2',
                   'Set1', 'Set2', 'Set3', 'Spectral', 'spectral',
                   'nipy_spectral'),
    'Other':      ('gist_earth', 'gist_ncar', 'gist_rainbow', 'gist_stern',
                   'jet', 'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2',
                   'ocean', 'rainbow', 'terrain', 'flag', 'prism')}



_CMAP_CODES = [c for c in matplotlib.cm.datad.keys() if not c.endswith("_r")]
_CMAP_DEFS = _cmap_to_svg_defs(_CMAP_CODES)
_CMAP_SVG = {unicode_type(c): _cmap_to_svg(c) for c in _CMAP_CODES}
CMAP_SVG = lambda x: _CMAP_SVG[x] if x in _CMAP_SVG else _cmap_to_svg(x)
_CMAP_REVERSED = {k: k.endswith("_r") for k in _CMAP_CODES}
_CMAP_CLASS = {vv: k for k, v in _CLASS_CMAP.items() for vv in v}
#print("unannotated cmaps", set(_CMAP_CODES) - set(_CMAP_CLASS.keys()))

DEFAULT = {"marker": ".", "line": "-", "cmap": "YlGnBu"}

class MPLSelectionWidget(DOMWidget):
    _view_name = Unicode('MPLDropdownView', sync=True)
    mpl_type = Enum([u'marker', u'line', u'cmap'], u'marker',
        help="MPL widget type", sync=True)
    value = Any(help="Selected value", sync=True)
    codes = List(Any, sync=True)
    svg = List(Unicode, sync=True)
    disabled = Bool(False, help="Enable or disable user changes", sync=True)
    description = Unicode(help="Description of the value this widget represents", sync=True)
    tabs = Dict(sync=True)

    def __init__(self, *args, **kwargs):
        if 'mpl_type' in kwargs:
            self.mpl_type = kwargs.pop('mpl_type')
        get_svg = {'marker': MARKER_SVG,
                   'line': LINE_SVG,
                   'cmap': CMAP_SVG}[self.mpl_type]
        if 'codes' in kwargs:
            self.codes = list(kwargs.pop('codes'))

        else:
            self.codes = {'marker': _MARKER_CODES,
                          'line': _LINE_CODES,
                          'cmap': _CMAP_CODES}[self.mpl_type]
        self.svg = [unicode_type(get_svg(c)) for c in self.codes]
        if 'value' not in kwargs:
            self.value = DEFAULT[self.mpl_type]
        if self.mpl_type == 'cmap':
            self.tabs = _CLASS_CMAP

        DOMWidget.__init__(self, *args, **kwargs)
