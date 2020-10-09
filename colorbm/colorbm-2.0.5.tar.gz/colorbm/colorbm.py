from matplotlib.colors import ListedColormap, LinearSegmentedColormap, to_hex, to_rgb
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
import sys
from .palettes import palettes_hex


class available_colormaps(object):
    # Colormap Lists
    # SEABORN
    seaborn_div = ['icefire', 'vlag']
    seaborn_seq = ['mako', 'rocket', 'crest', 'flare']
    seaborn = seaborn_div + seaborn_seq

    # SCIENTIFIC
    scientific_div = ['broc', 'cork', 'vik', 'lisbon', 'tofino', 'berlin', 'oleron']
    scientific_seq = ['acton', 'bamako', 'batlow', 'bilbao', 'buda', 'davos', 'devon', 'grayc', 'hawaii', 'imola',
                      'lajolla', 'lapaz', 'nuuk', 'oslo', 'roma', 'tokyo', 'turku', 'romao', 'broco', 'corko',
                      'viko']
    scientific = scientific_div + scientific_seq

    # CMasher
    cmasher_div = ['iceburn', 'redshift', 'watermelon', 'wildfire', 'guppy', 'pride', 'fusion', 'seasons', 'viola',
                   'waterlily']
    cmasher_seq = ['amber', 'apple', 'arctic', 'bubblegum', 'chroma', 'dusk', 'eclipse', 'ember', 'fall', 'flamingo',
                   'freeze', 'gem', 'gothic', 'heat', 'horizon', 'jungle', 'lavender', 'lilac', 'neon', 'neutral',
                   'nuclear', 'ocean', 'pepper', 'rainforest', 'savanna', 'sepia', 'sunburst', 'swamp', 'toxic', 'tree',
                   'voltage']
    cmasher = cmasher_div + cmasher_seq

    # cmocean
    cmocean_div = ['topo', 'balance', 'delta', 'curl', 'diff', 'tarn']
    cmocean_seq = ['thermal', 'haline', 'solar', 'ice', 'gray', 'oxy', 'deep', 'dense', 'algae', 'matter', 'turbid',
                   'speed', 'amp', 'tempo', 'rain', 'phase']
    cmocean = cmocean_div + cmocean_seq

    # CARTO
    carto_div = ['armyrose', 'fall', 'geyser', 'tealrose', 'tropic', 'earth']
    carto_seq = ['burg', 'burgyl', 'redor', 'oryel', 'peach', 'pinkyl', 'mint', 'blugrn', 'darkmint', 'emrld', 'bluyl',
                 'teal', 'tealgrn', 'purp', 'purpor', 'sunset', 'magenta', 'sunsetdark', 'brwnyl']
    carto = carto_div + carto_seq

    # Material Design
    mat_div = []
    mat_seq = ['matred', 'matpink', 'matpurple', 'matdpurple', 'matindigo', 'matblue', 'matlblue', 'matcyan', 'matteal',
               'matgreen', 'matlgreen', 'matlime', 'matyellow', 'matamber', 'matorange', 'matdorange', 'matbrown',
               'matgrey', 'matbgrey']
    mat = mat_div + mat_seq

    # Colorcet
    colorcet_div = ['cet-c1', 'cet-c1s', 'cet-c2', 'cet-c2s', 'cet-c4', 'cet-c4s', 'cet-c5', 'cet-c5s', 'cet-cbc1',
                    'cet-cbc2', 'cet-cbd1', 'cet-cbtc1', 'cet-cbtc2', 'cet-cbtd1', 'cet-d1', 'cet-d10', 'cet-d11',
                    'cet-d12', 'cet-d13', 'cet-d1a', 'cet-d2', 'cet-d3', 'cet-d4', 'cet-d6', 'cet-d7', 'cet-d8',
                    'cet-d9']
    colorcet_seq = ['cet-cbl1', 'cet-cbl2', 'cet-cbtl1', 'cet-cbtl2', 'cet-i1', 'cet-i2', 'cet-i3', 'cet-l1', 'cet-l10',
                    'cet-l11', 'cet-l12', 'cet-l13', 'cet-l14', 'cet-l15', 'cet-l16', 'cet-l17', 'cet-l18', 'cet-l19',
                    'cet-l2', 'cet-l3', 'cet-l4', 'cet-l5', 'cet-l6', 'cet-l7', 'cet-l8', 'cet-l9', 'cet-r1', 'cet-r2',
                    'cet-r3']
    colorcet = colorcet_div + colorcet_seq

    # MISC
    misc_div = []
    misc_seq = ['oliveblue', 'gsea', 'turbo', 'parula']
    misc = misc_div + misc_seq

    colormaps_div = seaborn_div + scientific_div + cmasher_div + cmocean_div + carto_div + mat_div + colorcet_div + misc_div
    colormaps_seq = seaborn_seq + scientific_seq + cmasher_seq + cmocean_seq + carto_seq + mat_seq + colorcet_seq + misc_seq
    colormaps = colormaps_div + colormaps_seq

    cmap_dic = {
        'seaborn': seaborn, 'scientific': scientific, 'cmasher': cmasher, 'cmocean': cmocean,
        'carto': carto, 'mat': mat, 'misc': misc, 'colorcet': colorcet}
    cmap_dic_key = [*cmap_dic]

    cmap_dic_div = {
        'seaborn': seaborn_div, 'scientific': scientific_div, 'cmasher': cmasher_div, 'cmocean': cmocean_div,
        'carto': carto_div, 'mat': mat_div, 'misc': misc_div, 'colorcet': colorcet_div}
    cmap_dic_div_key = [*cmap_dic_div]

    cmap_dic_seq = {
        'seaborn': seaborn_seq, 'scientific': scientific_seq, 'cmasher': cmasher_seq, 'cmocean': cmocean_seq,
        'carto': carto_seq, 'mat': mat_seq, 'misc': misc_seq, 'colorcet': colorcet_seq}
    cmap_dic_seq_key = [*cmap_dic_seq]

    def __init__(self, scheme=None):
        self.scheme = scheme

    @property
    def all(self):
        if self.scheme is None:
            return available_colormaps.colormaps
        elif self.scheme in available_colormaps.cmap_dic_key:
            return available_colormaps.cmap_dic[self.scheme]
        else:
            print('No such colormap scheme')
            sys.exit(0)

    @property
    def div(self):
        if self.scheme is None:
            return available_colormaps.colormaps_div
        elif self.scheme in available_colormaps.cmap_dic_div_key:
            return available_colormaps.cmap_dic_div[self.scheme]
        else:
            print('No such colormap scheme')
            sys.exit(0)

    @property
    def seq(self):
        if self.scheme is None:
            return available_colormaps.colormaps_seq
        elif self.scheme in available_colormaps.cmap_dic_seq_key:
            return available_colormaps.cmap_dic_seq[self.scheme]
        else:
            print('No such colormap scheme')
            sys.exit(0)


