SCALAR_TYPES = (str, int, float, bool, type(None))

SAME = object()

one = {
    "a": 1,
    "b": 2,
    "c": {
        "d": "qwe",
        "e": "asd",
    },
    "f": [
        10,
        20,
    ],
    "x": 10,
}

two = {
    "a": 1,
    "b": 3,
    "c": {
        "e": "zxc",
        "g": "vbn",
    },
    "f": [
        20,
        30,
    ],
    "x": "str",
}


def compare_values(v1, v2):
    """
    scalars: string, number, boolean, null -> dict{old: v1, new: v2}
    collections:
        - object -> {added: {k: v}, modified: {k: {old: v1, new: v3}}, delete: {k: v}}
        - array

    :param v1:
    :param v2:
    :return: a tuple of (add, delete,
    """
    if type(v1) is not type(v2):
        return {"old": v1, "new": v2}
    if isinstance(v1, SCALAR_TYPES):
        return compare_scalars(v1, v2)
    if isinstance(v1, dict):
        return compare_objects(v1, v2)
    if isinstance(v1, list):
        return compare_lists(v1, v2)
    raise TypeError("v1 and v2 must be instances of valid JSON types")


def compare_scalars(v1, v2):
    """(v1, v2) -> {old: v1, new: v2}"""
    if v1 != v2:
        return {"old": v1, "new": v2}
    return SAME


def compare_objects(v1, v2):
    """(v1, v2) -> (added: {k: v}, modified: {k: {old: v_old, new: v_new}}, deleted: {k: v})"""
    v1_keys = set(v1.keys())
    v2_keys = set(v2.keys())
    v1_only_keys = v1_keys - v2_keys
    common_keys = v1_keys.intersection(v2_keys)
    v2_only_keys = v2_keys - v1_keys
    added = {
        k: v2[k]
        for k in v2_only_keys
    }
    deleted = {
        k: v1[k]
        for k in v1_only_keys
    }
    modified = {
        k: comp_res
        for k in common_keys
        if (comp_res := compare_values(v1[k], v2[k])) and comp_res is not SAME
    }
    if added or modified or deleted:
        return {"added": added, "deleted": deleted, "modified": modified}
    return SAME


l1 = "abcxy"    # ab c   xy
l2 = "abbdxxy"  # ab bdx xy


def compare_lists(v1, v2):
    """(v1, v2) -> (added: [v, ...], modified: [{old: v_old, new: v_new}, ])"""
    common_prefix = []
    for i in range(min(len(v1), len(v2))):
        comp_res = compare_values(v1[i], v2[i])
        if comp_res is SAME:
            common_prefix.append(v1[i])
        else:
            break
    if len(common_prefix) == len(v1) and len(v1) == len(v2):
        return SAME
    common_suffix = []
    for i in range(-1, -1 - min(len(v1), len(v2)), -1):
        comp_res = compare_values(v1[i], v2[i])
        if comp_res is SAME:
            common_suffix.append(v1[i])
        else:
            break
    common_suffix.reverse()
    v1_middle = v1[len(common_prefix):-len(common_suffix)]
    v2_middle = v2[len(common_prefix):-len(common_suffix)]
    return {
        "common_prefix": common_prefix,
        "common_suffix": common_suffix,
        "v1_middle": v1_middle,
        "v2_middle": v2_middle,
    }
