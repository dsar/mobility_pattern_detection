import argparse
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *

def toCSVLine(data):
        return '|'.join(str(attribute) for attribute in data)

def main(args):
        # initialize sc
        sc = SparkContext()
        sqlContext = SQLContext(sc)
        # read file
        dataset = sc.textFile("/datasets/twitter-swisscom/twex.tsv")
        # split each line according to separator
        tokens = dataset.map(lambda l: l.split("\t"))
        # count tweets before filtering
        before = tokens.count()
        # keep only valid lines. valid lines have 20 attributes
        valid_lines = tokens.filter(lambda row: len(row) == 20)
        # count tweets after filtering
        after = valid_lines.count()
        # from each line, keep only necessary attributes
        projection = valid_lines.map(lambda row: [row[1], row[2], row[4], row[5], row[10], row[11]])
        if args.year is not None:
                # filter according to year of tweet
                result = projection.filter(lambda row: args.year in row[1])
                result = result.map(toCSVLine)
                # save result to hdfs
                file_path = "/user/giannako/tweets_" + args.year
                result.saveAsTextFile(file_path)
        else:
                # save all tweets to hdfs
                projection = projection.map(toCSVLine)
                projection.saveAsTextFile("/user/giannako/tweets_all")
        # log messages
        if not args.quiet:
                print("Before filtering: ", before)
                print("After filtering: ", after)
                percentage = float(before - after) / before * 100
                s = "{0:.2f}".format(percentage) + "%"
                print("Filtered: ", s)

if __name__ == "__main__":
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--year", type=str, help="Select which year to filter", default=None)
        argparser.add_argument("--quiet", action="store_true")
        parsed_args = argparser.parse_args()
        main(parsed_args)