def _url_sanitizer(url):
  if url[-1] != "/":
    url = url + "/"

  if url[0] == "/":
    url = url[1:]

  if url[-12:] == "?format=json":
    return url
  else:
    return url + "?format=json"