class available_palettes(object):
    # Palettes HEX in Dictionary
    # ggsci
    pal_dic_ggsci = {
        'npg': palettes_hex.npg, 'aaas': palettes_hex.aaas, 'nejm': palettes_hex.nejm,
        'lancet': palettes_hex.lancet, 'jama': palettes_hex.jama, 'jco': palettes_hex.jco,
        'ucscgb': palettes_hex.ucscgb, 'd3_20': palettes_hex.d3_20,
        'd3_10': palettes_hex.d3_10, 'd3_20b': palettes_hex.d3_20b, 'd3_20c': palettes_hex.d3_20c,
        'locuszoom': palettes_hex.locuszoom, 'igv': palettes_hex.igv,
        'alternating': palettes_hex.igv_alternating,
        'cosmic_hallmarks_dark': palettes_hex.cosmic_hallmarks_dark,
        'cosmic_hallmarks_light': palettes_hex.cosmic_hallmarks_light,
        'cosmic_signature_substitutions': palettes_hex.cosmic_signature_substitutions,
        'uchicago': palettes_hex.uchicago, 'uchicago_light': palettes_hex.uchicago_light,
        'uchicago_dark': palettes_hex.uchicago_dark,
        'startrek': palettes_hex.startrek,
        'tron': palettes_hex.tron, 'futurama': palettes_hex.futurama,
        'rickandmorty': palettes_hex.rickandmorty, 'simpsons': palettes_hex.simpsons}
    pal_key_ggsci = [*pal_dic_ggsci]

    # paintings
    pal_dic_paintings = {
        'starrynight': palettes_hex.starrynight,
        'monalisa': palettes_hex.monalisa, 'scream': palettes_hex.scream, 'lastsupper': palettes_hex.lastsupper,
        'afternoon': palettes_hex.afternoon,
        'optometrist': palettes_hex.optometrist,
        'kanagawa': palettes_hex.kanagawa, 'kanagawa_alternative': palettes_hex.kanagawa_alternative,
        'kiss': palettes_hex.kiss, 'memory': palettes_hex.memory,
        'lilies': palettes_hex.lilies}
    pal_key_paintings = [*pal_dic_paintings]

    # CARTO
    pal_dic_carto = {
        'antique': palettes_hex.antique, 'bold': palettes_hex.bold, 'pastel': palettes_hex.pastel,
        'prism': palettes_hex.prism, 'safe': palettes_hex.safe, 'vivid': palettes_hex.vivid}
    pal_key_carto = [*pal_dic_carto]

    # MISC
    pal_dic_misc = {
        'economist': palettes_hex.economist, 'economist_primary': palettes_hex.economist_primary,
        'economist_alternative': palettes_hex.economist_alternative}
    pal_key_misc = [*pal_dic_misc]

    # Nintendo
    pal_dic_nintendo = {
        'mario': palettes_hex.mario, 'luigi': palettes_hex.luigi, 'yoshi': palettes_hex.yoshi,
        'isabelle': palettes_hex.isabelle, 'tomnook': palettes_hex.tomnook}
    pal_key_nintendo = [*pal_dic_nintendo]

    pal_dic_colorcet = {'glasbey': palettes_hex.glasbey, 'glasbey_bw': palettes_hex.glasbey_bw,
                        'glasbey_category10': palettes_hex.glasbey_category10,
                        'glasbey_cool': palettes_hex.glasbey_cool, 'glasbey_dark': palettes_hex.glasbey_dark,
                        'glasbey_hv': palettes_hex.glasbey_hv, 'glasbey_light': palettes_hex.glasbey_light,
                        'glasbey_warm': palettes_hex.glasbey_warm}
    pal_key_colorcet = [*pal_dic_colorcet]

    pal_dic = {**pal_dic_ggsci, **pal_dic_paintings, **pal_dic_carto, **pal_dic_misc, **pal_dic_nintendo, **pal_dic_colorcet}
    pal_key = [*pal_dic]

    # Store palettes name list in dictionary
    pal_scheme_dic = {
        'ggsci': pal_key_ggsci, 'paintings': pal_key_paintings, 'carto': pal_key_carto, 'misc': pal_key_misc,
        'nintendo': pal_key_nintendo, 'colorcet': pal_key_colorcet}
    pal_scheme = [*pal_scheme_dic]

    def __init__(self, cpal=None):
        self.cpal = cpal

    @property
    def get(self):
        if self.cpal is None:
            return available_palettes.pal_key
        elif self.cpal in available_palettes.pal_scheme:
            return available_palettes.pal_scheme_dic[self.cpal]
        else:
            print('No such color palette scheme')
            sys.exit(0)


