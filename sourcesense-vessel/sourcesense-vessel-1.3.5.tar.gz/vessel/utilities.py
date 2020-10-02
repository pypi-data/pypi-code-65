import urllib

def sanitizeClusterName(name):
  return urllib.parse.quote(name.lower()
    .replace(" ", "-")
    .replace("_", "-")
    .replace(".", "-"))