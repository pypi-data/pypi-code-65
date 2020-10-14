from translate_bookmark.url import Url, Domain


def test_get_domain():
    url = Url(
        url='https://www.packers.com/news/packers-lb-ty-summers-far-from-satisfied-with-defensive-debut')
    assert url.domain == Domain.PACKERSCOM
