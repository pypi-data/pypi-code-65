#!/usr/bin/env python
# -*- coding:utf-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Authors:
# - Brian Bockelman, <bbockelm@cse.unl.edu>, 2017-2018
# - James Alexander Clark, <james.clark@ligo.org>, 2018-2019
"""
igwn_lfn2pfn.py

LFN-to-PFN algorithms for IGWN
"""
from __future__ import print_function
import os
import re
import traceback
from rucio.client.client import Client
from rucio.rse.protocols.protocol import RSEDeterministicTranslation
from rucio.common.exception import DataIdentifierNotFound
import rucio.rse.rsemanager as rsemgr

# ?: is a non-capturing group because we don't use the duration of frames
_LEGACY_GWF_RE = re.compile(
    r'([A-Z]+)-([A-Za-z0-9_]+)-([0-9]{5,5})(?:[0-9]+)-([0-9]+).([A-Za-z]+)')

_IGWN_GWF_RE = re.compile(
    r'([A-Z]+)-([A-Za-z0-9_]+)-([0-9]{3,3})(?:[0-9]+)-([0-9]+).([A-Za-z]+)')

_LV_CONTENT_RE = re.compile(r'([A-Z0-9]+)_([A-Za-z0-9_]+)')

_K_CONTENT_RE = re.compile(r'([A-Z0-9]+)_([A-Z0-9]+)')

_LEGACY_SFT_RE = re.compile(
    r'([A-Z]+)-(?:[A-Za-z0-9_]+)-([0-9]+)-([0-9]+).(?:[A-Za-z]+)')

_TESTS_RE = re.compile(r'^[A-Z]+\.[a-z0-9]+$')


def igwn(scope, name, rse=None, rse_attrs=None, proto_attrs=None):
    """
    This function maps the scope:LFN to the PFN for the newer GWF & SFT schemas

    Parameters:

    :param scope: Scope of the LFN.
    :param name: File name of the LFN.
    :param rse: RSE for PFN (ignored)
    :param rse_attrs: RSE attributes for PFN (ignored)
    :param protocol_attrs: RSE protocol attributes for PFN (ignored)
    :returns: Path for use in the PFN generation.
    """
    # Prevents unused argument warnings in pylint
    del rse
    del rse_attrs
    del proto_attrs

    # Exception for automatix test data. E.g.,
    # test.61f182e47315405ebc029599672199f2
    match = _TESTS_RE.match(name)
    if match:
        return "%s/%s" % (scope, name)

    # Match IGWN schema
    match = _IGWN_GWF_RE.match(name)
    if not match:
        raise ValueError("Invalid IGWN filename")
    detector, dataset, gps_prefix, _, extension = match.groups()

    if extension not in ['gwf', 'sft']:
        raise NotImplementedError("Extension %s not recognised" % extension)

    dir_hash = "%s-%s-%s" % (detector, dataset, gps_prefix)

    pfn = "%s/%s/%s/%s" % (scope, dataset, dir_hash, name)

    return pfn


RSEDeterministicTranslation.register(igwn)


def kagra_offline(scope, name, rse=None, rse_attrs=None, proto_attrs=None):
    """
    Map the GWF files according to the KAGRA aggregated offline schema.

    Low-latency frames at ICRR are aggregated into 4096 frame files and
    placed in a directory named for the detector:

    O3:K-K1_C10-1268645888-4096.gwf ->
    <prefix>/C10/O3/K1/K-K1_C10-1268645888-4096.gwf

    This function maps the scope:LFN to the PFN.

    Parameters:

    :param scope: Scope of the LFN.
    :param name: File name of the LFN.
    :param rse: RSE for PFN (ignored)
    :param rse_attrs: RSE attributes for PFN (ignored)
    :param protocol_attrs: RSE protocol attributes for PFN (ignored)
    :returns: Path for use in the PFN generation.
    """
    # Prevents unused argument warnings in pylint
    del rse
    del rse_attrs
    del proto_attrs

    # Exception for automatix test data. E.g.,
    # test.61f182e47315405ebc029599672199f2
    match = _TESTS_RE.match(name)
    if match:
        return "%s/%s" % (scope, name)

    # Parse LFN
    match = _LEGACY_GWF_RE.match(name)
    if not match:
        raise ValueError("Invalid LIGO filename")
    detector, dataset, _, _, _ = match.groups()

    detector = detector[0] + '1'

    # Parse frame type
    match = _K_CONTENT_RE.match(dataset)
    _, calib = match.groups()

    pfn = "%s/%s/%s/%s" % (calib, scope, detector, name)

    return pfn


