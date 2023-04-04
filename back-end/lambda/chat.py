import boto3
import os
from boto3.dynamodb.types import TypeSerializer
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory

from datetime import datetime
import json

now = datetime.utcnow()
pinpoint = boto3.client('pinpoint')
dynamodb = boto3.client('dynamodb')
ts= TypeSerializer()

openai_api_key_ssm_parameter_name = os.environ['OPENAI_API_KEY_SSM_PARAMETER_NAME']
chat_index_table_name = os.environ['CONVERSATION_INDEX_TABLE_NAME']
conversation_table_name = os.environ['CONVERSATION_TABLE_NAME']

class Chat():
    def __init__(self, event):
        self.set_user_number(event)
        self.set_chat_index()
        self.set_memory()

    def set_memory(self):
        _id = self.user_number + "-" + str(self.chat_index)
        self.message_history = DynamoDBChatMessageHistory(table_name=conversation_table_name, session_id=_id)
        self.memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=self.message_history, return_messages=True)

    def get_chat_index(self):
        key = {'phone_number':self.user_number}
        chat_index = dynamodb.get_item(TableName=chat_index_table_name, Key=ts.serialize(key)['M'])
        if 'Item' in chat_index:
            return int(chat_index['Item']['chat_index']['N'])
        return 0

    def increment_chat_index(self):
        self.chat_index += 1
        input = {
            'phone_number': self.user_number,
            'chat_index': self.chat_index,
            'updated_at': str(now)
        }
        dynamodb.put_item(TableName=chat_index_table_name, Item=ts.serialize(input)['M'])

    def create_new_chat(self):
        self.increment_chat_index()

    def set_user_number(self,event):
        body = json.loads(event['body'])
        self.user_number = body['phone_number']

    def set_chat_index(self):
        self.chat_index = self.get_chat_index()

    def http_response(self, message):
        return {
            'statusCode': 200,
            'body': json.dumps(message),
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS
            },
        }