"""toil_cvflag commands."""
from os.path import abspath, dirname, join, isdir
import os
import gzip
import subprocess
import tempfile

import click
from toil_container import ContainerArgumentParser
from toil_container import ContainerJob

from toil_cvflag import __version__


class CavemanFlagging(ContainerJob):

    """A class to execute caveman flagging jobs."""

    def __init__(self, vcf, options=None, *args, **kwargs):
        """Set variables that will be used in later steps."""
        utils_dir = join(abspath(dirname(__file__)), "caveman_utils")
        self.options = options
        self.vcf = vcf
        self.flag_script = join(utils_dir, "cgpFlagCaVEMan_custom.pl")
        self.flag_config = join(utils_dir, "flag.vcf.custom.config.ini")
        self.flag_to_vcf_config = join(utils_dir, "flag.to.vcf.custom.convert.ini")
        super(CavemanFlagging, self).__init__(options=self.options, *args, **kwargs)

    def run(self, fileStore):
        """Run caveman flagging on vcf."""
        o_vcf = self.vcf.replace(".vcf", ".flagged.vcf")
        cmd = [
            "perl",
            self.flag_script,
            "--input",
            self.vcf,
            "--outFile",
            o_vcf,
            "--species",
            self.options.species,
            "--normBam",
            self.options.normal_bam,
            "-tumBam",
            self.options.tumor_bam,
            "--bedFileLoc",
            self.options.bedFileLoc,
            "--indelBed",
            self.options.indelBed,
            "--unmatchedVCFLoc",
            self.options.unmatchedVCFLoc,
            "--reference",
            self.options.reference + ".fai",  # Reference index (fai) from caveman help
            "--studyType",
            "pulldown" if self.options.sequencing_method == "TGD" else "genomic",
            "--flagConfig",
            self.flag_config,
            "--flagToVcfConfig",
            self.flag_to_vcf_config,
            "--verbose",
        ]

        if self.options.annoBedLoc:
            cmd += [
                "--annoBedLoc",
                self.options.annoBedLoc,
            ]

        # Unicode to string
        cmd = list(map(str, cmd))
        self.call(cmd)

        # gzip and create tbi
        self.call(["bgzip", "-f", o_vcf])
        self.call(["tabix", "-f", "-p", "vcf", o_vcf + ".gz"])


class ConcatVcfs(ContainerJob):

    """A class to concatenate vcfs."""

    def run(self, fileStore):
        """Concatenate a list of vcf files into one vcf."""
        fileStore.logToMaster("start merging...")
        unsorted_merged_vcf = tempfile.NamedTemporaryFile(
            prefix="unsorted", suffix=".vcf", dir=self.options.working_dir, delete=True
        )
        result = []
        for vcf in self.options.vcfs:
            vcf = vcf.replace(".vcf", ".flagged.vcf.gz")
            with gzip.open(vcf, "r") as f:
                lines = f.readlines()
                headers = [l.decode() for l in lines if l.startswith(b"#")]
                variants = [l.decode() for l in lines if not l.startswith(b"#")]
            result.extend(variants)

        with open(unsorted_merged_vcf.name, "w") as f:
            f.write("".join(headers))
            f.write("".join(result))

        fileStore.logToMaster("Concatenated vcf: {}".format(unsorted_merged_vcf.name))

        out_vcf = self.options.out.strip(".gz")
        cmd = ["vcf-sort", unsorted_merged_vcf.name, ">", out_vcf]
        self.call(["bash", "-c", " ".join(cmd)])
        self.call(["bgzip", "-f", out_vcf])
        self.call(["tabix", "-f", "-p", "vcf", out_vcf + ".gz"])
        unsorted_merged_vcf.close()
        for vcf in self.options.vcfs:
            os.remove(vcf)