class seq(object):
    def __init__(self, cmap, n=256):
        self.cmap = cmap
        self.rgb = np.loadtxt(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sequential\{}.rgb'.format(self.cmap)),
            delimiter=',')
        self.n = n

    @property
    def as_cmap(self):
        return LinearSegmentedColormap.from_list(self.cmap, self.rgb, N=self.n)

    @property
    def as_cmap_r(self):
        return LinearSegmentedColormap.from_list(self.cmap, self.rgb[::-1], N=self.n)

    @property
    def as_hex(self):
        self.hex = seq.srgblist_to_hex(self.rgb)
        return self.hex

    @property
    def as_rgb(self):
        return self.rgb

    # Convert RBG list to HEX list
    @staticmethod
    def srgblist_to_hex(s):
        h = []
        for x in enumerate(s):
            h += [to_hex(x[1])]
        return h


class div(seq):
    def __init__(self, cmap, n=256):
        self.cmap = cmap
        self.rgb = np.loadtxt(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'diverging\{}.rgb'.format(self.cmap)),
            delimiter=',')
        self.n = n


class pal(object):

    def __init__(self, cpal):
        self.cpal = cpal

    @property
    def as_cmap(self):
        if self.cpal not in available_palettes.pal_key:
            print('No such color palette')
            sys.exit(0)
        else:
            return ListedColormap(available_palettes.pal_dic[self.cpal])

    @property
    def as_cmap_r(self):
        if self.cpal not in available_palettes.pal_key:
            print('No such color palette')
            sys.exit(0)
        else:
            return ListedColormap(available_palettes.pal_dic[self.cpal][::-1])

    @property
    def as_hex(self):
        if self.cpal not in available_palettes.pal_key:
            print('No such color palette')
            sys.exit(0)
        else:
            return available_palettes.pal_dic[self.cpal]

    @property
    def as_rgb(self):
        if self.cpal not in available_palettes.pal_key:
            print('No such color palette')
            sys.exit(0)
        else:
            return pal.hexlist_to_rgb(available_palettes.pal_dic[self.cpal])

    # Convert HEX list to RGB list
    @staticmethod
    def hexlist_to_rgb(s):
        r = np.empty((0, 3))
        for x in enumerate(s):
            r = np.vstack((r, to_rgb(x[1])))
        return r


