import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional, Dict, Any
import os
from src.app.repositories.base import IBookRepository
from src.app.schemas.book import BookCreate
from src.app.core.exceptions import EntityAlreadyExistsError
from src.app.core.logging import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DynamoDBBookRepository(IBookRepository):
    def __init__(self, table_name: str):
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT")
        
        # Third: Timeouts - Explicitly set timeouts to prevent hanging
        config = Config(
            connect_timeout=2, 
            read_timeout=2, 
            retries={'max_attempts': 0}
        )
        
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        kwargs = {
            'endpoint_url': endpoint_url,
            'region_name': os.getenv("AWS_REGION", "ap-southeast-2"),
            'config': config
        }
        
        if access_key and secret_key:
            kwargs['aws_access_key_id'] = access_key
            kwargs['aws_secret_access_key'] = secret_key
            
        self.dynamodb = boto3.resource('dynamodb', **kwargs)
        self.table = self.dynamodb.Table(table_name)

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ClientError),
        before_sleep=lambda retry_state: logger.warning(f"Retrying DynamoDB call... Attempt {retry_state.attempt_number}")
    )
    def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={'id': book_id})
            return response.get('Item')
        except ClientError as e:
            logger.error(f"DynamoDB Error getting book {book_id}: {str(e)}")
            raise e

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ClientError),
        before_sleep=lambda retry_state: logger.warning(f"Retrying DynamoDB create... Attempt {retry_state.attempt_number}")
    )
    def create(self, book: BookCreate) -> bool:
        try:
            self.table.put_item(
                Item=book.model_dump(),
                ConditionExpression="attribute_not_exists(id)"
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise EntityAlreadyExistsError("Book", book.id)
            logger.error(f"DynamoDB Error creating book {book.id}: {str(e)}")
            raise e
