from __future__ import print_function
from pprint import pprint
from time import time
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
import requests
from requests_aws4auth import AWS4Auth
import urllib.parse
import json

# TESTING !!!

REGION = 'us-east-1'
HOST = 'search-photos-xzh7hrqko56izsipclb6hdfng4.us-east-1.es.amazonaws.com'
INDEX = 'photos' #domain name of OS
SERVICE = 'es'

s3 = boto3.client('s3')

rekognition_client = boto3.client('rekognition')

print('Loading function')

cred = boto3.Session().get_credentials()
auth = AWS4Auth(cred.access_key, cred.secret_key, REGION, SERVICE, session_token=cred.token)

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    image = event['Records'][0]['s3']['object']['key']
    
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(key)
    
    try:
        response_r = rekognition_client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}})
        labels = response_r['Labels']
        print(labels)
        custom_labels=[]
        for label in labels:
            custom_labels.append(label['Name'])
        response = s3.head_object(Bucket=bucket, Key=key)
        timeStamp = response['LastModified'].isoformat()
        indexmetadata = json.dumps(response['Metadata'])
        format={
            'objectKey':image,
            'bucket':bucket,
            'createdTimeStamp':timeStamp,
            'labels':custom_labels,
            'metadata' :indexmetadata
        }
        
        jsonBody = json.dumps(format)
        print(jsonBody)
        # - aws lambda update-function-code --function-name photos-indexing-1 --zip-file fileb://deployment_package.zip
        url = HOST + '/' + INDEX + '/_doc'
        print(url)
        headers = { "Content-Type": "application/json" }
        print(headers)
        # r = requests.post(url, auth=auth, data=jsonBody)
        # # , headers=headers)
        # print(r)
        
        osClient = OpenSearch(
        hosts=[{'host': str(HOST), 'port':443}],
        use_ssl=True,
        http_auth=auth,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
        
        temp=osClient.index(index='photos', body=format)
        print(temp)
        
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    



# from __future__ import print_function
# from pprint import pprint
# from time import time
# import boto3
# import json
# from opensearchpy import OpenSearch, RequestsHttpConnection
# import requests
# from requests_aws4auth import AWS4Auth
# import urllib.parse
# import json

# REGION = 'us-east-1'
# HOST = 'search-photos-xzh7hrqko56izsipclb6hdfng4.us-east-1.es.amazonaws.com'
# INDEX = 'photos' #domain name of OS
# SERVICE = 'es'

# client = boto3.client('lexv2-runtime')

# cred = boto3.Session().get_credentials()
# auth = AWS4Auth(cred.access_key, cred.secret_key, REGION, SERVICE, session_token=cred.token)

# def lambda_handler(event, context):
#     client = boto3.client('lexv2-runtime')
#     # print(json.dumps(event))
#     # HOW TO GET QUERY FROM FRONT
#     # q1 = "show me tree and dog"
#     # event["q"]    
#     q1 = event["queryStringParameters"]["q"]
#     # q1 = "dog"
#     labels = send_msg_toLex(q1)
    
#     print(labels)
#     output = []
    
#     if len(labels) != 0:
#       osClient = OpenSearch(
#         hosts=[{'host': str(HOST), 'port':443}],
#         use_ssl=True,
#         http_auth=auth,
#         verify_certs=True,
#         connection_class=RequestsHttpConnection)
        
#       resp = []
#       for key in labels:
#         print("key")
#         print(key)
#         if (key is not None) and key != '':
#             searchData = osClient.search({"query": {"match": {"labels": key}}})
#             print("search data:")
#             print(searchData)
#             resp.append(searchData)
#       print(resp)
#       for r in resp:
#         if 'hits' in r:
#              for val in r['hits']['hits']:
#                 key = val['_source']['objectKey']
#                 if key not in output:
#                     output.append('https://b2-ccbd-asgn2.s3.amazonaws.com/'+key)
      
#     img_paths = list(set(output))
#     print(output)
    
#     if not img_paths:
#         return {
#             "isBase64Encoded": False,
#             "statusCode": 200,
#             "headers": {"Access-Control-Allow-Origin":"*"},
#             'body': json.dumps({
#                   'imagePaths': [],
#                   'userQuery': q1,
#                   'labels': labels
#                 })
#         }
#     else:    
#         return {
#             'isBase64Encoded': False,
#             'statusCode': 200,
#             'headers': {"Access-Control-Allow-Origin": "*"},
#             'body': json.dumps({
#                   'imagePaths': img_paths,
#                   'userQuery': q1,
#                   'labels': labels
#                 })
#             }
    
# def send_msg_toLex(msg_from_user):
#   # Initiate conversation with Lex
#   response = client.recognize_text(
#     botId='W9GA1VXKUM', # MODIFY HERE
#     botAliasId='VOUTGWZY2Q', # MODIFY HERE
#     localeId='en_US',
#     sessionId='testuser',
#     text=msg_from_user)
  
#   msg_from_lex = response.get('messages', [])
#   if msg_from_lex:
#     print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
#     print(response)
  
#   print(response)
  
#   slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})
#   print("SLOTS : ", slots)
#   result_array = []
#   for key, value in slots.items():
#     if key == 'slot1':
#         result_array.append(value['value']['interpretedValue'])
#     if key == 'slot2':
#         result_array.append(value['value']['interpretedValue'])
    
#   print(result_array)
#   return result_array
    
