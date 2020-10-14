from translate_bookmark import article


def test_get_article_for_packerswire():
    url = 'https://packerswire.usatoday.com/2020/10/01/losing-ascending-wr-allen-lazard-is-a-tough-blow-for-packers/'
    actual: str = article.get_article_for_packerswire(url=url)
    assert actual.startswith('The Green Bay')
    assert actual.endswith('injuries.')


def test_get_article_for_dev_to():
    url = 'https://dev.to/courseprobe/top-10-reactjs-tools-used-by-the-most-successful-developers-34e3?utm_source=digest_mailer&utm_medium=email&utm_campaign=digest_email'
    actual: str = article.get_article_for_dev_to(url=url)
    print(actual)
    assert actual.startswith('Did you know')
    assert actual.endswith('Save your Life')


def test_get_article_for_packerscom():
    url = 'https://www.packers.com/news/leaner-crisper-jamaal-williams-making-all-around-impact-on-packers-offense'
    actual: str = article.get_article_for_packers(url=url)
    assert actual.startswith('GREEN BAY')
    assert actual.endswith('at.\"')
