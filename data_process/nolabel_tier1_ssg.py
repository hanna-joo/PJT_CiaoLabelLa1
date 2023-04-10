# nolabel_tier1_ssg.py
import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import col, explode, struct, lit, concat, split, array

spark = SparkSession.builder \
    .master("yarn") \
    .appName("SSG") \
    .getOrCreate()

ssg = spark.read.option("multiline", "true").option("header", "true").csv("pjt3/raws/nolabel_ssg.csv")\
.withColumn('title', f.upper(col('title')))\
.sort(["title", "price"], ascending=True).coalesce(1).dropDuplicates(['title'])\
.withColumn('del_labels', f.regexp_extract('title', r'유라벨|유/무|랜덤발송|렌덤발송|혼용발송|랜덤출고|랜덤 발송|랜덤', 0))\
.filter(col('del_labels').isin(''))\
.drop(col('del_labels'))\
.withColumn('id2', f.concat(col('id'), f.lit('02')))\
.select(col('id2').alias('id'), col('title'), col('price'), col('link'), col('img_link'))\
.withColumn('volume', f.regexp_extract('title', r'(\d\.\d{1,3}|\d)+(ML|L|리터)', 0))\
.withColumn('quantity', f.regexp_extract('title', r'\d+(개입|개|입|병|펫|캔|EA|PET|CAN|페트|박스)', 0))\
.withColumn('proc1', f.regexp_replace('title', r'((\d\.\d{1,3}|\d)+(ML|L|리터))*((\d)+(개입|개|입|병|펫|캔|본|EA|PET|CAN|박스|페트))*', ''))\
.withColumn('proc2', f.regexp_replace('proc1', r'( x | X )', ' '))\
.withColumn('proc3', f.regexp_replace('proc2', r'([(\[★][a-zA-Z0-9가-힣 ]*[\])★])*([-=+,#/?:^$@*"※~&%ㆍ!|()\[\]<>`…_★]+)*', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r'(무라벨)*(라벨프리)*(본사직영)*(노라벨)*(생수배달)*(정기배달)*(배달전문)*(다운로드쿠폰증정)*(라벨없는)*(생수배송전문)*(생수전문배송)*(상세설명참조)*', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r'(\d{2,})+', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r'[xX×]', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r'(\s)+', ' '))\
.withColumn('proc3', f.regexp_replace('proc3', r'^ ', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r' $', ''))\
.withColumn('proc3', f.regexp_replace('proc3', r'\d*(박스|EA|PET|CAN)', ''))\
.select('id', col('proc3').alias('title'), 'volume', 'quantity', 'price', 'link', 'img_link')

ssg.write.format('parquet').mode('overwrite').save('pjt3/first/nolabel_ssg1.parquet')
