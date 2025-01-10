import awswrangler as wr
import pandas as pd
import boto3
import io

s3 = boto3.client('s3')


#df = pd.read_csv("/Users/emif/Downloads/barvivo-na-us-detailsalestrafficbychilditem-2019-11-17.csv")

# print(df.head())

# dest_path = ("s3://f14-datalake-raw-dev/scrapers/seller_central_test/detail_page_sales_and_traffic_by_child_item_by_asin/"
#              "p_creation_dt=2019-11-17/barvivo-na-us-detailsalestrafficbychilditem-2019-11-17.jsonl")



def read_from_s3(s3_client, bucket_name: str, file_prefix: str, encoding: str = "utf-8") -> str:
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_prefix)
    body = obj["Body"].read().decode(encoding)
    return body


bucket_land = 'f14-datalake-landing-dev'
prefix_land = 'integrations/sellerboard_toolzilla_test/table_per_product/10-15-2021_13_39_34.959185.csv'
bucket_raw = 'f14-datalake-raw-dev'

prefix = 'sellerboard/test.jsonl'
path = f"s3://{bucket_raw}/{prefix}"


test = read_from_s3(s3, bucket_land, prefix_land, encoding="utf-8-sig")

df = pd.read_csv(io.StringIO(test), quotechar='"', delim_whitespace=False)

wr.s3.to_json(df, path, orient="records", lines=True)
