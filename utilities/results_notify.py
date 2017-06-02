# Results Notifier
##
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import boto3
import sys
import json
import uuid
import os.path
import os
import subprocess
from ConfigParser import SafeConfigParser

def main(argv=None):
    parser = SafeConfigParser()
    parser.read('mpcs.conf')
    region = parser.get('mpcs.aws', 'app_region')
    try:
        sqs = boto3.resource('sqs', region_name=region)
        queue = sqs.get_queue_by_name(QueueName=parser.get('mpcs.aws.sqs', 'job_results_queue'))
        url = 'https://meyermt.ucmpcs.org:4433/annotations/'
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

                job_id = str(msg_body['job_id'])
                user_email = str(msg_body['user_email'])
                job_user = str(msg_body['username'])
                try:
                    client = boto3.client('ses', region_name=region)
                    sender = parser.get('mpcs.auth', 'email_sender')
                    client.send_email(Source=sender, Destination={'ToAddresses': [user_email]}, 
                                        Message={'Subject': {'Data': 'GAS Job Complete'},
                                        'Body': {'Html': {'Data': "Job <a href=\"" + url + job_id + "\">" + job_id + "</a> has completed."}}})

                    message.delete()
                    print 'deleted job from queue'
                except ClientError as e:
                    # Notification email should be sent to admin here
                    print "Unexpected error: %s" % e
                    raise

if __name__ == "__main__":
  sys.exit(main())

### EOF
