import boto3
import logging


# logging config
logging.basicConfig(
    # filename="stage_dump.log",
    # filemode="w",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)


# Funcion para dumpear items en S3
def s3_items_from_table(s3_client, bucket, prefix):
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    objects = []
    for page in pages:
        for item in page["Contents"]:
            objects.append(item["Key"])
    return objects


def move_from_s3_to_s3(
    object, source_bucket_name, source_s3_r, target_bucket_name, destination_s3_r
):
    # create a reference to source image
    old_obj = source_s3_r.Object(source_bucket_name, object)
    # create a reference for destination image
    new_obj = destination_s3_r.Object(target_bucket_name, object)
    # upload the image to destination S3 object
    new_obj.put(Body=old_obj.get()["Body"].read())


# Credenciales AWS Source
aws_access_key_id = "your_access_key"
aws_secret_access_key = "your_secret_key"
aws_session_token = "your_session_token"
aws_access_key_id_source = aws_access_key_id
aws_secret_access_key_source = aws_secret_access_key
aws_session_token_source = aws_session_token

# Credenciales AWS Target
aws_access_key_id = "your_access_key"
aws_secret_access_key = "your_secret_key"
aws_session_token = "your_session_token"
aws_access_key_id_target = aws_access_key_id
aws_secret_access_key_target = aws_secret_access_key
aws_session_token_target = aws_session_token


## VARIABLES DE CORRIDA ##
source_bucket = "f14-datalake-raw-prod"
target_bucket = "f14-datalake-raw-dev"

source_prefix = (
    "amazon_sp_api/get_fba_fulfillment_current_inventory_data/p_creation_dt=2021-10-27/"
)
target_prefix = (
    "amazon_sp_api/get_fba_fulfillment_current_inventory_data/p_creation_dt=2021-10-27/"
)


# Cliente S3 para recorrer el origen
s3_source = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id_source,
    aws_secret_access_key=aws_secret_access_key_source,
    aws_session_token=aws_session_token_source,
)


# Cliente S3 para recorrer el target
s3_target = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id_target,
    aws_secret_access_key=aws_secret_access_key_target,
    aws_session_token=aws_session_token_target,
)


# Source Session
session_src = boto3.session.Session(
    aws_access_key_id=aws_access_key_id_source,
    aws_secret_access_key=aws_secret_access_key_source,
    aws_session_token=aws_session_token_source,
    region_name="eu-west-1",
)
# Source Resource
source_s3_r = session_src.resource("s3")


# Target Session
session_destination = boto3.session.Session(
    aws_access_key_id=aws_access_key_id_target,
    aws_secret_access_key=aws_secret_access_key_target,
    aws_session_token=aws_session_token_target,
    region_name="eu-west-1",
)

# Target Resource
destination_s3_r = session_destination.resource("s3")


# Obtiene items de S3 source
list_s3_objects_source = s3_items_from_table(
    s3_client=s3_source, bucket=source_bucket, prefix=source_prefix
)


logging.info(f"Cantidad de objetos en source: {len(list_s3_objects_source)}")
logging.info(list_s3_objects_source[:4])


# Copying elements one by one
if len(list_s3_objects_source) > 0:
    c = 0
    for obj in list_s3_objects_source:
        try:
            move_from_s3_to_s3(
                obj, source_bucket, source_s3_r, target_bucket, destination_s3_r
            )
            c += 1
            logging.info(f"OK:   file_nro:{c}   >>{obj}<<")
        except Exception as exception:
            logging.info(f"FAILED:   >>{obj}<<  FAILED REASON:   >>{exception}<<")
    logging.info(f"Process Finished: {len(list_s3_objects_source)} copied")
else:
    logging.info("Nothing to move")