def get_parser():
    """Get pipeline configuration using toil's."""
    parser = ContainerArgumentParser(
        version=__version__, description="A hello world toil pipeline."
    )

    settings = parser.add_argument_group("pipeline arguments")

    settings.add_argument(
        "--vcf",
        help="Path of vcf file. (Can pass multiple --vcf).",
        required=True,
        type=click.Path(file_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--out",
        help="Output merged vcf file.",
        required=True,
        type=click.Path(dir_okay=True, writable=True, resolve_path=True),
    )
    settings.add_argument(
        "--reference",
        help="Reference .fasta used to left-align indels of vcfs.",
        required=False,
        type=click.Path(file_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--normal-bam",
        help="Path to the normal bam.",
        required=True,
        type=click.Path(file_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--tumor-bam",
        help="Path to the tumor bam.",
        required=True,
        type=click.Path(file_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--indelBed",
        help="A bed file containing germline indels to filter on.",
        required=True,
        type=click.Path(file_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--bedFileLoc",
        help=(
            "Path to a folder containing centromeric, snp, hi seq depth, "
            "simple repeat bed files."
        ),
        required=True,
        type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--unmatchedVCFLoc",
        help=(
            "Path to a directory containing the unmatched VCF normal files listed"
            " in the config file or unmatchedNormal.bed.gz(bed file is used in"
            "preference)."
        ),
        required=True,
        type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--annoBedLoc",
        help=(
            "Path to a folder containing centromeric, snp, hi seq depth, "
            "simple repeat bed files."
        ),
        required=False,
        type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    )
    settings.add_argument(
        "--bin-size",
        help=(
            "Number of variants in a splitted vcf file in caveman flagging."
            "if bin_size > variants in input vcf, no parallization is applied."
        ),
        default=100000,
        required=False,
        type=click.INT,
    )
    settings.add_argument(
        "--sequencing-method", help="WGS or TGD", default=False, required=False
    )
    settings.add_argument(
        "--runtime", help="Runtime minutes for system jobs.", default=90, required=False
    )
    settings.add_argument(
        "--memory", help="Memory for system jobs.", default="4G", required=False
    )
    settings.add_argument(
        "--species", required=False, default="HUMAN",
    )
    return parser


def process_parsed_options(options):
    """Perform validations and add post parsing attributes to `options`."""
    options.working_dir = temp = tempfile.mkdtemp()
    if not isdir(temp):
        subprocess.check_call(["mkdir", "-p", temp])

    if options.writeLogs is not None:
        subprocess.check_call(["mkdir", "-p", options.writeLogs])

    return options


def split_vcf(options):
    """Split large vcf file into smaller files."""
    with gzip.open(options.vcf, "r") as f:
        vcf = None
        vcfs = []
        count = options.bin_size + 1
        header = ""

        for i in f:
            if i.startswith(b"#"):
                header += i.decode()
            else:
                if count > options.bin_size:
                    # close vcf if any
                    vcf and vcf.close() or None

                    # create new vcf
                    vcf = tempfile.NamedTemporaryFile(
                        prefix="split_",
                        suffix=".vcf",
                        dir=options.working_dir,
                        delete=False,
                    )

                    # append to vcfs and write header
                    vcfs.append(vcf.name)
                    vcf.file.write(header)
                    count = 0

                vcf.file.write(i.decode())
                count += 1

    vcf.close()
    click.echo("Splitted {} into {} vcfs".format(options.vcf, len(vcfs)))
    return vcfs


def run_toil(options):
    """Run toil pipeline give an options namespace."""
    kwargs = dict(options=options, runtime=options.runtime, memory=options.memory)
    head_job = ContainerJob(**kwargs)
    options.vcfs = split_vcf(options=options)

    for vcf in options.vcfs:
        head_job.addChild(CavemanFlagging(vcf, **kwargs))

    head_job.addFollowOn(ConcatVcfs(**kwargs))
    ContainerJob.Runner.startToil(head_job, options)


def main():
    """
    Parse options and run toil.

    **Workflow**

    1. Define Options using `get_parser`: build an `arg_parse` object that
       includes both toil options and pipeline specific options. These will be
       separated in different sections of the `--help` text and used by the
       jobs to do the work.

    2. Validate with `process_parsed_options`: once the options are parsed, it
       maybe necessary to conduct *post-parsing* operations such as adding new
       attributes to the `options` namespace or validating combined arguments.

    3. Execute with `run_toil`: this function uses the `options` namespace to
       build and run the toil `DAG`.
    """
    options = get_parser().parse_args()
    options = process_parsed_options(options=options)
    run_toil(options=options)
