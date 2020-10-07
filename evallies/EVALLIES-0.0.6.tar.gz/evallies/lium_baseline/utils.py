import copy
import numpy
import sidekit

def add_show_in_id(im):
    """
    Work on StatServer 
    """
    im2 = copy.deepcopy(im)
    max_length = 0
    for mod, seg in zip(im.modelset, im.segset):
        if max_length < 1 + len(mod) + len(seg):
            max_length = 1 + len(mod) + len(seg)
            im2.modelset = im2.modelset.astype('<U{}'.format(max_length))

    for ii, c_id in enumerate(im.modelset):
        im2.modelset[ii] = im.segset[ii] + "$" + c_id

    return im2


def remove_show_from_id(im):
    """
    Work on StatServer
    :param im:
    :return:
    """
    im2 = copy.deepcopy(im)
    im2.modelset = im2.modelset.astype('U', copy=False)
    for idx, c_id in enumerate(im.modelset):
        im2.modelset[idx] = c_id.split('$')[1]
    return im2

def s4d_to_allies(s4d_segmentation):
    """
    Convert a s4d.Diar object into the proper ALLIES format for segmentation
    :param s4d_segmentation: is a s4d.Diar object
    """
    spk = []
    st = []
    en = []
    for segment in s4d_segmentation:
        spk.append(segment["cluster"])
        st.append(float(segment["start"]) / 100.)
        en.append(float(segment["stop"]) / 100.)
    hyp = Reference(spk, st, en)
    #hyp = {"speaker": spk, "start_time": st, "end_time": en}
    return hyp

def keep_recurring_speakers(iv_ss, rank_F, occ_number=2, filter_by_name=False):
    """
    """
    unique, counts = numpy.unique(iv_ss.modelset, return_counts=True)
    tot_sessions = 0
    kept_idx = []
    for model in range(unique.shape[0]):
        if counts[model] >= occ_number and (
            (
                not (unique[model]).startswith("speaker")
                and not (unique[model]).startswith("presentat")
                and not (unique[model]).startswith("sup+")
                and not (unique[model]).startswith("voix")
                and not (unique[model]).startswith("publicitaire")
                and not (unique[model]).startswith("locuteur")
                and not (unique[model]).startswith("inconnu")
                and not (unique[model]).startswith("traduct")
                and not ("#" in (unique[model]))
                and "_" in (unique[model])
                and filter_by_name
            )
            or (not filter_by_name)
        ):
            kept_idx = numpy.append(
                kept_idx, numpy.where(iv_ss.modelset == unique[model])
            )
            tot_sessions += counts[model]
    #
    flt_iv = sidekit.StatServer()
    flt_iv.stat0 = numpy.ones((tot_sessions, 1))
    flt_iv.stat1 = numpy.ones((tot_sessions, rank_F))
    flt_iv.modelset = numpy.empty(tot_sessions, dtype="|O")
    flt_iv.segset = numpy.empty(tot_sessions, dtype="|O")
    flt_iv.start = numpy.empty(tot_sessions, dtype="|O")
    flt_iv.stop = numpy.empty(tot_sessions, dtype="|O")
    #
    i = 0
    for model in range(unique.shape[0]):
        if counts[model] >= occ_number and (
            (
                not (unique[model]).startswith("speaker")
                and not (unique[model]).startswith("presentat")
                and not (unique[model]).startswith("sup+")
                and not (unique[model]).startswith("voix")
                and not (unique[model]).startswith("publicitaire")
                and not (unique[model]).startswith("locuteur")
                and not (unique[model]).startswith("inconnu")
                and not (unique[model]).startswith("traduct")
                and not ("#" in (unique[model]))
                and "_" in (unique[model])
                and filter_by_name
            )
            or (not filter_by_name)
        ):
            for ivector in numpy.where(iv_ss.modelset == unique[model])[0]:
                flt_iv.stat1[i, :] = iv_ss.stat1[ivector, :]
                flt_iv.modelset[i] = iv_ss.modelset[ivector]
                flt_iv.segset[i] = iv_ss.segset[ivector]
                flt_iv.start[i] = iv_ss.start[ivector]
                flt_iv.stop[i] = iv_ss.stop[ivector]
                i += 1
    unique = numpy.unique(flt_iv.modelset)
    return flt_iv, unique.shape[0], kept_idx


