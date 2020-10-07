import hashlib
import math
import struct

from typing import Optional, Sequence

from opentelemetry.sdk.trace.sampling import Sampler, Decision, SamplingResult
from opentelemetry.util.types import Attributes

MAX_INT32 = math.pow(2, 32) - 1

class DeterministicSampler(Sampler):
    def __init__(self, rate: int):
        if rate < 1:
            raise ValueError("SampleRate must be greater than zero")
        self.rate = rate
        self.upper_bound = MAX_INT32 / rate

    def get_description(self):
        return "HoneycombDeterministicSampler"

    def should_sample(
        self,
        parent_context: Optional["SpanContext"],
        trace_id: int,
        name: str,
        attributes: Attributes = None,
        links: Sequence["Link"] = (),
    ) -> "SamplingResult":
        sample_rate = {'SampleRate': self.rate}
        if attributes is None:
           attributes = sample_rate
        else:
            attributes.update(sample_rate)
        sha1 = hashlib.sha1()
        sha1.update(hex(trace_id).encode('utf-8'))
        value, = struct.unpack('>I', sha1.digest()[:4])
        if value >= self.upper_bound:
            return SamplingResult(Decision.DROP, attributes)
        return SamplingResult(Decision.RECORD_AND_SAMPLE, attributes)
