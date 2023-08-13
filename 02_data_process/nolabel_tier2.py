# nolabel_tier2.py
import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import col, explode, struct, lit, concat, split, array
from pyspark.ml.feature import Tokenizer

spark = SparkSession.builder \
    .master("yarn") \
    .appName("NOLABEL") \
    .getOrCreate()

ssg = spark.read.option("multiline", "true").option("header", "true").parquet(
    "pjt3/first/nolabel_ssg1.parquet").withColumn('source', lit('ssg'))
naver = spark.read.option("multiline", "true").option("header", "true").parquet(
    "pjt3/first/nolabel_naver1.parquet").withColumn('source', lit('naver'))
kurly = spark.read.option("multiline", "true").option("header", "true").parquet(
    "pjt3/first/nolabel_kurly1.parquet").withColumn('source', lit('kurly'))

total = naver.union(ssg).union(kurly) \
    .filter(col('title') != '') \
    .filter((col('volume') != '') & (col('quantity') != '')) \
    .withColumn('quantity', f.regexp_replace('quantity', r'(개입|개|입|병|펫|캔|EA|PET|CAN|페트)', '')) \
    .withColumn('volume', f.regexp_replace('volume', r'(L|리터)', 'L')) \
    .withColumn('price', f.regexp_replace('price', r',', '')) \
    .withColumn('price', f.regexp_replace('price', r'원', '')) \
    .withColumn('price_unit', f.round(col('price') / col('quantity').cast('int'), 2)) \
    .sort(["title", "price_unit"]).coalesce(1).dropDuplicates(['title', 'volume']).sort(["title", "price_unit"])

tokenizer = Tokenizer(inputCol="title", outputCol="proc")

final = tokenizer.transform(total).withColumn('proc', f.array_distinct(col('proc'))) \
    .withColumn('proc', f.concat_ws(" ", col('proc'))) \
    .withColumn('proc', f.upper(col('proc'))) \
    .select('id', col('proc').alias('title'), 'volume', 'quantity', 'price', 'price_unit', 'link', 'img_link') \
    .sort(["title", "price_unit"]).coalesce(1).dropDuplicates(['title', 'volume']).sort(["title", "price_unit"])

df = final.toPandas()
df.to_json("/home/multi/pjt3/final.json")
