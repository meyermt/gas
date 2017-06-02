# Unarchiver Job
##
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import boto3
import botocore
import sys
import json
import uuid
import os.path
import os
import re
import subprocess
from ConfigParser import SafeConfigParser

def main(argv=None):
    parser = SafeConfigParser()
    parser.read('mpcs.conf')
    region = parser.get('mpcs.aws', 'app_region')
    try:
        sqs = boto3.resource('sqs', region_name=region)
        queue = sqs.get_queue_by_name(QueueName=parser.get('mpcs.aws.sqs', 'unarchive_queue'))
    except ClientError as e:
        # Notification email should be sent to admin here
        print "Unexpected error: %s" % e
        raise

    while True:
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10)

        if len(messages) > 0:
            print 'found a message!'
            for message in messages:
                msg_body = json.loads(json.loads(message.body)['Message'])
                try:
                    # boto3 glacier api: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html#Glacier.Client.get_job_output
                    glacier = boto3.client('glacier', region_name = region)
                    response = glacier.get_job_output(
                        vaultName=parser.get('mpcs.aws.glacier', 'vault'),
                        jobId=msg_body['JobId']
                    )
                    input_file = response['archiveDescription']
                    file_content = response['body']		
                    s3 = boto3.client('s3', region_name = region)
                    bucket_name = parser.get('mpcs.aws.s3','results_bucket')
                    prefix = parser.get('mpcs.aws.s3', 'key_prefix')
                    response2 = s3.upload_fileobj(file_content, bucket_name, input_file)
                    print ('upload resp is ' + str(response2))
                    matcher = re.search(prefix + '(.*)~.*', input_file)
                    print ('matcher is ' + str(matcher.group(1)))
                    job_id = matcher.group(1)
                    dynamodb = boto3.resource('dynamodb', region_name=region)
                    ann_table = dynamodb.Table(parser.get('mpcs.aws.dynamodb', 'annotations_table'))
                    ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="REMOVE results_file_archive_id")

                    message.delete()
                    print 'deleted job from queue'
                except ClientError as e:
                    # Notification email should be sent to admin here
                    print "Unexpected error: %s" % e
                    raise

if __name__ == "__main__":
  sys.exit(main())
