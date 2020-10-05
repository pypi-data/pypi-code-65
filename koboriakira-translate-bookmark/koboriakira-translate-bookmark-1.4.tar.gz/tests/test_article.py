from translate_bookmark import article


def test_get_article_for_packerswire():
    url = 'https://packerswire.usatoday.com/2020/10/01/losing-ascending-wr-allen-lazard-is-a-tough-blow-for-packers/'
    actual: str = article.get_article_for_packerswire(url=url)
    expect: str = 'The Green Bay Packers are suddenly razor-thin at the wide receiver position.\nWhile Davante Adams is close'
    assert actual.startswith(expect)


def test_get_article_for_dev_to():
    url = 'https://dev.to/courseprobe/top-10-reactjs-tools-used-by-the-most-successful-developers-34e3?utm_source=digest_mailer&utm_medium=email&utm_campaign=digest_email'
    actual: str = article.get_article_for_dev_to(url=url)
    expect: str = 'Increase your value to employers by learning these top tools for developing web apps in React.'
    assert actual.startswith(expect)
