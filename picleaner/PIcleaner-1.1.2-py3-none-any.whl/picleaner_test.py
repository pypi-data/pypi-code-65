import pytest
import re
from PIcleaner.cleaner import Cleaner

@pytest.fixture(scope="module")
def cleaner():
    return Cleaner()

def test_default_language(cleaner):
    language = 'nl'
    assert cleaner.language == language, "Default Language Failed"

def test_default_model_size(cleaner):
    model_size = 'sm'
    assert cleaner.model_size == model_size, "Default Model Size Failed"

@pytest.mark.parametrize('language', ['bg'])
def test_non_existing_language(language, capsys):
    _ = Cleaner(language)
    captured = capsys.readouterr()
    assert "Spacy model error: {}_core_news_sm".format(language) in captured.out, "Non-Existing Language Improper Exception"


@pytest.mark.parametrize('text', [r'<img src="https://www.oozo.nl/images/noimage.png" />Heb jij een interessante vraag op het snijvlak van privacy, cybersecurity en recht? Stuur je vraag naar',
                                  r'ING doet aangifte om cyberaanval,<p>ING gaat aangifte doen vanwege de grootschalige cyberaanval van zondagavond op het internet- en mobiel bankieren bij de bank</p>',
                                  r'Oekraïne pakt belangrijke cybercrimineel op,"<p>In Oekra&#239;ne is een belangrijke cybercrimineel opgepakt. Gennadi Kapkanov werd zondag gearresteerd in Kiev, meldde de Oekra&#239;ense politie maandag. Hij zou het Avalanche-netwerk hebben geleid.</p>',
                                  r'Politie rolt ’s werelds grootste DDoS-netwerk op; inval in Scheemda,"<img src=""https://www.oozo.nl/images/noimage.png"" />Driebergen &#8211; De Nederlandse politie heeft dinsdag 24 april de grootste cybercriminele website Webstresser.org opgerold. Webstresser.org was een zogenaamde ‘booter’ of ‘stresser’ dienst: een webs'])
def test_remove_html_tags(cleaner, text):
    result = cleaner.clean(text)[0]
    assert re.search('<.*?>', result) is None, "Cleaned String Contains HTML tags"

@pytest.mark.parametrize('text', [r'<img src="https://www.oozo.nl/images/noimage.png" <script>console.log("test");</script>/>Heb jij een interessante vraag op het snijvlak van privacy, cybersecurity en recht? Stuur je vraag naar',
                                  r'<script>console.log("test");</script> Oekraïne pakt belangrijke cybercrimineel op,"<p>In Oekra&#239;ne is een belangrijke cybercrimineel opgepakt. Gennadi Kapkanov werd zondag gearresteerd in Kiev, meldde de Oekra&#239;ense politie maandag. Hij zou het Avalanche-netwerk hebben geleid.</p>',
                                  r'Politie rolt ’s werelds grootste<script>console.log("test");</script>DDoS-netwerk op; inval in Scheemda,"<img src=""https://www.oozo.nl/images/noimage.png"" />Driebergen &#8211; De Nederlandse politie heeft dinsdag 24 april de grootste cybercriminele website Webstresser.org opgerold. Webstresser.org was een zogenaamde ‘booter’ of ‘stresser’ dienst: een webs'])
def test_remove_js_code(cleaner, text):
    result = cleaner.clean(text)[0]
    assert re.search(r'<script[\s\S]*?>[\s\S]*?<\/script>', result) is None, "Cleaned String Contains JavaScript Code"