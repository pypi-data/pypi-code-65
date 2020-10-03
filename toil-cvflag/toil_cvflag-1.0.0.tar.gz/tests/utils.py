"""Utils for tests."""
from os.path import join, dirname, abspath

ROOT = abspath(dirname(__file__))

DATA = join(ROOT, "data")

TEST = {
    "input_vcf": join(DATA, "vcf", "snv.vcf.gz"),
    "expected_vcf": join(DATA, "vcf", "flagged.snv.vcf.gz"),
    "normal_bam": join(DATA, "bam", "normal.bam"),
    "tumor_bam": join(DATA, "bam", "tumor.bam"),
    "reference": join(DATA, "reference", "reference.fasta"),
    "indelBed": join(DATA, "indel.germline.bed"),
    "bedFileLoc": join(DATA, "flag_config"),
    "annoBedLoc": join(DATA, "annotable_region"),
    "unmatchedVCFLoc": join(DATA, "pon"),
}
