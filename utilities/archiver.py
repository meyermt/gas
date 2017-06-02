# Archiver
# archives free user
##
__author__ = 'Michael Meyer <meyermt@uchicago.edu>'

import boto3
import sys
import json
import uuid
import os.path
import os
import cork
import time
from boto3.dynamodb.conditions import Key
from ConfigParser import SafeConfigParser

def main(argv=None):
    # site used for SafeConfigParser: https://pymotw.com/2/ConfigParser/
    parser = SafeConfigParser()
    parser.read('mpcs.conf')
    region = parser.get('mpcs.aws', 'app_region')

    # Set up the conenction to the auth database
    auth_db = cork.sqlalchemy_backend.SqlAlchemyBackend(
        db_full_url=parser.get('mpcs.auth', 'db_url'),
        users_tname='users', roles_tname='roles', pending_reg_tname='register', initialize=False)

    # Instantiate an authn/authz provider
    auth = cork.Cork(backend=auth_db,
        email_sender=parser.get('mpcs.auth', 'email_sender'),
        smtp_url=parser.get('mpcs.auth', 'smtp_url'))

    tmp_dir = 'glacier-tmp/'

    try:
        os.makedirs(tmp_dir + parser.get('mpcs.aws.s3', 'key_prefix'))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

    # get system users
    users = auth.list_users()
    #print (users)
    for user in users:

            while True:
                # get system users
                users = auth.list_users()
                #print (users)
                for user in users:
                    if user[1] == 'free_user':
                        try:
                            dynamodb = boto3.resource('dynamodb', region_name=region)
                            ann_table = dynamodb.Table(parser.get('mpcs.aws.dynamodb', 'annotations_table'))
                            query_result = ann_table.query(IndexName='username_index', KeyConditionExpression=Key('username').eq(user[0]))
                            if len(query_result['Items']) > 0:
                                for item in query_result['Items']:
                                    now = int(time.time())
                                    complete_time = item['complete_time']
                                    diff = now - complete_time
                                    if (diff > 1800 and 'results_file_archive_id' not in item):
                                        print('difference in time is ' + str(diff) + ' seconds')
                                        s3 = boto3.client('s3', region_name=region)
                                        results_bucket = parser.get('mpcs.aws.s3', 'results_bucket')
                                        result_file = item['s3_key_result_file']
                                        print ('archiving file: ' + result_file)
                                        tmp_file = tmp_dir + item['s3_key_result_file']
                                        s3.download_file(results_bucket, result_file, tmp_file)
                                        # glacier boto api: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html
                                        glacier = boto3.client('glacier', region_name=region)
                                        response = glacier.upload_archive(vaultName=parser.get('mpcs.aws.glacier', 'vault'), archiveDescription=result_file, body=item['input_file_name'])
                                        archId = response['archiveId']
                                        print ('archived with archiveId: ' + str(archId))
                                        ann_table.update_item(Key={'job_id': item['job_id']}, UpdateExpression="SET results_file_archive_id = :archId",
                                                                                              ExpressionAttributeValues={ ':archId': archId})
                                        s3.delete_object(Bucket=results_bucket, Key=result_file)
                                        os.remove(tmp_file)
                        except ClientError as e:
                            # Notification email should be sent to admin here
                            print "Unexpected error: %s" % e
                            raise
                time.sleep(60)

if __name__ == "__main__":
  sys.exit(main())

### EOF
