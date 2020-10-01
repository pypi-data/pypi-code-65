short_words = ["the", "in", "a", "as", "to", "be", "an", "for", "nor", "but", "yet", "so", "at", "around", "by", "after", "along", "for", "from", "of", "on", "to", "with", "without"]

def titlecaps(s):
    words = s.lower().split()
    for i in range(0, len(words)):
        if words[i] not in short_words and len(words[i])>3:
            words[i] = words[i].capitalize()
    words[0] = words[0].capitalize()
    return " ".join(words)
