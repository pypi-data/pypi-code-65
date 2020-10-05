from .tags import Tag, Tags


class FooBar(Tag):
    FOO = 'foo'
    BAR = 'bar'


def test_tag():
    assert FooBar.name() == 'foobar'

def test_tags():
    tags = Tags([FooBar.FOO])
    assert tags.tags == {
        'foobar': 'foo'
    }
