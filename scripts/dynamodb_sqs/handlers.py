import json
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError


class ElapsedTimeFilter(logging.Filter):
    """
    Logging filter that injects the elapsed time since the filter's creation
    into each log record.

    Attributes
    ----------
    start_time : datetime
        The time when the filter (and typically the logger) was created.
        Used as the reference point for elapsed time.
    """

    def __init__(self, start_time):
        """
        Initialize the ElapsedTimeFilter.

        Parameters
        ----------
        start_time : datetime
            The reference start time to calculate elapsed time from.
        """
        super().__init__()
        self.start_time = start_time

    def filter(self, record):
        """
        Add the elapsed time (in HH:MM:SS format) to the log record.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to which the elapsed time will be added.

        Returns
        -------
        bool
            Always returns True to allow the log record to be processed.
        """
        elapsed = datetime.now() - self.start_time
        # Format as HH:MM:SS
        record.elapsed = str(elapsed).split(".", maxsplit=1)[0]
        return True


def get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a simple console logger.

    Parameters
    ----------
    name : str
        The name of the logger.
    log_level : int, optional
        The logging level (default is logging.INFO).

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Set up elapsed time filter
    start_time = datetime.now()
    elapsed_filter = ElapsedTimeFilter(start_time)
    console_handler.addFilter(elapsed_filter)

    # Create formatter with elapsed time
    formatter = logging.Formatter(
        "%(asctime)s [%(elapsed)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger if not already present
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


logger = get_logger(__name__)


class DynamoDBHandler:
    """DynamoDB handler for the pipeline."""

    def __init__(self, table_name: str, sqs_message: list):
        self.table_name = table_name
        self.sqs_message = sqs_message
        try:
            session = boto3.Session(profile_name=AWS_PROFILE)
            self.dynamodb = session.resource(
                "dynamodb", region_name=AWS_REGION
            )
            self.table = self.dynamodb.Table(table_name)
        except (NoRegionError, NoCredentialsError) as e:
            logger.error("AWS configuration error: %s", e)
            raise
        except ClientError as e:
            logger.error("Failed to initialize DynamoDB client: %s", e)
            raise

    def get_row_id(self):
        """Get the item id from the SQS message."""
        body = self.sqs_message["Body"]
        try:
            body_json = json.loads(body)
            row_id = (
                body_json.get("dynamodb", {})
                .get("Keys", {})
                .get("id", {})
                .get("S", "")
            )
            logger.info("Processing row_id: %s", row_id)
            return row_id
        except (json.JSONDecodeError, ClientError) as e:
            logger.error("Error processing message: %s", e)
            return None

    def get_row(self):
        """Get an item from the table."""
        row_id = self.get_row_id()
        if row_id:
            response = self.table.get_item(Key={"id": row_id})
            return response.get("Item", {})
        return None

    def get_row_value(self, key: str):
        """Get an item value from the table."""
        row = self.get_row()
        if row:
            return row.get(key, "")
        return ""

    def update_row(
        self,
        key: dict,
        update_expression: str,
        expression_attribute_names: dict,
        expression_values: dict,
    ):
        """Update an item in the table."""
        self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_values,
        )


class SQSHandler:
    """SQS handler for the pipeline."""

    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        try:
            session = boto3.Session(profile_name=AWS_PROFILE)
            self.sqs = session.client("sqs", region_name=AWS_REGION)
        except (NoRegionError, NoCredentialsError) as e:
            logger.error("AWS configuration error: %s", e)
            raise
        except ClientError as e:
            logger.error("Failed to initialize SQS client: %s", e)
            raise

    def get_message(self):
        """Receive a message from the queue."""
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=0,
            # Makes message visible again right after receive
            VisibilityTimeout=0,
        )
        try:
            messages = response.get("Messages", [])
            if messages:
                logger.info("Message received from queue")
                return messages
            return []
        except ClientError as e:
            logger.error(
                "Error receiving message from queue: %s",
                e.response["Error"]["Message"],
            )
            return []

    def delete_message(self, message: dict):
        """Delete a message from the queue."""
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=message["ReceiptHandle"],
        )
        logger.info("Message deleted from queue")


# AWS Configuration
AWS_REGION = "us-east-1"
AWS_PROFILE = "tram-case-playground"
SQS_QUEUE_URL = (
    "https://sqs.us-east-1.amazonaws.com/442426869000/file-pointer-queue"
)
DYNAMODB_TABLE_NAME = "ddp-event-table"

# Example usage
if __name__ == "__main__":
    try:
        sqs_handler = SQSHandler(SQS_QUEUE_URL)
        sqs_message = sqs_handler.get_message()
        print(sqs_message)

        if sqs_message:
            dynamodb_handler = DynamoDBHandler(
                DYNAMODB_TABLE_NAME, sqs_message[0]
            )
            row = dynamodb_handler.get_row()
            print(row)

            # Get the row value
            row_value = dynamodb_handler.get_row_value("s3_path")
            print(row_value)

            # Update the item
            dynamodb_handler.update_row(
                key={"id": row["id"]},
                update_expression="SET #s = :new_status",
                expression_attribute_names={"#s": "status"},
                expression_values={":new_status": "FINISHED"},
            )

            sqs_handler.delete_message(sqs_message[0])

    except (NoRegionError, NoCredentialsError, ClientError) as e:
        logger.error("AWS operation failed: %s", e)
        exit(1)
