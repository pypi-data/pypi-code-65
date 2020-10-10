from enum import Enum, unique

CASE_TAG_FLAG = "__case_tag__"


class NewTag:
    def __init__(self, desc=""):
        self.desc = desc


@unique
class Tag(Enum):
    SMOKE = NewTag("冒烟")
    ALL = NewTag("完整")

    # 以下开始为扩展标签，自行调整
    V1_0_0 = NewTag("V1.0.0版本")
    V2_0_0 = NewTag("V2.0.0版本")


def tag(*tag_type):
    """指定测试用例的标签，可以作为测试用例分组使用，用例默认会有Tag.ALL标签，支持同时设定多个标签，如：
    @tag(Tag.V1_0_0, Tag.SMOKE)
    def test_func(self):
        pass

    :param tag_type:标签类型，在tag.py里边自定义
    :return:
    """

    def wrap(func):
        if not hasattr(func, CASE_TAG_FLAG):
            tags = {Tag.ALL}
            tags.update(tag_type)
            setattr(func, CASE_TAG_FLAG, tags)
        else:
            getattr(func, CASE_TAG_FLAG).update(tag_type)
        return func

    return wrap
