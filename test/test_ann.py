## Load Test for Annotator
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import sys
import time
import boto3
from ConfigParser import SafeConfigParser

def main(argv=None):
    parser = SafeConfigParser()
    parser.read('mpcs.conf')
    region = parser.get('mpcs.aws', 'app_region')
    ctr = 1

    while True:

        # this will bomb inside the annotators, but should work for our purposes to scale
        #client = boto3.client('sns', region_name=region)
        #client.publish(TopicArn=parser.get('mpcs.aws.sns', 'job_request_topic'), Message='load-test')
        client = boto3.client('sqs', region_name=region)
        client.send_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/meyermt_job_requests', MessageBody='load-test')
        print 'wrote test message ' + str(ctr)
        ctr = ctr + 1
        time.sleep(5)

if __name__ == "__main__":
    sys.exit(main())

### EOF