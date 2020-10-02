from translate_bookmark import article


def test_get_article_for_packerswire():
    url = 'https://packerswire.usatoday.com/2020/10/01/losing-ascending-wr-allen-lazard-is-a-tough-blow-for-packers/'
    actual: str = article.get_article_for_packerswire(url=url)
    expect: str = 'The Green Bay Packers are suddenly razor-thin at the wide receiver position.\nWhile Davante Adams is close'
    assert actual.startswith(expect)
