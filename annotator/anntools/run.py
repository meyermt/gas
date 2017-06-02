# Copyright (C) 2011-2016 Vas Vasiliadis
# University of Chicago
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import sys
import time
import driver
import boto3
import re
import shutil
import os.path
import json
import botocore
from boto3.dynamodb.conditions import Key
from ConfigParser import SafeConfigParser

count_suffix = '.count.log'
annot_suffix = '.annot.vcf'

# A rudimentary timer for coarse-grained profiling
class Timer(object):
        def __init__(self, verbose=False):
                self.verbose = verbose

        def __enter__(self):
                self.start = time.time()
                return self

        def __exit__(self, *args):
                self.end = time.time()
                self.secs = self.end - self.start
                self.msecs = self.secs * 1000  # millisecs
                if self.verbose:
                        print "Elapsed time: %f ms" % self.msecs

if __name__ == '__main__':
        parser = SafeConfigParser()
        parser.read('../mpcs.conf')
        bucket_name = parser.get('mpcs.aws.s3', 'results_bucket')
        region = parser.get('mpcs.aws', 'app_region')
        # Call the AnnTools pipeline
        if len(sys.argv) > 1:
                input_file_name = sys.argv[1]
                with Timer() as t:
                        driver.run(input_file_name, 'vcf')
                print "Total runtime: %s seconds" % t.secs

                print 'your filename is ' + input_file_name
                # boto3 api for uploads: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.upload_file
                try:
                        job_id = sys.argv[2]
                        s3 = boto3.resource('s3', region_name=region)
                        no_ext = os.path.splitext(input_file_name)[0]
                        matcher = re.search('(.*)/(meyermt.*)', input_file_name)
                        save_as = matcher.group(2)
                        ann_file = no_ext + annot_suffix
                        s3_annot_key = save_as + annot_suffix
                        s3.meta.client.upload_file(ann_file, bucket_name, s3_annot_key)
                        count_file = input_file_name + count_suffix
                        s3_count_key = save_as + count_suffix
                        s3.meta.client.upload_file(count_file, bucket_name, s3_count_key)
                        dynamodb = boto3.resource('dynamodb', region_name=region)
                        ann_table = dynamodb.Table(parser.get('mpcs.aws.dynamodb', 'annotations_table'))
                        # info on updating http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.Python.03.html#GettingStarted.Python.03.03
                        ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="SET s3_key_log_file = :s3_key_log", ExpressionAttributeValues={ ':s3_key_log': s3_count_key})
                        ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="SET s3_key_result_file = :s3_key_file", ExpressionAttributeValues={ ':s3_key_file': s3_annot_key})
                        ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="SET complete_time = :comp_time", ExpressionAttributeValues={ ':comp_time': int(time.time())})
                        ann_table.update_item(Key={'job_id': job_id}, UpdateExpression="SET job_status = :run_status", ExpressionAttributeValues={ ':run_status': 'COMPLETED'})
                        # will publish notification that job has completed
                        client = boto3.client('sns', region_name=region)
                        query_result = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
                        item = query_result['Items'][0]
                        data = {'job_id': job_id, 'username': item['username'], 'user_email': item['user_email']}
        		response = client.publish(TopicArn=parser.get('mpcs.aws.sns', 'job_complete_topic'), Message=json.dumps(data))
                except ClientError as e:
                        # Notification email should be sent to admin here
                        print "Unexpected error: %s" % e
                        raise
                print ('response is ' + str(response))
		del_path = matcher.group(1)
                # shutil api: https://docs.python.org/2/library/shutil.html
                shutil.rmtree(del_path)
        else:
                print 'A valid .vcf file must be provided as input to this program.'
