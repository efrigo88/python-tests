import boto3
import logging

# Run variables
env = "prod"

raw = f"uala-arg-datalake-raw-{env}"
stage = f"uala-arg-datalake-stage-{env}"
analytics = f"uala-arg-datalake-analytics-{env}"

pipe_gp = "7001D"
prefix = f"ar/gp/T{pipe_gp}"
prefix_analytics = f"ar/tb_ar_gp_t{pipe_gp[:4]}"

# logging config
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

dts_to_delete = [
    "2020-10-20",
    "2020-10-21",
    "2020-10-22",
    "2020-10-23",
    "2020-10-24",
    "2020-10-25",
    "2020-10-26",
    "2020-10-27",
    "2020-10-28",
    "2020-10-29",
    "2020-10-30",
    "2020-10-31",
    "2020-11-01",
    "2020-11-02",
    "2020-11-03",
    "2020-11-04",
    "2020-11-05",
    "2020-11-06",
    "2020-11-07",
    "2020-11-08",
    "2020-11-09",
    "2020-11-10",
    "2020-11-11",
    "2020-11-12",
    "2020-11-13",
    "2020-11-14",
]


# S3 Client
s3 = boto3.client("s3")


# Dump Fn from S3
def s3_items_from_table(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    objects = []
    for page in pages:
        for item in page["Contents"]:
            objects.append(item["Key"])

    return objects


# Delete function
def s3_one_by_one(bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        return f"key: >>{key}<< successfully deleted"
    except ValueError as e:
        return f"there was a problem with key: >>{key}<<, {e}"


# RAW ########################################
logging.info(f"Bucket to delete from: {raw}\n")

# list S3 Objects
files = s3_items_from_table(bucket=raw, prefix=prefix)
logging.info(f"{len(files)} items in total")


files_to_delete = []
for i in files:
    for j in dts_to_delete:
        if j in i:
            files_to_delete.append(i)


logging.info(f"Number of files to be deleted: {len(files_to_delete)}")
logging.info("List of files to be deleted: ")
for i in files_to_delete:
    logging.info(f"\t>>{i}<<")


# deleting objects one by one
logging.info("\n")
if len(files_to_delete) > 0:
    for i in files_to_delete:
        logging.info(s3_one_by_one(raw, i))
else:
    logging.info("Nothing to delete")


# STAGE ########################################
logging.info(f"Bucket to delete from: {stage}\n")

# list S3 Objects
files = s3_items_from_table(bucket=stage, prefix=prefix)
logging.info(f"{len(files)} items in total")


files_to_delete = []
for i in files:
    for j in dts_to_delete:
        if j in i:
            files_to_delete.append(i)


logging.info(f"Number of files to be deleted: {len(files_to_delete)}")
logging.info("List of files to be deleted: ")
for i in files_to_delete:
    logging.info(f"\t>>{i}<<")


# deleting objects one by one
logging.info("\n")
if len(files_to_delete) > 0:
    for i in files_to_delete:
        logging.info(s3_one_by_one(stage, i))
else:
    logging.info("Nothing to delete")


# ANALYTICS ########################################
logging.info(f"Bucket to delete from: {analytics}\n")

# list S3 Objects
files = s3_items_from_table(bucket=analytics, prefix=prefix_analytics)
logging.info(f"{len(files)} items in total")


files_to_delete = []
for i in files:
    for j in dts_to_delete:
        if j in i:
            files_to_delete.append(i)


logging.info(f"Number of files to be deleted: {len(files_to_delete)}")
logging.info("List of files to be deleted: ")
for i in files_to_delete:
    logging.info(f"\t>>{i}<<")


# deleting objects one by one
logging.info("\n")
if len(files_to_delete) > 0:
    for i in files_to_delete:
        logging.info(s3_one_by_one(analytics, i))
else:
    logging.info("Nothing to delete")

logging.info("The WHOLE process finished successfully!!!")
