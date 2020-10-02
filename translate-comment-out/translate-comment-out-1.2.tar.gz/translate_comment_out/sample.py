from translate_comment_out.translator import translate


translated_source = translate(filepath='sample.js', dest='ja')
print(translated_source)
