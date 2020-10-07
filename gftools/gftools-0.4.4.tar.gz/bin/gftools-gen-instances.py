"""
gftools gen-instances
"""
import argparse
import sys
from gftools.axes_pb2 import AxisProto
from google.protobuf import text_format
from glob import glob
import shutil
import os
import re
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib import TTFont
from copy import copy


# TODO move axis_registry and read_proto to seperate module
def axis_registry(path):
    proto_dir = os.path.join(path, "*.textproto")
    protos = [read_proto(f) for f in glob(proto_dir)]
    protos = {p.tag: p for p in protos}
    # temp fix weight names https://github.com/google/fonts/issues/2701
    for i in protos["wght"].fallback:
        i.name = i.name.replace(" ", "")
    return protos


def read_proto(f):
    """Parse an Axis .textproto file"""
    result = AxisProto()
    with open(f, "rb") as doc:
        text_format.Parse(doc.read(), result)
    return result


def update_nametable(ttfont, family_name, style_name):
    nametbl = ttfont["name"]
    is_ribbi = style_name in ["Regular", "Italic", "Bold", "Bold Italic"]
    # remove mac os name (they're not needed)
    nametbl.removeNames(platformID=1)
    # update familyname
    if is_ribbi:
        nametbl.setName(family_name, 1, 3, 1, 1033)
    else:
        nametbl.setName(family_name, 16, 3, 1, 1033)
        non_ribbi_family_name = f"{family_name} {style_name.replace(' Italic', '')}"
        nametbl.setName(non_ribbi_family_name, 1, 3, 1, 1033)

    # update stylename
    if is_ribbi:
        nametbl.setName(style_name, 2, 3, 1, 1033)
    else:
        nametbl.setName(style_name, 17, 3, 1, 1033)
        non_ribbi_style_name = "Regular" if "Italic" not in style_name else "Italic"
        nametbl.setName(non_ribbi_style_name, 2, 3, 1, 1033)

    # full name
    full_name = f"{family_name} {style_name}"
    nametbl.setName(full_name, 4, 3, 1, 1033)

    # ps name
    ps_name = f"{family_name.replace(' ', '')}-{style_name.replace(' ', '')}"
    nametbl.setName(ps_name, 6, 3, 1, 1033)

    # unique name
    vendor_id = ttfont["OS/2"].achVendID.strip()
    version_rec = nametbl.getName(5, 3, 1, 1033)
    if version_rec:
        version_num = re.search(
            r"[0-9]{1,4}.[0-9]{1,9}", version_rec.toUnicode()
        ).group(0)
    else:
        version_num = f"{ttfont['head'].majorVersion}.{ttfont['head'].minorVersion}"
    unique_id = f"{version_num};{vendor_id};{ps_name}"
    nametbl.setName(unique_id, 3, 3, 1, 1033)


def get_instance_coords(ttfont, axis_registry):
    axes = {
        a.axisTag: {"min": a.minValue, "max": a.maxValue} for a in ttfont["fvar"].axes
    }
    return _coordinator(axes, axis_registry)


def _coordinator(axes, axis_registry, s=0, p={}, res=[]):
    """Use backtracking to assemble all coordinate permutations"""
    if s == len(axes):
        res.append(copy(p))
        return
    axes_keys = list(axes.keys())
    axis = axes_keys[s]
    for fallback in axis_registry[axis].fallback:
        if fallback.value >= axes[axis]["min"] and fallback.value <= axes[axis]["max"]:
            p[axis] = fallback.value
            _coordinator(axes, axis_registry, s + 1, p, res)
            del p[axis]
    return res


def names_from_coords(coords, axis_registry, v1_api=False):
    family_name_particles = []
    style_particles = []
    # TODO don't use sorted order. Establish and order
    # https://github.com/google/fonts/issues/2702
    for axis_name, axis_val in sorted(coords.items()):
        axis_in_reg = axis_registry[axis_name]
        axis_fallbacks = {a.value: a.name for a in axis_in_reg.fallback}
        # Do not include default axis particles in name, unless it is the
        # Weight axis since we always want Regular to be present
        if axis_name != "wght" and axis_val == axis_in_reg.default_value:
            continue
        if not v1_api:
            style_particles.append(axis_fallbacks[axis_val])
        else:
            if axis_name in ["ital", "wght"]:
                style_particles.append(axis_fallbacks[axis_val])
            else:
                family_name_particles.append(axis_fallbacks[axis_val])
    return (" ".join(family_name_particles), " ".join(style_particles))


def update_fs_selection(ttfont, stylename):
    fs_selection = ttfont["OS/2"].fsSelection

    # turn off all bits except for bit 7 (USE_TYPO_METRICS)
    fs_selection &= 0b10000000

    if "Italic" in stylename:
        fs_selection |= 0b1
    if stylename in ["Bold", "Bold Italic"]:
        fs_selection |= 0b100000
    # enable Regular bit for all other styles
    if stylename not in ["Bold", "Bold Italic"] and "Italic" not in stylename:
        fs_selection |= 0b1000000
    ttfont["OS/2"].fsSelection = fs_selection


def update_mac_style(ttfont, stylename):
    mac_style = 0b0
    if "Italic" in stylename:
        mac_style |= 0b10
    if stylename in ["Bold", "Bold Italic"]:
        mac_style |= 0b1
    ttfont["head"].macStyle = mac_style


def gen_instances(varfont, axis_registry, dst, instance_coords=None, overlap=False):
    """Instantiate a variable font using the GF axisregistry"""
    name = varfont['name']
    # A variable font family often contains two fonts, one for Roman, the
    # other for Italic. If the varfont is an italic font, we will update
    # the stylename to reflect this
    is_italic = True if "Italic" in name.getName(2, 3, 1, 1033).toUnicode() else False

    # if a user hasn't specified any instance_coords, we will construct the instances
    # using the fallback names and values from the Google Fonts axis registry
    if not instance_coords:
        instance_coords = get_instance_coords(varfont, axis_registry)

    for coords in instance_coords:
        static_font = instantiateVariableFont(varfont, coords, overlap=overlap)
        family_suffix, style_name = names_from_coords(
            coords, axis_registry, v1_api=True
        )
        family_name = static_font["name"].getName(16, 3, 1, 1033) or \
                static_font["name"].getName(1, 3, 1, 1033)
        family_name = (
            f"{family_name.toUnicode()} {family_suffix}"
            if family_suffix
            else family_name.toUnicode()
        )
        style_name = f"{style_name} Italic".replace("Regular Italic", "Italic") if is_italic else style_name
        update_nametable(static_font, family_name, style_name)
        update_fs_selection(static_font, style_name)
        update_mac_style(static_font, style_name)

        filename = f"{family_name}-{style_name}.ttf".replace(" ", "")
        out = os.path.join(dst, filename)
        static_font.save(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("varfont", help="A variable font")
    parser.add_argument("--axis-registry", help="Path to axis registry")
    parser.add_argument(
        "--remove-overlaps",
        action="store_true",
        default=False,
        help="Remove overlaps in static fonts",
    )
    parser.add_argument("--coordinates", help="User specified list of coordinates")
    parser.add_argument("-o", "--out", default="static", help="output dir")
    args = parser.parse_args()

    varfont = TTFont(args.varfont)
    axis_reg = axis_registry("/Users/marcfoley/Type/fonts/axisregistry")
    if not os.path.isdir(args.out):
        os.mkdir(args.out)
    gen_instances(varfont, axis_reg, args.out, args.remove_overlaps)


if __name__ == "__main__":
    main()

