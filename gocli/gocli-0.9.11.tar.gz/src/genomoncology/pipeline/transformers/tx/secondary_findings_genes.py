from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "gene": "gene",
    "disease_name__mstring": "disease_name",
    "disease_mim__mstring": "disease_mim",
}


def parse_gene(x):
    return x["key"]


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.SECONDARY_FINDINGS_GENES,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.SECONDARY_FINDINGS_GENES.value),
        name_mapping(NAME_MAPPING),
        lambda x: assoc(x, "gene", parse_gene(x)),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.SECONDARY_FINDINGS_GENES,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.SECONDARY_FINDINGS_GENES.value),
    ),
    is_header=True,
)
