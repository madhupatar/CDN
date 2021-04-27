import csv
import pickle

popular = {}
for l in csv.reader(open('/course/cs5700sp21/pageviews.csv').readlines()[1: 50]):
    popular["/" + l[0]] = l[1]

try:
    popular_file = open("popular", "wb")
    pickle.dump(popular, popular_file)
    popular_file.close()
except:
    print("Unable to load popular file")