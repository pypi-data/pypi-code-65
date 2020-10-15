from iapa.preML import read
from iapa.classification import Classification

print("Address Directory of CSV File:")
csv = input()
print("Address Directory of Results Folder:")
data_path = input()
df = read(csv)
clf = Classification(df, "poly", data_path)
clf.execute()