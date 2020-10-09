
# iob2コーパス

import sys
from sout import sout

# iob2コーパス
class Corpus:
	# 初期化処理
	def __init__(self, corpus_filename):
		# ファイル読み込み
		with open(corpus_filename, "r", encoding = "utf-8") as f:
			raw_str = f.read()
	# 区切りの取得
	def get_sep(self, mode):
		raise Exception("mijisso!")
		# if mode == "sentence":
		# if mode == ""
	# 形態素数
	def __len__(self):
		raise Exception("mijisso!")
	# スライス
	def __getitem__(self, idx):
		raise Exception("mijisso!")

# # コーパス読み込み
# def load_corpus(corpus_filename):
# 	# 整形
# 	row_ls = raw_str.split("\n")
# 	for row in row_ls:

# 	pass

# 	# 整形
# 	corpus = []
# 	rec_buff, sent_buff = [], []
# 	row_ls = raw_str.split("\n")
# 	for row in row_ls:
# 		if row.strip() != "":
# 			word, tag = row.split('\t')
# 			if word in div_ls:
# 				# 文の切れ目の場合
# 				sent_buff.append([word, tag])
# 				rec_buff.append(sent_buff)
# 				sent_buff = []
# 			else:
# 				# 文 / レコードの切れ目ではない場合
# 				sent_buff.append([word, tag])
# 		else:
# 			# レコードの切れ目の場合
# 			corpus.append(rec_buff)
# 			rec_buff = []
# 	# コーパス末尾の処理 (バッファが残っていたら格納する)
# 	if sent_buff != []:
# 		rec_buff.append(sent_buff)
# 	if rec_buff != []:
# 		corpus.append(rec_buff)


# 	return corpus

