## Load Test for Annotator
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import sys
import time

def main(argv=None):
	parser = SafeConfigParser()
    parser.read('mpcs.conf')
    region = parser.get('mpcs.aws', 'app_region')
    ctr = 1

    while True:

    	# this will bomb the req queue with tons of messages
    	client = boto3.client('sns', region_name=region)
  		client.publish(TopicArn=parser.get('mpcs.aws.sns', 'job_request_topic'), Message='load-test')
  		print 'wrote test message ' + str(ctr)
  		ctr = ctr + 1
  		time.sleep(3)

if __name__ == "__main__":
  sys.exit(main())

### EOF
