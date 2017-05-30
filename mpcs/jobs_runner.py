# Annotation REST API
##
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import boto3
import sys
import json
import uuid
import os.path
import os
import subprocess

queue_name = request.app.config['mpcs.aws.sqs.job_requests_queue']

def main(argv=None):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    while True:
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10)

        if len(messages) > 0:
            print 'found a message!'
            for message in messages:
                msg_body = json.loads(json.loads(message.body)['Message'])

                job_id = str(msg_body['job_id'])
                print 'processing job: ' + job_id
                s3_key_input_file = msg_body['s3_key_input_file']
                unique_folder = str(uuid.uuid4()) + '/'
                s3_filepath = unique_folder + s3_key_input_file
                # Using a uuid for filepath, so will create dirs each time
                # Some of this from this post: http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
                try:
                    os.makedirs(os.path.dirname(ann_dir + s3_filepath))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
                # boto3 api information about downloading files: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.download_file
                client = boto3.resource('s3')
                client.meta.client.download_file(msg_body['s3_inputs_bucket'], s3_key_input_file, ann_dir + s3_filepath)
                response = {'code': '200 OK'}
                #subprocess.Popen(['python', 'run.py', s3_filepath, job_id])
                dynamodb = boto3.resource('dynamodb')
                ann_table = dynamodb.Table('meyermt_annotations')
                status = ann_table.get_item(Key={'job_id': job_id})['Item']['job_status']
                if status != 'COMPLETED':
                    ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="SET job_status = :run_status", ExpressionAttributeValues={ ':run_status': 'RUNNING'})

                message.delete()
                print 'deleted job from queue'

if __name__ == "__main__":
  sys.exit(main())

### EOF