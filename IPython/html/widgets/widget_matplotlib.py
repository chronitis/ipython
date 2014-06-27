"""Matplotlib-related widgets"""

from .widget import DOMWidget
from IPython.utils.traitlets import Unicode, List, Bool, Any, Dict, TraitError
from .widget_selection import _SelectionWidget


from matplotlib.markers import MarkerStyle
from matplotlib.lines import Line2D
import matplotlib.cm
from matplotlib.backends.backend_svg import RendererSVG, XMLWriter
from StringIO import StringIO

def _marker_to_svg(m, size=32, linewidth=2, color=(0,0,0)):
    l = Line2D((size/2,), (size/2,), linestyle="None",
               marker=m,
               markersize=size/2, markeredgewidth=linewidth,
               markeredgecolor=color, markerfacecolor=(0.75, 0.75, 0.75))
    store = StringIO()
    rend = RendererSVG(width=size, height=size, svgwriter=store)
    l.draw(rend)
    rend.finalize()
    return store.getvalue()

_MARKER_SVG = {m: _marker_to_svg(m) for m in MarkerStyle.markers}
MARKER_SVG = lambda x: _MARKER_SVG[x] if x in _MARKER_SVG else _marker_to_svg(x)

def _linestyle_to_svg(ls, size=64, linewidth=2, color=(0,0,0)):
    width = size
    height = size/4
    l = Line2D((width/8, 7*width/8), (height/2, height/2),
               color=color, linewidth=linewidth, linestyle=ls)
    store = StringIO()
    rend = RendererSVG(width=width, height=height, svgwriter=store)
    l.draw(rend)
    rend.finalize()
    return store.getvalue()

_LINE_SVG = {l: _linestyle_to_svg(l) for l in Line2D.lineStyles}
LINE_SVG = lambda x: _LINE_SVG[x] if x in _LINE_SVG else _linestyle_to_svg(x)

def _cmap_to_svg(name, size=512):
    width=size
    height=size/32

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

    store = StringIO()
    writer = XMLWriter(store)
    writer.start("svg", width='%ipt' % width, height='%ipt' % height)
    writer.start("defs")
    writer.start("linearGradient", id="cmap", x1="0%", y1="0%", x2="100%", y2="0%")
    for i, pos in enumerate(xpos):
        color = map(lambda x: int(x*255), colormap(pos))
        red, green, blue, alpha = color
        offset = int(pos * 100)
        writer.start("stop", offset='%i%%' % offset,
                     style="stop-color:rgb(%i,%i,%i);stop-opacity:1" % (red, green, blue))
        writer.end() #stop
    writer.end() #linearGradient
    writer.end() #defs
    writer.start("rect", width='%i'%width, height='%i'%height, fill="url(#cmap)")
    writer.end() #rect
    writer.end() #svg
    return store.getvalue()

_CMAP_SVG = {c: _cmap_to_svg(c) for c in matplotlib.cm.datad}
CMAP_SVG = lambda x: _CMAP_SVG[x] if x in _CMAP_SVG else _cmap_to_svg(x)


class MPLSelectionWidget(_SelectionWidget):
    _view_name = Unicode('SVGDropdownView', sync=True)
    mpl_type = Enum([u'marker', u'line', u'cmap'], u'marker',
        help="MPL widget type", sync=True)

    def __init__(self, *pargs, **kwargs):
        if 'mpl_type' in kwargs:
            self.mpl_type = kwargs.pop('mpl_type')
        get_svg = {'marker': MARKER_SVG, 'line': LINE_SVG, 'cmap': CMAP_SVG}[self.mpl_type]
        if 'values' in kwargs:
            values = kwargs.pop('values')
            if isinstance(values, list):
                self.values = OrderedDict((unicode_type(v), get_svg(v)) for v in values)
            elif isinstance(values, dict):
                self.values = values
        else:
            self.values = {'marker': _MARKER_SVG, 'line': _LINE_SVG, 'cmap': _CMAP_SVG}[self.mpl_type]
        _SelectionWidget.__init__(self, *args, **kwargs)

