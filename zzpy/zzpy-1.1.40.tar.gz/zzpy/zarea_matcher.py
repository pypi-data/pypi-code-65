def __match(pattern, value):
    import re
    return any(re.match(p, value) for p in pattern.split(","))


def match_area(matchers, area_a, area_b):
    return any(m(area_a, area_b) for m in matchers)


def load_matcher(config):
    def _f(area_a, area_b):
        assert len(area_a) == 3
        assert len(area_b) == 3
        patterns_std = config["pattern_a"].split("|")
        assert len(patterns_std) == 3
        patterns_3rd = config["pattern_b"].split("|")
        assert len(patterns_3rd) == 3
        args = {"province": area_a[0],
                "city": area_a[1], "district": area_a[2]}
        return all(__match(pattern, area) for pattern, area in zip(patterns_std, area_a)) and all(__match(pattern.format(**args), area) for pattern, area in zip(patterns_3rd, area_b))
    return _f


def load_matchers(path):
    import zzpy as z
    return [load_matcher(config) for config in z.read_jsonline(path)]


def main():
    matcher = load_matcher(
        {"pattern_a": "重庆市|.*|.*", "pattern_b": "重庆市|.*|.*"})
    print(matcher(("重庆市", "asdf", "123"), ("重庆市", "xxx", "qqq")))
    
    matcher = load_matcher(
        {"pattern_a": ".*|.*|.*", "pattern_b": "{province}|{city}|.*"})
    print(matcher(("重庆市", "asdf", "123"), ("重庆市", "xxx", "qqq")))
    print(matcher(("重庆市", "asdf", "123"), ("重庆市", "asdf", "qqq")))


if __name__ == "__main__":
    main()