class pcolor(object):

    def __init__(self, cmap, n=256):
        self.cmap = cmap
        self.n = n
        if self.cmap in available_colormaps.colormaps_div:
            self.type = 'diverging'
        elif self.cmap in available_colormaps.colormaps_seq:
            self.type = 'sequential'
        elif self.cmap in available_palettes.pal_key:
            self.type = 'palettes'
        else:
            print('No such colormap or palette')
            sys.exit(0)

    def show(self, **kwargs):

        rev = kwargs.get('reversed', False)

        if self.type == 'palettes':
            testPlots(self.cmap).scatterPlot
        else:
            if not rev:
                if self.type == 'diverging':
                    testPlots(self.cmap).imagePlot(div(self.cmap, self.n).as_cmap, div=True)
                elif self.type == 'sequential':
                    testPlots(self.cmap).imagePlot(seq(self.cmap, self.n).as_cmap)

            else:
                if self.type == 'diverging':
                    testPlots(self.cmap).imagePlot(div(self.cmap, self.n).as_cmap_r, div=True)
                elif self.type == 'sequential':
                    testPlots(self.cmap).imagePlot(seq(self.cmap, self.n).as_cmap_r)

    def to_xml(self, **kwargs):

        wd = kwargs.get('wd', os.getcwd())
        filename = kwargs.get('filename', self.cmap)

        if self.type == 'diverging':
            rgblist = div(self.cmap).as_rgb
        elif self.type == 'sequential':
            rgblist = seq(self.cmap).as_rgb
        else:
            print('Only colormaps are supported!')
            sys.exit(0)
        points = np.linspace(0, 1, rgblist.shape[0])
        f = open(os.path.join(wd, '{}.xml'.format(filename)), 'w', newline='\n')
        print('<ColorMaps>', file=f)
        print('<ColorMap name="{}" space="RGB">'.format(self.cmap), file=f)

        for i, x in enumerate(rgblist):
            print(
                '<Point x="{:1.8f}" o="{:1.8f}" r="{:1.8f}" g="{:1.8f}" b="{:1.8f}"/>'.format(points[i], points[i],
                                                                                              x[0], x[1],
                                                                                              x[2]), file=f)
        print('</ColorMap>', file=f)
        print('</ColorMaps>', file=f)

        print('输出xml文件成功')
        print('文件名为：{}.xml'.format(filename))
        print('输出文件夹路径为：{}'.format(wd))

    def to_csv(self, **kwargs):

        wd = kwargs.get('wd', os.getcwd())
        filename = kwargs.get('filename', self.cmap)
        fmt = kwargs.get('fmt', 'rgb')

        if fmt == 'rgb':
            if self.type == 'diverging':
                olist = div(self.cmap).as_rgb
            elif self.type == 'sequential':
                olist = seq(self.cmap).as_rgb
            else:
                olist = pal(self.cmap).as_rgb
            np.savetxt(os.path.join(wd, '{}.csv'.format(filename)), olist, delimiter=',', fmt='%1.8f')

        elif fmt == 'hex':
            if self.type == 'diverging':
                olist = div(self.cmap).as_hex
            elif self.type == 'sequential':
                olist = seq(self.cmap).as_hex
            else:
                olist = pal(self.cmap).as_hex

            olist = np.array(olist).reshape(-1, 1)
            np.savetxt(os.path.join(wd, '{}.csv'.format(filename)), olist, delimiter=',', fmt='%s')
        else:
            print('错误的格式!')
            sys.exit(0)

        print('输出csv文件成功')
        print('输出颜色格式为：{}'.format(fmt))
        print('文件名为：{}.csv'.format(filename))
        print('输出文件夹路径为：{}'.format(wd))


class testPlots(object):

    def __init__(self, cmap):
        self.cmap = cmap

    def imagePlot(self, cmapObj, **kwargs):

        x = np.random.random((128, 128))
        x = x * 256

        divPlot = kwargs.get('div', False)
        if divPlot:
            x -= 128
        else:
            pass

        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        im = ax.imshow(x, extent=[-x.shape[1] / 2., x.shape[1] / 2., -x.shape[0] / 2., x.shape[0] / 2.],
                       interpolation='gaussian',
                       cmap=cmapObj)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.2)
        plt.colorbar(im, cax=cax)
        plt.show()

    @property
    def scatterPlot(self):

        plt.rcParams['scatter.edgecolors'] = 000000

        np.random.seed(19680801)
        N = 100
        x = np.random.rand(N)
        y = np.random.rand(N)

        fig, ax = plt.subplots()
        colors = np.random.rand(N)
        area = (30 * np.random.rand(N)) ** 2  # 0 to 15 point radii

        ax.scatter(x, y, s=area, c=colors, alpha=0.5, cmap=pal(self.cmap).as_cmap)
        plt.show()
