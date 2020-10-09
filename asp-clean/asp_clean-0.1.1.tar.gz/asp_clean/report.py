import random
from collections import defaultdict
from operator import itemgetter
from typing import Dict, List

from .compose import Composer
from .load import AspirateLoader
from .parse import Parser


class Container:
    def __init__(self):
        self.field_collector: Dict[str, list] = defaultdict(list)
        self.docs: List[dict] = []
        self.report_numbers: List[str] = []
        self.raw_report_texts: List[str] = []
        self._summary = None
        self.new_report_texts = None

    @property
    def doc_count(self):
        return len(self.docs)

    @property
    def field_summary(self):
        if self._summary is None:
            self._update_summary()
        return self._summary

    def get_doc(self, index):
        return self.docs[index]

    def get_raw_report_texts(self, index):
        return self.raw_report_texts[index]

    def get_new_report_texts(self, index):
        return self.new_report_texts[index]

    def _update_summary(self):
        summary = [(k, len(v)) for k, v in self.field_collector.items()]
        summary.sort(key=itemgetter(1), reverse=True)
        self._summary = summary

    def update_collection(self, supplier: AspirateLoader, parser: Parser):

        for aspirate in supplier.iter_aspirates():
            doc = parser.parse_aspirate_result(aspirate.result)
            self._handel_old_reports(doc, aspirate)
        self._form_new_report_texts()
        self._handel_id()
        parser.job_report()

    def _handel_old_reports(self, doc, aspirate):
        if len(doc) > 0:
            self.docs.append(doc)
            self.raw_report_texts.append(aspirate.result)
            self.report_numbers.append(aspirate.number)
            for k, v in doc.items():
                self.field_collector[k].append(v)

    def _form_new_report_texts(self):
        composer = Composer(connector=":")
        self.new_report_texts = [
            composer.compose_report(doc, shuffle=False) for doc in self.docs
        ]

    def _handel_id(self):
        report_number_len = len(self.report_numbers)
        report_number_unique_len = len(set(self.report_numbers))
        print(
            f"Reporter: {report_number_len} report numbers"
            f"{report_number_unique_len} unique report numbers."
            "If the report numbsers are not all unique,"
            "it suggest the number cannot be use as id"
        )
        self.ids = list(range(len(self.new_report_texts)))


class Reporter(object):
    def __init__(self, supplier: AspirateLoader, parser: Parser):
        self._supplier = supplier
        self._parser = parser
        self.collect_info()

    def collect_info(self):
        self.container = Container()
        self.container.update_collection(self._supplier, self._parser)
        print(f"Collect {self.doc_count} reports")

    @property
    def field_summary(self) -> list:
        return self.container.field_summary

    @property
    def doc_count(self) -> int:
        return self.container.doc_count

    @property
    def report_numbers(self) -> list:
        return self.container.report_numbers

    @property
    def ids(self) -> list:
        return self.container.ids

    @property
    def new_report_texts(self) -> list:
        return self.container.new_report_texts

    @property
    def docs(self):
        return self.container.docs

    def get_comparison(self):
        index = self._select_index()
        raw_report = self.container.get_raw_report_texts(index)
        new_report = self.container.get_new_report_texts(index)
        return f"{raw_report}\n =>\n {new_report}"

    def get_composition(
        self, composer: Composer, ratio=1.0, shuffle=True
    ) -> str:
        index = self._select_index()
        doc = self.container.get_doc(index)
        new_report = composer.compose_report(doc, shuffle=shuffle, ratio=ratio)
        return new_report

    def _select_index(self):
        select_idx = random.randint(0, self.doc_count - 1)
        return select_idx