RSEDeterministicTranslation.register(kagra_offline)


def ligo_legacy(scope, name, rse=None, rse_attrs=None, proto_attrs=None):
    """
    Return the PFN for LFN <name>, based on historical file placement at
    Caltech.  Accepts .gwf and .sft file extensions.
    """
    name = os.path.basename(name)

    # Prevents unused argument warnings in pylint
    del rse
    del rse_attrs
    del proto_attrs

    # Exception for automatix test data. E.g.,
    # test.61f182e47315405ebc029599672199f2
    match = _TESTS_RE.match(name)
    if match:
        return "%s/%s" % (scope, name)

    if name.endswith('.gwf'):
        pfn = ligo_legacy_frames(scope, name)
    elif "sft" in name:
        try:
            pfn = ligo_legacy_sfts_from_metadata(scope, name)
        except DataIdentifierNotFound:
            pfn = ligo_legacy_sfts_from_replicas(scope, name)
    else:
        raise NotImplementedError("Extension not recognised for %s" % name)

    return pfn


RSEDeterministicTranslation.register(ligo_legacy)


def ligo_legacy_sfts_from_metadata(scope, name):
    """
    Map SFT files to e.g.,:

    O2:H-H1_TUKEYWIN_C00-1164562334-1800.sft ->
    O2/pulsar/sfts/tukeywin/LHO_C00/H-1_H1_1800SFT_O2-1164/H-1_H1_1800SFT_O2-1164562334-1800.sft

    SFT files must be pre-registered at a non-deterministic RSE LIGO-CIT-SFTS

    Will try to construct path based on metadata for supported datasets.  Falls
    back to using the replica paths at LIGO-CIT-SFTS on failure.

    """

    print("Getting SFT paths jrom metadata")
    match = _LEGACY_SFT_RE.match(name)
    if not match:
        raise ValueError("Invalid LIGO filename")
    detector, gps_start, duration = match.groups()

    # Get metadata
    client = Client()
    did_meta = client.get_metadata(scope=scope, name=name, plugin='JSON')
    try:
        window = did_meta['window'].lower()
        calibration = did_meta['calibration']
    except KeyError:
        print(traceback.format_exc())
        print("DID %s:%s has insufficient metadata" % (scope, name))
        raise DataIdentifierNotFound

    if scope == 'O2' and window == 'tukeywin':

        if detector in ['H', 'L']:
            ifo_cal = "L%sO_%s" % (detector, calibration)
        else:
            raise DataIdentifierNotFound

        gps_prefix = gps_start[:4]
        dir_hash = "%s-1_%s1_%sSFT_%s-%s" % (detector, detector, duration,
                                             scope, gps_prefix)

        sft_name = "%s-1_%s1_%sSFT_%s-%s-%s.sft" % (detector, detector,
                                                    duration, scope, gps_start,
                                                    duration)

        pfn = "%s/pulsar/sfts/%s/%s/%s/%s" % (scope, window, ifo_cal, dir_hash,
                                              sft_name)
    else:
        raise DataIdentifierNotFound

    return pfn


def ligo_legacy_sfts_from_replicas(scope, name):
    """
    Map SFT files to e.g.,:

    O2:H-H1_TUKEYWIN_C00-1164562334-1800.sft ->
    O2/pulsar/sfts/tukeywin/LHO_C00/H-1_H1_1800SFT_O2-1164/H-1_H1_1800SFT_O2-1164562334-1800.sft

    SFT files must be pre-registered at a non-deterministic RSE LIGO-CIT-SFTS
    """
    # Using paths from the non-deterministic RSE at CIT
    print("Getting SFT paths from existing replicas")
    client = Client()
    replicas = next(client.list_replicas(dids=[{'scope': scope, 'name': name}],
                                         rse_expression="LIGO-CIT-SFTS"))
    rse_info = rsemgr.get_rse_info("LIGO-CIT-SFTS")

    protocol = rse_info['protocols'][0]
    schema = protocol['scheme']
    prefix = protocol['prefix']
    port = protocol['port']
    rucioserver = protocol['hostname']

    # Determine URI prefix from RSE configuration
    if schema == 'srm':
        prefix = protocol['extended_attributes']['web_service_path'] + prefix
    url = schema + '://' + rucioserver + ':' + str(port) + prefix

    archive_pfn = ''.join(replicas['pfns'].keys())

    # Strip out the protocol and prefix to get the universal path
    pfn = archive_pfn.replace(url+'/', '')

    return pfn


