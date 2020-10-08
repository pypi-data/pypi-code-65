#!/usr/bin/env python3

"""\
html parser for sample forms and project initiation forms
"""

import re
import sys

import pandas as pd
import regex
from bs4 import BeautifulSoup
from dateutil.parser import parse
from lxml.html.clean import Cleaner


class ParseHtml:
    """\
    HTML parser that returns clean parameters and data extracted from *iLabs*
    submitted forms.

    :type html: str
    :type kill_tags: list

    :param html:
        Input HTML
    :param kill_tags:
        HTML tags to be cleaned and removed

    :rtype: str
    :return:
        Cleaned html string

    Example
    -------

    >>> from SCRIdb.htmlparser import cleanhtml
    >>> cleanhtml("<p>Some<b>bad<i>HTML")

    """

    def __init__(self, func):
        self.func = func
        self.kargs = {}
        # self.tables = {}
        self.soup = str
        # self.id = 1

    def __call__(self, *args):

        new_html = self.func(*args)
        self.soup = BeautifulSoup(new_html, "html.parser")

    def reset(self):
        self.__init__(self.func)

    def get_general_attrs(self, **labels) -> None:

        self.soup.a.decompose()
        request_id = self.soup.h2.string.strip().split()[0]
        date_created = self.soup.find(text=regex.compile("Created")).strip()
        date_created = re.search(r"(?<=Created: ).*", date_created).group()
        date_created = parse(date_created).strftime("%Y-%m-%d")
        if self.soup.find("td", string="Lab Name:"):
            self.kargs["labName"] = self.soup.a.text
        if self.soup.find("td", string="Customer institute:"):
            self.kargs["institute"] = (
                self.soup.find("td", string="Customer institute:",)
                .findNextSibling()
                .get_text()
            )
            labinfo = (
                self.soup.find("td", string="Lab PI(s):").findNextSibling().get_text()
            ).strip()
            self.kargs["PI_name"] = re.match(r"\A.+?(?=:)", labinfo).group()
            self.kargs["PI_email"] = re.search(
                r"[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+", labinfo
            ).group()
            phone = (
                re.search(r"(?<=Phone: ).*", labinfo).group()
                if re.search(r"(?<=Phone: ).*", labinfo)
                else ""
            )
            self.kargs["Phone"] = phone if phone else "NULL"
        self.kargs["request_id"] = request_id
        self.kargs["date_created"] = date_created

        stype = ""
        for tag in self.soup.find_all("label"):
            if tag.text.strip() in labels:
                if tag.text.strip() == "Sample type":
                    stype = tag.findNext().text.strip()
                elif tag.text.strip() in [
                    "Notes or comments",
                    "Staff notes or comments",
                    "Brief summary of project goals",
                    "Experimental design",
                ] and tag.findNext().text.strip() in [
                    "Notes or comments",
                    "Staff notes or comments",
                    "Brief summary of project goals",
                    "Experimental design",
                    "",
                ]:
                    self.kargs[labels[tag.text.strip()]] = "NULL"
                else:
                    self.kargs[labels[tag.text.strip()]] = tag.findNext().text.strip()
            if tag.text.strip() == "Specify new sample type":
                stype = tag.findNext().text.strip()

        self.kargs["Sample type"] = stype

        # get rid of none checked radio buttons and checkboxes
        for i in self.soup.find_all("input", attrs={"checked": False}):
            try:
                i.parent.decompose()
            except AttributeError:
                pass

        try:
            tag = self.soup.find_all("font", text="Choose 10X Kit")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Problems":
                        self.kargs["Choose 10X Kit"] = tag.text.strip()
                tag = tag.findNext()
        except IndexError:
            pass

        try:
            tag = self.soup.find_all("font", text="Choose Kit")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Problems":
                        if "Choose Kit" in self.kargs:
                            self.kargs["Choose Kit"].append(tag.text.strip())
                        else:
                            self.kargs["Choose Kit"] = [tag.text.strip()]
                tag = tag.findNext()
            self.kargs["Choose Kit"] = " ".join(self.kargs["Choose Kit"])
        except (KeyError, IndexError):
            pass

        try:
            tag = self.soup.find_all("font", text="Choose InDrop Version")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Problems":
                        self.kargs["Choose InDrop Version"] = tag.text.strip()
                tag = tag.findNext()
        except IndexError:
            pass

        try:
            tag = self.soup.find_all("font", text="Problems")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Staff notes or comments":
                        if "Problems" in self.kargs:
                            self.kargs["Problems"].append(tag.text.strip())
                        else:
                            self.kargs["Problems"] = [tag.text.strip()]
                tag = tag.findNext()
            self.kargs["Problems"] = "; ".join(self.kargs["Problems"])
        except (KeyError, IndexError):
            pass

        try:
            tag = self.soup.find_all("font", text="Other notes or comments:")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Staff notes":
                        self.kargs["Other notes or comments:"] = tag.text.strip()
                tag = tag.findNext()
        except IndexError:
            pass

        try:
            tag = self.soup.find_all("font", text="Staff notes")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Project label":
                        self.kargs["Staff notes"] = tag.text.strip()
                tag = tag.findNext()
        except IndexError:
            pass

        try:
            tag = self.soup.find_all("font", text="Project label")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    self.kargs["Project label"] = tag.text.strip()
                tag = tag.findNext()
        except (AttributeError, IndexError):
            pass

        return None

    def get_tables(self, index: str = "Sample Name") -> None:

        # collect samples
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Upload samples from Excel?":
                samples_table = pd.read_html(repr(tag.find_next("table")), index_col=0)[
                    0
                ]
                samples_table = samples_table.dropna(how="all")
                # Important: get rid of spaces in sample name, since sample name is
                # used to construct prefix for seqc outputs
                samples_table[index] = samples_table[index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                samples_table = samples_table.set_index(index)
                # establish indexed sample names to test for discrepancies
                idx = samples_table.index

                try:
                    assert (
                        not idx.empty
                    ), "Missing sample data! Check the form for Sample data integrity."
                except AssertionError as e:
                    print(str(e))
                    sys.exit("ERROR:\n" + str(e))

                self.kargs["samples"] = samples_table.to_dict(orient="index")

        # collect library prep parameters
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Sample parameters":
                sample_parameters = pd.read_html(
                    repr(tag.find_next("table")), index_col=0
                )[0]
                sample_parameters = sample_parameters.dropna(how="all")
                # get rid of spaces in sample name
                sample_parameters[index] = sample_parameters[index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                sample_parameters = sample_parameters.set_index(index)
                if sample_parameters.empty:
                    pass
                else:
                    try:
                        assert not bool(
                            sample_parameters.index.difference(idx).values.any()
                        ), (
                            "sample names don't match in sample_parameters table "
                            "compared to samples table"
                        )
                    except (KeyError, AssertionError) as e:
                        print("ERROR: index = ", index)
                        print(
                            pd.DataFrame(
                                {
                                    "sample_parameters": pd.Series(
                                        sample_parameters.index
                                    ),
                                    "sample_names": pd.Series(idx),
                                }
                            )
                        )
                        print(str(e))
                        sys.exit("ERROR:\n" + str(e))
                    t = sample_parameters.to_dict(orient="index")
                    for sample in t.keys():
                        self.kargs["samples"][sample].update(t[sample])

        # collect hashtags if any
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Hash tag barcodes used":
                converters = {
                    "Hash tag barcode (4 digit)": str,
                    "Hash Tag Sequence": str,
                    "Barcode": str,
                    "Label": str,
                }
                hashtags_table = pd.read_html(
                    str(tag.find_next("table")), index_col=0, converters=converters
                )[0]
                columns = [
                    "Label",
                    "Hash Tag Sequence",
                    "Barcode",
                    "Sample Name (Optional)",
                    "Notes",
                ]
                hashtags_table = hashtags_table[columns]
                hashtags_table = hashtags_table.dropna(how="all")

                try:
                    assert not hashtags_table.empty, (
                        "Missing hashtags data! Check the form for hashtag data "
                        "integrity."
                    )
                except AssertionError as e:
                    print(str(e))
                    sys.exit("ERROR:\n" + str(e))

                # attach hashtags to samples
                if hashtags_table["Sample Name (Optional)"].dropna().empty:
                    hashtags_table = hashtags_table.T.iloc[[0, 1, 2, 4]]
                    hashtags_table.index = [
                        "hlabels",
                        "hashtags",
                        "barcodes",
                        "hashtag_notes",
                    ]
                    hashtags_table = hashtags_table.to_dict(orient="index")
                    for sample in self.kargs["samples"]:
                        self.kargs["samples"][sample][
                            "hastag_parameters"
                        ] = hashtags_table
                else:
                    hashtags_table.columns = [
                        "hlabels",
                        "hashtags",
                        "barcodes",
                        "sample_name",
                        "hashtag_notes",
                    ]
                    hashtags_table["sample_name"] = hashtags_table[
                        "sample_name"
                    ].replace(to_replace=r" ", value="_", regex=True)
                    t1 = hashtags_table.to_dict()

                    for sample in self.kargs["samples"]:
                        hashtags = {
                            "hashtags": {
                                i: t1["hashtags"][i]
                                for i in [
                                    k
                                    for k, v in t1["sample_name"].items()
                                    if v == sample
                                ]
                            }
                        }
                        barcodes = {
                            "barcodes": {
                                i: t1["barcodes"][i]
                                for i in [
                                    k
                                    for k, v in t1["sample_name"].items()
                                    if v == sample
                                ]
                            }
                        }
                        hlabels = {
                            "hlabels": {
                                i: t1["hlabels"][i]
                                for i in [
                                    k
                                    for k, v in t1["sample_name"].items()
                                    if v == sample
                                ]
                            }
                        }
                        hashtag_notes = {
                            "hashtag_notes": {
                                i: t1["hashtag_notes"][i]
                                for i in [
                                    k
                                    for k, v in t1["sample_name"].items()
                                    if v == sample
                                ]
                            }
                        }

                        hastag_parameters = {}
                        [
                            hastag_parameters.update(i)
                            for i in [hashtags, barcodes, hlabels, hashtag_notes]
                        ]
                        self.kargs["samples"][sample][
                            "hastag_parameters"
                        ] = hastag_parameters

        # collect hashtags prep parameters
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Hashtag parameters":
                hashtag_parameters = pd.read_html(
                    repr(tag.find_next("table")), index_col=0
                )[0]
                hashtag_parameters = hashtag_parameters.dropna(how="all")
                # get rid of spaces in sample name
                hashtag_parameters[index] = hashtag_parameters[index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                hashtag_parameters = hashtag_parameters.set_index(index)
                if hashtag_parameters.empty:
                    pass
                else:
                    try:
                        assert not bool(
                            hashtag_parameters.index.difference(idx).values.any()
                        ), (
                            "sample names don't match in hashtag parameters "
                            "table compared to samples table"
                        )
                    except (KeyError, AssertionError) as e:
                        print("ERROR: index = ", index)
                        print(
                            pd.DataFrame(
                                {
                                    "hashtag_parameters": pd.Series(
                                        hashtag_parameters.index
                                    ),
                                    "sample_names": pd.Series(idx),
                                }
                            )
                        )
                        print(str(e))
                        sys.exit("ERROR:\n" + str(e))
                    t = hashtag_parameters.to_dict(orient="index")
                    for k, v in t.items():
                        self.kargs["samples"][k]["hastag_parameters"].update(v)

        # collect TCR prep parameters
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "TCR parameters":
                tcr_parameters = pd.read_html(
                    repr(tag.find_next("table")), index_col=0
                )[0]
                tcr_parameters = tcr_parameters.dropna(how="all")
                # get rid of spaces in sample name
                tcr_parameters[index] = tcr_parameters[index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                tcr_parameters = tcr_parameters.set_index(index)
                if tcr_parameters.empty:
                    pass
                else:
                    try:
                        assert not bool(
                            tcr_parameters.index.difference(idx).values.any()
                        ), (
                            "sample names don't match in hashtag parameters "
                            "table compared to samples table"
                        )
                    except (KeyError, AssertionError) as e:
                        print("ERROR: index = ", index)
                        print(
                            pd.DataFrame(
                                {
                                    "tcr_parameters": pd.Series(tcr_parameters.index),
                                    "sample_names": pd.Series(idx),
                                }
                            )
                        )
                        print(str(e))
                        sys.exit("ERROR:\n" + str(e))
                    t = tcr_parameters.to_dict(orient="index")
                    for k, v in t.items():
                        self.kargs["samples"][k]["TCR_parameters"] = v

        return None


@ParseHtml
def cleanhtml(html: str = "", kill_tags: list = ["span"]) -> str:
    """\
    HTML parser that returns clean parameters and data extracted from *iLabs*
    submitted forms.

    :param html:
        Input HTML
    :param kill_tags:
        HTML tags to be cleaned and removed

    :return:
        Cleaned html string

    """
    cleaner = Cleaner(
        style=True,
        links=True,
        add_nofollow=True,
        javascript=True,
        meta=True,
        page_structure=True,
        kill_tags=kill_tags,
        processing_instructions=True,
        embedded=True,
        frames=True,
        forms=False,
    )
    new_html = cleaner.clean_html(html)

    return new_html
