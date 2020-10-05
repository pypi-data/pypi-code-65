def check_thai_sentence_length(input_text):
    syllable = "ั		ิ	ี	ึ	ื	ุ	ู	ฺ ็	่	้	๊	๋	์	ํ	๎"
    for char in syllable:
        input_text = input_text.replace(char, "")
        return len(input_text)
