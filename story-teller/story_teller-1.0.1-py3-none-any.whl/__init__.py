from .comedy import Comedy
from .horror import Horror

STORIES_MAPPING = {
    "comedy": Comedy().tell_story(),
    "horror": Horror().tell_story()
}


def tell_the_story(story_type):
    story = STORIES_MAPPING.get(story_type, None)

    if story is None:
        raise Exception("Invalid story genre")

    return story
