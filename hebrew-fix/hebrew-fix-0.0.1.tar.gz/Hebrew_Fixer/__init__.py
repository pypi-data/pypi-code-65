




def fixed_result(binary, encode):
    try:
        binary = binary.encode(encode)
        return str(binary, encoding=encode)
    except Exception as e:
        pass


def Fix():
    letters = "א ב ג ד ה ו ז ח ט י כ ל מ נ ס ע פ צ ק ר ש ת".split(" ")
    encodes = ["ISO-8859-8", "Windows-1255", "UTF-8"]
    correct = False
    try:
        for encode in encodes:
            result = fixed_result("קשעש", encode)
            if result is None or result == "":
                continue
            for letter in result:
                if letter not in letters:
                    correct = False
                    break
                correct = True
            if correct:
                return {"result": result, "encode": encode}
    except Exception as e:
        pass




