from os import path
import posixpath
import numpy as np
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from ...io.utils import get_first_hdf5_entry, get_h5_value
from ...io.writer import NXProcessWriter
from ...misc.histogram import PartialHistogram, VolumeHistogram, hist_as_2Darray
from ..logger import Logger, LoggerOrPrint
from .utils import parse_params_values
from .cli_configs import HistogramConfig


class VolumesHistogram:
    """
    A class for extracting or computing histograms of one or several volumes.
    """
    def __init__(self, fnames, output_file, chunk_size_slices=100, chunk_size_GB=None, nbins=1e6, logger=None):
        """
        Initialize a VolumesHistogram object.

        Parameters
        -----------
        fnames: list of str
            List of paths to HDF5 files.
            To specify an entry for each file name, use the "?" separator:
            /path/to/file.h5?entry0001
        output_file: str
            Path to the output file
        write_histogram_if_computed: bool, optional
            Whether to write histograms that are computed to a file.
            Some volumes might be missing their histogram. In this case, the histogram
            is computed, and the result is written to a dedicated file in the same
            directory as 'output_file'.
            Default is True.
        """
        self._get_files_and_entries(fnames)
        self.chunk_size_slices = chunk_size_slices
        self.chunk_size_GB = chunk_size_GB
        self.nbins = nbins
        self.logger = LoggerOrPrint(logger)
        self.output_file = output_file


    def _get_files_and_entries(self, fnames):
        res_fnames = []
        res_entries = []
        for fname in fnames:
            if "?" not in fname:
                entry = None
            else:
                fname, entry = fname.split("?")
                if entry == "":
                    entry = None
            res_fnames.append(fname)
            res_entries.append(entry)
        self.fnames = res_fnames
        self.entries = res_entries


    def _get_config_onevolume(self, fname, entry):
        return {
            "chunk_size_slices": self.chunk_size_slices,
            "chunk_size_GB": self.chunk_size_GB,
            "bins": self.nbins,
            "filename": fname,
            "entry": entry,
        }


    def _get_config(self):
        conf = self._get_config_onevolume("", "")
        conf.pop("filename")
        conf.pop("entry")
        conf["filenames"] = self.fnames
        conf["entries"] = [entry if entry is not None else "None" for entry in self.entries]
        return conf


    def _write_histogram_onevolume(self, fname, entry, histogram):
        output_file = path.join(
            path.dirname(self.output_file),
            path.splitext(path.basename(fname))[0]
        ) + "_histogram" + path.splitext(fname)[1]
        self.logger.info(
            "Writing histogram of %s into %s" % (fname, output_file)
        )
        writer = NXProcessWriter(output_file, entry, filemode="w", overwrite=True)
        writer.write(
            hist_as_2Darray(histogram),
            "histogram",
            config=self._get_config_onevolume(fname, entry)
        )


    def get_histogram_single_volume(self, fname, entry, write_histogram_if_computed=True):
        entry = entry or get_first_hdf5_entry(fname)
        hist_path = posixpath.join(entry, "histogram" , "results", "data")
        rec_path = posixpath.join(entry, "reconstruction", "results" , "data")
        rec_url = DataUrl(file_path=fname, data_path=rec_path)
        hist = get_h5_value(fname, hist_path)
        if hist is None:
            self.logger.info("No histogram found in %s, computing it" % fname)
            vol_histogrammer = VolumeHistogram(
                rec_url,
                chunk_size_slices=self.chunk_size_slices,
                chunk_size_GB=self.chunk_size_GB,
                nbins=self.nbins,
                logger=self.logger
            )
            hist = vol_histogrammer.compute_volume_histogram()
            if write_histogram_if_computed:
                self._write_histogram_onevolume(fname, entry, hist)
            hist = hist_as_2Darray(hist)
        return hist


    def get_histogram(self):
        histograms = []
        for fname, entry in zip(self.fnames, self.entries):
            self.logger.info("Getting histogram for %s" % fname)
            hist = self.get_histogram_single_volume(fname, entry)
            histograms.append(hist)
        self.logger.info("Merging histograms")
        histogrammer = PartialHistogram(method="fixed_bins_number", num_bins=self.nbins)
        hist = histogrammer.merge_histograms(histograms, dont_truncate_bins=True)
        return hist


    def write_histogram(self, hist):
        self.logger.info("Writing final histogram to %s" % (self.output_file))
        writer = NXProcessWriter(self.output_file, "entry0000", filemode="w", overwrite=True)
        writer.write(
            hist_as_2Darray(hist),
            "histogram",
            config=self._get_config()
        )


def histogram_cli():
    args = parse_params_values(
        HistogramConfig,
        parser_description="Extract/compute histogram of volume(s)."
    )
    logger = Logger(
        "nabu_histogram", level=args["loglevel"], logfile="nabu_histogram.log"
    )
    output = args["output_file"].split("?")[0]
    if path.exists(output):
        logger.fatal("Output file %s already exists, not overwriting it" % output)
        exit(1)
    chunk_size_gb = float(args["chunk_size_GB"])
    if chunk_size_gb <= 0:
        chunk_size_gb = None
    histogramer = VolumesHistogram(
        args["h5_file"],
        output,
        chunk_size_slices=int(args["chunk_size_slices"]),
        chunk_size_GB=chunk_size_gb,
        nbins=int(args["bins"]),
        logger=logger
    )
    hist = histogramer.get_histogram()
    histogramer.write_histogram(hist)


if __name__ == "__main__":
    histogram_cli()
