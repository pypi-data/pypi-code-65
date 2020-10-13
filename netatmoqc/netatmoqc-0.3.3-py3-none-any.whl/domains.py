#!/usr/bin/env python3
import attr
import copy
import logging
import numpy as np
import plotly.graph_objects as go
import pyproj
from .plots import DEF_FIGSHOW_CONFIG, get_domain_fig

logger = logging.getLogger(__name__)

# We'll approximate the Earth as a sphere
_EARTH_RADIUS = 6.3710088e6  # Mean earth radius in meters
_EQUATOR_PERIM = 2 * np.pi * _EARTH_RADIUS


@attr.s(kw_only=True)
class Domain:
    nlon = attr.ib(default=1)
    nlat = attr.ib(default=1)
    lonc = attr.ib(default=0.0)
    latc = attr.ib(default=0.0)
    lon0 = attr.ib(default=0.0)
    lat0 = attr.ib(default=0.0)
    gsize = attr.ib(default=_EQUATOR_PERIM)
    ezone = attr.ib(default=0)
    lmrt = attr.ib(default=False)
    tstep = attr.ib(default=0.0)
    name = attr.ib(default="")
    # The params below are netatmoqc-specific.
    # nsplit_lon and nsplit_lat are employed to split the domain in subdomains
    # for preliminary clustering
    nsplit_lon = attr.ib(default=1)
    nsplit_lat = attr.ib(default=1)
    # thinning_grid_coarse_factor is used for post-clustering thinning
    thinning_grid_coarse_factor = attr.ib(default=1)

    def __attrs_post_init__(self):
        if self.lmrt and abs(self.lat0) > 0:
            logger.warning(
                "lat0 should be 0 if lmrt=True. Resetting lat0 from %s to 0.",
                self.lat0,
            )
            self.lat0 = 0.0
        self._Proj = pyproj.Proj(self.projparams)

        # Creating vectorized versions of some methods
        self.contains_lonlat = np.vectorize(self._contains_lonlat_non_vec)
        self.cart2grid = np.vectorize(self._cart2grid_non_vec)

    @classmethod
    def construct_from_dict(cls, config):
        return cls(
            name=config.name,
            tstep=config.tstep,
            nlon=config.nlon,
            nlat=config.nlat,
            lonc=config.lonc,
            latc=config.latc,
            lon0=config.lon0,
            lat0=config.lat0,
            gsize=config.gsize,
            ezone=config.ezone,
            lmrt=config.lmrt,
            nsplit_lon=config.split.lon,
            nsplit_lat=config.split.lat,
            thinning_grid_coarse_factor=config.thinning_grid_coarse_factor,
        )

    @property
    def proj(self):
        latrange = 180 * (self.nlat * self.gsize) / _EQUATOR_PERIM
        if self.lmrt or latrange > 35 or np.isclose(latrange, 0):
            # <https://proj.org/operations/projections/merc.html>
            # <https://desktop.arcgis.com/en/arcmap/10.3/guide-books/
            #  map-projections/mercator.htm>
            return "merc"
        elif np.isclose(self.lat0, 90.0):
            # <https://proj.org/operations/projections/stere.html>
            # <https://desktop.arcgis.com/en/arcmap/10.3/guide-books/
            #  map-projections/polar-stereographic.htm>
            return "stere"
        else:
            # <https://proj.org/operations/projections/lcc.html>
            # <https://desktop.arcgis.com/en/arcmap/10.3/guide-books/
            #  map-projections/lambert-conformal-conic.htm>
            return "lcc"

    @property
    def projname(self):
        proj2projname = dict(
            merc="Mercator",
            stere="Polar Stereographic",
            lcc="Lambert Conformal Conic",
        )
        try:
            return proj2projname[self.proj]
        except KeyError:
            return self.proj

    @property
    def plotly_projname(self):
        proj2projname = dict(
            merc="mercator", stere="stereographic", lcc="conic conformal",
        )
        try:
            return proj2projname[self.proj]
        except KeyError:
            return self.proj

    @property
    def projparams(self):
        return dict(
            # Lambert conformal conic
            proj=self.proj,
            R=_EARTH_RADIUS,
            lat_0=self.lat0,  # Lat of domain center. Is this maybe latc?
            lon_0=self.lon0,  # Lon of domain center. Is this maybe lonc?
            lat_1=self.lat0,  # 1st standard parallel
            lat_2=self.lat0,  # 2nd standard parallel
            # a, b: semimajor and semiminor axes (ellipsoidal planet)
            a=_EARTH_RADIUS,
            b=_EARTH_RADIUS,
        )

    @property
    def ngrid(self):
        return self.nlat * self.nlon

    def change_grid_spacing(self, factor):
        """ Change grid spacing, with factor = new.gsize / old.gsize """
        factor = abs(factor)
        if factor > 1:
            # New grid is coarser than the original
            assert np.isclose(factor, np.rint(factor))
            factor = int(factor)
            assert self.nlon % factor == 0
            assert self.nlat % factor == 0
            transform = lambda x: x / factor
        else:
            # New grid is finer than or equal to the original
            inv_factor = factor ** -1
            assert np.isclose(inv_factor, np.rint(inv_factor))
            inv_factor = int(inv_factor)
            factor = inv_factor ** -1
            transform = lambda x: x * inv_factor

        self.gsize *= factor
        self.nlon = int(transform(self.nlon))
        self.nlat = int(transform(self.nlat))
        self.ezone = int(np.rint(transform(self.ezone)))

    def get_coarser(self, factor):
        """ Copy of domain but with courser grid by a factor "factor" """
        assert factor >= 1
        new = copy.deepcopy(self)
        new.change_grid_spacing(factor=factor)
        return new

    def get_finer(self, factor):
        """ Copy of domain but with finer grid by a factor "factor" """
        assert factor >= 1
        new = copy.deepcopy(self)
        new.change_grid_spacing(factor=factor ** -1)
        return new

    def get_thinning_grid_version(self):
        """ Return another version of self, but with the thinning grid """
        if self.thinning_grid_coarse_factor < 1:
            return None
        else:
            return self.get_coarser(factor=self.thinning_grid_coarse_factor)

    @property
    def n_subdomains(self):
        return self.nsplit_lon * self.nsplit_lat

    def split(self, nsplit_lon=None, nsplit_lat=None):
        """Split a domain "nsplit_lon(lat)" times along the lon(lat) axis"""

        if nsplit_lon is None:
            nsplit_lon = self.nsplit_lon
        if nsplit_lat is None:
            nsplit_lat = self.nsplit_lat

        assert isinstance(nsplit_lon, int)
        assert isinstance(nsplit_lat, int)
        assert nsplit_lon > 0
        assert nsplit_lat > 0
        assert self.nlon % nsplit_lon == 0
        assert self.nlat % nsplit_lat == 0

        new_nlat = self.nlat // nsplit_lat
        new_nlon = self.nlon // nsplit_lon
        nsplit = nsplit_lon * nsplit_lat

        splits = []
        for iy in range(nsplit_lat):
            new_yc = self.ymin + (iy + 0.5) * new_nlat * self.gsize
            for ix in range(nsplit_lon):
                new_xc = self.xmin + (ix + 0.5) * new_nlon * self.gsize
                new_lonc, new_latc = self.xy2lonlat(new_xc, new_yc)
                split = self.__class__(
                    name="{} Split {}/{}".format(
                        self.name, iy * nsplit_lat + ix + 1, nsplit
                    ),
                    tstep=self.tstep,
                    nlon=new_nlon,
                    nlat=new_nlat,
                    lonc=new_lonc,
                    latc=new_latc,
                    lon0=self.lon0,
                    lat0=self.lat0,
                    gsize=self.gsize,
                    ezone=self.ezone,
                    lmrt=self.lmrt,
                )
                splits.append(split)
        return splits

    def trim_obs(self, df):
        """Remove from dataframe "df" those obs that lie outside the domain"""
        return df[self.contains_lonlat(df.lon, df.lat)].copy()

    def lonlat2xy(self, lon, lat):
        # lat, lon in degrees
        # returns x, y in meters
        return self._Proj(latitude=lat, longitude=lon)

    def xy2lonlat(self, x, y):
        # x, y in meters
        # return lat, lon in degrees
        lon, lat = self._Proj(x, y, inverse=True)
        return lon, lat

    @property
    def center_xy(self):
        return self.lonlat2xy(lon=self.lonc, lat=self.latc)

    @property
    def xres(self):
        return self.gsize

    @property
    def yres(self):
        return self.gsize

    @property
    def xmax(self):
        return self.center_xy[0] + 0.5 * self.nlon * self.xres

    @property
    def xmin(self):
        return self.center_xy[0] - 0.5 * self.nlon * self.xres

    @property
    def ymax(self):
        return self.center_xy[1] + 0.5 * self.nlat * self.yres

    @property
    def ymin(self):
        return self.center_xy[1] - 0.5 * self.nlat * self.yres

    @property
    def ezone_xmax(self):
        return self.xmax + self.ezone * self.xres

    @property
    def ezone_ymax(self):
        return self.ymax + self.ezone * self.yres

    @property
    def domain_corners_xy(self):
        return (
            (self.xmin, self.ymin),
            (self.xmax, self.ymin),
            (self.xmax, self.ymax),
            (self.xmin, self.ymax),
        )

    @property
    def domain_corners_lonlat(self):
        return tuple(self.xy2lonlat(*xy) for xy in self.domain_corners_xy)

    @property
    def ezone_corners_xy(self):
        return (
            (self.xmax, self.ymin),
            (self.ezone_xmax, self.ymin),
            (self.ezone_xmax, self.ezone_ymax),
            (self.xmin, self.ezone_ymax),
            (self.xmin, self.ymax),
            (self.xmax, self.ymax),
        )

    @property
    def ezone_corners_lonlat(self):
        return tuple(self.xy2lonlat(*xy) for xy in self.ezone_corners_xy)

    @property
    def minlat(self):
        return min(lonlat[1] for lonlat in self.domain_corners_lonlat)

    @property
    def minlon(self):
        return min(lonlat[0] for lonlat in self.domain_corners_lonlat)

    @property
    def maxlat(self):
        return max(lonlat[1] for lonlat in self.domain_corners_lonlat)

    @property
    def maxlon(self):
        return max(lonlat[0] for lonlat in self.domain_corners_lonlat)

    @property
    def ezone_maxlat(self):
        return max(lonlat[1] for lonlat in self.ezone_corners_lonlat)

    @property
    def ezone_maxlon(self):
        return max(lonlat[0] for lonlat in self.ezone_corners_lonlat)

    @property
    def ezone_minlat(self):
        return min(lonlat[1] for lonlat in self.ezone_corners_lonlat)

    @property
    def ezone_minlon(self):
        return min(lonlat[0] for lonlat in self.ezone_corners_lonlat)

    @property
    def lat_range(self):
        return self.minlat, self.maxlat

    @property
    def lon_range(self):
        return self.minlon, self.maxlon

    def _cart2grid_non_vec(self, x, y):
        """ Takes (x, y) and returns grid (i, j) """
        i = int((x - self.xmin) / self.gsize)
        j = int((y - self.ymin) / self.gsize)
        if i < 0 or i > self.ngrid - 1:
            i = None
        if j < 0 or j > self.ngrid - 1:
            j = None
        return i, j

    def lonlat2grid(self, lon, lat):
        x, y = self.lonlat2xy(lon, lat)
        return self.cart2grid(x, y)

    def get_grid_ij2xy_map(self):
        # We can then work with x=grid2x[i, j], y=grid2y[i, j]
        xvals = np.linspace(self.xmin, self.xmax, self.nlon, endpoint=False)
        yvals = np.linspace(self.ymin, self.ymax, self.nlat, endpoint=False)
        grid2x, grid2y = np.meshgrid(xvals, yvals)
        return grid2x, grid2y

    def get_grid_ij2lonlat_map(self):
        return self.xy2lonlat(*self.get_grid_ij2xy_map())

    def _contains_lonlat_non_vec(self, lon, lat):
        x, y = self.lonlat2xy(lon, lat)
        return (
            x >= self.xmin
            and x < self.xmax
            and y >= self.ymin
            and y < self.ymax
        )

    def get_fig(self, **kwargs):
        return get_domain_fig(self, **kwargs)

    def show(self, config=None, **kwargs):
        # This "config" is plotly's fig.show config, not our parsed config file
        default_config = DEF_FIGSHOW_CONFIG.copy()
        if config is not None:
            default_config.update(config)
        config = default_config

        fig = self.get_fig(**kwargs)
        fig.show(config=config)
