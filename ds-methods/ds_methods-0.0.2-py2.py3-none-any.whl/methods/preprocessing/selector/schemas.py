from schema import Schema, And, Optional


options_schema = Schema(
    And({
        Optional('include'): And([str], len),
        Optional('exclude'): And([str], len),
    }, lambda x: 'include' in x or 'exclude' in x),
    ignore_extra_keys=True,
)
