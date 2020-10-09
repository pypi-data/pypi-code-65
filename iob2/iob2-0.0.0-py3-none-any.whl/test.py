
# iob2コーパス

import sys
from sout import sout
from relpath import add_import_path
add_import_path("../")
from iob2 import Corpus	# iob2コーパス

# コーパス読み込み
corpus = Corpus("./test_corpus.iob2")	# iob2コーパス
# debug
sout(corpus)
# 区切りの取得
sent_sep = corpus.get_sep("sentence")
# debug
sout(sent_sep)