def ligo_legacy_frames(scope, name):
    """
    Map the GWF files according to the Caltech schema.

    ER8:H-H1_HOFT_C02-1126256640-4096 ->
    ER8/hoft_C02/H1/H-H1_HOFT_C02-11262/H-H1_HOFT_C02-1126256640-4096
    """
    # pylint: disable=too-many-branches

    match = _LEGACY_GWF_RE.match(name)
    if not match:
        raise ValueError("Invalid LIGO filename")
    detector, dataset, gps_prefix, _, _ = match.groups()
    dir_hash = "%s-%s-%s" % (detector, dataset, gps_prefix)

    # Virgo

    # In O1: all Virgo data went to /archive/frames/AdVirgo

    # In O2:
    #       - V1Online went to /archive/frames/AdVirgo
    #       - raw V1O2Repro1A and V1O2Repro2A lived in /archive/frames/O2

    # In O3: raw, V1Online live in /archive/frames/O3

    if dataset == 'V1Online' and scope != 'O3':
        detector = 'AdVirgo'
        dataset = 'HrecOnline'
        pfn = '%s/%s/%s/%s' % (detector, dataset, dir_hash, name)

    elif detector == 'V' and dataset == 'raw' and scope in ['O2', 'O3']:
        detector = detector[0] + '1'
        pfn = "%s/%s/%s/%s/%s" % (scope, dataset, detector, dir_hash, name)

    elif dataset == 'V1Online' and scope == 'O3':
        pfn = "%s/%s/%s/%s" % (scope, dataset, dir_hash, name)

    elif detector == 'V' and dataset == 'raw':
        detector = 'AdVirgo'
        pfn = "%s/%s/%s/%s" % (detector, dataset, dir_hash, name)

    elif dataset in ['V1O2Repro1A', 'V1O2Repro2A', 'V1O3Repro1A']:
        pfn = '%s/%s/%s/%s' % (scope, dataset, dir_hash, name)

    # KAGRA
    elif dataset in ['K1_C10', 'K1_C00']:
        pfn = "%s/%s/%s/%s/%s" % (scope, detector, dataset, dir_hash, name)

    # GEO
    elif detector == 'G':

        # GEO
        # G-G1_RDS_C01_L3-1269615000-60.gwf ->
        # <prefix>/A6/L3/GEO/G-G1_RDS_C01_L3-12696/G-G1_RDS_C01_L3-1269615000-60.gwf
        detector = "GEO"

        if dataset == 'G1_RDS_C01_L3':
            pfn = "A6/L3/%s/%s/%s" % (detector, dir_hash, name)

    else:
        # LIGO

        match = _LV_CONTENT_RE.match(dataset)
        detector, dataset = match.groups()

        if dataset == 'R' and scope == 'postO3':
            dataset = 'raw_other'

        elif dataset == 'R' and scope != 'postO3':
            dataset = 'raw'

        elif dataset == 'RDS':
            dataset = 'rds'

        elif dataset == 'HOFT_C00':
            dataset = 'hoft'

        elif dataset in ['HOFT_C01', 'HOFT_C02', 'HOFT_X04']:
            dataset = dataset.replace('HOFT', 'hoft')

        elif dataset == 'HOFT_C01_4kHz':
            dataset = 'hoft_C01_4kHz'

        elif dataset == 'CLEANED_HOFT_C02':
            dataset = 'hoft_C02_clean'

        elif dataset == 'HOFT_CLEAN_SUB60HZ_C01':
            dataset = 'hoft_C01_clean_sub60Hz'

        pfn = "%s/%s/%s/%s/%s" % (scope, dataset, detector, dir_hash, name)

    return pfn
