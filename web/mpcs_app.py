# mpcs_app.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Application logic for the GAS
#
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import base64
import datetime
import hashlib
import hmac
import json
import sha
import string
import time
import urllib
import urlparse
import uuid
import boto3
import botocore.session
import re
from boto3.dynamodb.conditions import Key, Attr

from mpcs_utils import log, auth
from bottle import route, request, redirect, template, static_file

'''
*******************************************************************************
Set up static resource handler - DO NOT CHANGE THIS METHOD IN ANY WAY
*******************************************************************************
'''
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
  # Tell Bottle where static files should be served from
  return static_file(filename, root=request.app.config['mpcs.env.static_root'])

'''
*******************************************************************************
Home page
*******************************************************************************
'''
@route('/', method='GET', name="home")
def home_page():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'home', auth=auth)

'''
*******************************************************************************
Registration form
*******************************************************************************
'''
@route('/register', method='GET', name="register")
def register():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'register',
    auth=auth, name="", email="", username="",
    alert=False, success=True, error_message=None)

@route('/register', method='POST', name="register_submit")
def register_submit():
  try:
    auth.register(description=request.POST.get('name').strip(),
                  username=request.POST.get('username').strip(),
                  password=request.POST.get('password').strip(),
                  email_addr=request.POST.get('email_address').strip(),
                  role="free_user")
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register',
      auth=auth, alert=True, success=False, error_message=error)

  return template(request.app.config['mpcs.env.templates'] + 'register',
    auth=auth, alert=True, success=True, error_message=None)

@route('/register/<reg_code>', method='GET', name="register_confirm")
def register_confirm(reg_code):
  log.info(request.url)
  try:
    auth.validate_registration(reg_code)
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
      auth=auth, success=False, error_message=error)

  return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
    auth=auth, success=True, error_message=None)

'''
*******************************************************************************
Login, logout, and password reset forms
*******************************************************************************
'''
@route('/login', method='GET', name="login")
def login():
  log.info(request.url)
  redirect_url = "/annotations"
  # If the user is trying to access a protected URL, go there after auhtenticating
  if request.query.redirect_url.strip() != "":
    redirect_url = request.query.redirect_url

  return template(request.app.config['mpcs.env.templates'] + 'login',
    auth=auth, redirect_url=redirect_url, alert=False)

@route('/login', method='POST', name="login_submit")
def login_submit():
  auth.login(request.POST.get('username'),
             request.POST.get('password'),
             success_redirect=request.POST.get('redirect_url'),
             fail_redirect='/login')

@route('/logout', method='GET', name="logout")
def logout():
  log.info(request.url)
  auth.logout(success_redirect='/login')


'''
*******************************************************************************
*
CORE APPLICATION CODE IS BELOW...
*
*******************************************************************************
'''

'''
*******************************************************************************
Subscription management handlers
*******************************************************************************
'''
import stripe

# Display form to get subscriber credit card info
@route('/subscribe', method='GET', name="subscribe")
def subscribe():
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  return template(request.app.config['mpcs.env.templates'] + 'subscribe',
  auth=auth)

# Process the subscription request
@route('/subscribe', method='POST', name="subscribe_submit")
def subscribe_submit():
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  token = request.POST.get('stripe_token')
  try:
    # stripe doc on customers: https://stripe.com/docs/api#customers
    stripe.api_key = request.app.config['mpcs.stripe.secret_key']
    customerId = stripe.Customer.create(
      description = 'Customer for ' + auth.current_user.username,
      source = token,
      email = auth.current_user.email_addr
    )
    
    # stripe doc on subscriptions: https://stripe.com/docs/api#subscriptions
    stripe.Subscription.create(
      customer=customerId,
      plan='premium_plan'
    )
    auth.current_user.update(role="premium_user")
    try:
      dynamodb = boto3.resource('dynamodb', region_name=request.app.config['mpcs.aws.app_region']) 
      ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])
      query_results = ann_table.query(IndexName='username_index', KeyConditionExpression=Key('username').eq(auth.current_user.username))
      items = query_results['Items']
      # again, boto glacier doc: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html#Glacier.Client.initiate_job
      glacier = boto3.client('glacier', region_name = request.app.config['mpcs.aws.app_region'])
      for item in items:
        if 'results_file_archive_id' in item:
          response = glacier.initiate_job(
            vaultName = request.app.config['mpcs.aws.glacier.vault'],
            jobParameters = {'Type': 'archive-retrieval', 'SNSTopic': request.app.config['mpcs.aws.sns.archive_retrieve_topic'],
                           'ArchiveId': item['results_file_archive_id'], 'Tier': 'Expedited'}
          )
    except ClientError as e:
      # Notification email should be sent to admin here
      print "Unexpected error: %s" % e
      raise
  # stripe doc on error handling: https://stripe.com/docs/api#error_handling
  # in real life, gotta do something more with these than just pass on, which is dumb
  # this just showing that we may want to do something for each one of these
  except stripe.error.CardError as e:
    body = e.json_body
    err  = body['error']

    print "Status is: %s" % e.http_status
    print "Type is: %s" % err['type']
    print "Code is: %s" % err['code']
    # param is '' in this case
    print "Param is: %s" % err['param']
    print "Message is: %s" % err['message']
  except stripe.error.RateLimitError as e:
    # Too many requests made to the API too quickly
    print 'too many requests made, slow it down!'
    pass
  except stripe.error.InvalidRequestError as e:
    # Invalid parameters were supplied to Stripe's API
    print 'invalid params sent into stripe'
    pass
  except stripe.error.AuthenticationError as e:
    # Authentication with Stripe's API failed
    # (maybe you changed API keys recently)
    print 'you got your auth wrong'
    pass
  except stripe.error.APIConnectionError as e:
    # Network communication with Stripe failed
    print 'could not communicate with stripe'
    pass
  except stripe.error.StripeError as e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
    print 'not really sure what went wrong'
    pass
  except Exception as e:
    # Something else happened, completely unrelated to Stripe
    print 'really not sure what went wrong'
    raise
    pass

  return template(request.app.config['mpcs.env.templates'] + 'subscribe_confirm',
  auth=auth, stripe_id=customerId['id'])

'''
*******************************************************************************
Display the user's profile with subscription link for Free users
*******************************************************************************
'''
@route('/profile', method='GET', name="profile")
def user_profile():
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  return template(request.app.config['mpcs.env.templates'] + 'profile',
  auth=auth)


'''
*******************************************************************************
Creates the necessary AWS S3 policy document and renders a form for
uploading an input file using the policy document
*******************************************************************************
'''
@route('/annotate', method='GET', name="annotate")
def upload_input_file():
  log.info(request.url)

  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)

  # Use the boto session object only to get AWS credentials
  session = botocore.session.get_session()
  aws_access_key_id = str(session.get_credentials().access_key)
  aws_secret_access_key = str(session.get_credentials().secret_key)
  aws_session_token = str(session.get_credentials().token)

  # Define policy conditions
  bucket_name = request.app.config['mpcs.aws.s3.inputs_bucket']
  encryption = request.app.config['mpcs.aws.s3.encryption']
  acl = request.app.config['mpcs.aws.s3.acl']

  # Generate unique ID to be used as S3 key (name)
  key_name = request.app.config['mpcs.aws.s3.key_prefix'] + str(uuid.uuid4())

  # Redirect to a route that will call the annotator
  redirect_url = str(request.url) + "/job"

  if auth.current_user.role == 'free_user':
    content_length = 150000
  else:
    # premium can go up to 10 MB
    content_length = 10485760

  # Define the S3 policy doc to allow upload via form POST
  # The only required elements are "expiration", and "conditions"
  # must include "bucket", "key" and "acl"; other elements optional
  # NOTE: We also must inlcude "x-amz-security-token" since we're
  # using temporary credentials via instance roles
  policy_document = str({
    "expiration": (datetime.datetime.utcnow() +
      datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "conditions": [
      {"bucket": bucket_name},
      ["starts-with","$key", key_name],
      ["starts-with", "$success_action_redirect", redirect_url],
      ["content-length-range", 0, content_length],
      {"x-amz-server-side-encryption": encryption},
      {"x-amz-security-token": aws_session_token},
      {"acl": acl}]})

  # Encode the policy document - ensure no whitespace before encoding
  policy = base64.b64encode(policy_document.translate(None, string.whitespace))

  # Sign the policy document using the AWS secret key
  signature = base64.b64encode(hmac.new(aws_secret_access_key, policy, hashlib.sha1).digest())

  # Render the upload form
  # Must pass template variables for _all_ the policy elements
  # (in addition to the AWS access key and signed policy from above)
  return template(request.app.config['mpcs.env.templates'] + 'upload',
    auth=auth, bucket_name=bucket_name, s3_key_name=key_name,
    aws_access_key_id=aws_access_key_id,
    aws_session_token=aws_session_token, redirect_url=redirect_url,
    encryption=encryption, acl=acl, policy=policy, signature=signature,
    content_length=content_length)


'''
*******************************************************************************
Accepts the S3 redirect GET request, parses it to extract
required info, saves a job item to the database, and then
publishes a notification for the annotator service.
*******************************************************************************
'''
@route('/annotate/job', method='GET')
def create_annotation_job_request():
  auth.require(fail_redirect='/login?redirect_url=' + request.url)  
  bucket_name = request.query.bucket
  s3_key = str(request.query.key)
  prefix = str(request.app.config['mpcs.aws.s3.key_prefix'])
  matcher = re.search('.+/(.+)~(.+)', s3_key)
  user = auth.current_user.username
  job_id = str(matcher.group(1))
  input_file_name = str(matcher.group(2))
  submit_time = int(time.time())
  user_email = auth.current_user.email_addr
  try:
    data = {'job_id': job_id, 'username': user, 'input_file_name': input_file_name, 's3_inputs_bucket': bucket_name, 's3_key_input_file': s3_key, 'submit_time': submit_time, 'job_status': 'PENDING', 'user_email': user_email}
    dynamodb = boto3.resource('dynamodb', region_name=request.app.config['mpcs.aws.app_region'])
    ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])
    ann_table.put_item(Item=data)
    client = boto3.client('sns', region_name=request.app.config['mpcs.aws.app_region'])
    client.publish(TopicArn=str(request.app.config['mpcs.aws.sns.job_request_topic']), Message=json.dumps(data))
  except ClientError as e:
    # Notification email should be sent to admin here
    print "Unexpected error: %s" % e
    raise
  redirect_url = str('/annotations/' + job_id)
  redirect(redirect_url)

'''
*******************************************************************************
List all annotations for the user
*******************************************************************************
'''
@route('/annotations', method='GET', name="annotations_list")
def get_annotations_list():
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  try:
    dynamodb = boto3.resource('dynamodb', region_name=request.app.config['mpcs.aws.app_region'])
    ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])
    query_results = ann_table.query(IndexName='username_index', KeyConditionExpression=Key('username').eq(auth.current_user.username))
    items = query_results['Items']
    link_url = '/annotate'
  except ClientError as e:
    # Notification email should be sent to admin here
    print "Unexpected error: %s" % e
    raise
  return template(request.app.config['mpcs.env.templates'] + 'annotations',
  items=items, auth=auth, link_url=link_url)

'''
*******************************************************************************
Display details of a specific annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>', method='GET', name="annotation_details")
def get_annotation_details(job_id):
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  try:
    dynamodb = boto3.resource('dynamodb', region_name=request.app.config['mpcs.aws.app_region'])
    ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])
    query_result = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
    job = query_result['Items'][0]
    job_user = job['username']
    request_time = time.ctime(job['submit_time'])
    s3 = boto3.client('s3', region_name=request.app.config['mpcs.aws.app_region'])
    if 's3_key_result_file' in job:
      annot_url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': request.app.config['mpcs.aws.s3.results_bucket'], 
  					'Key': job['s3_key_result_file']})
    else:
      annot_url = 'N/A'
  except ClientError as e:
    # Notification email should be sent to admin here
    print "Unexpected error: %s" % e
    raise
  if 'complete_time' in job:
    complete_time = time.ctime(job['complete_time'])
    complete_int = job['complete_time']
  else:
    complete_time = 'N/A'
    complete_int = 0
  if job_user == auth.current_user.username:  
    return template(request.app.config['mpcs.env.templates'] + 'ann_detail',
    auth=auth, job_id=job_id, request_time=request_time, input_file_name=job['input_file_name'],
    job_status=job['job_status'], complete_time=complete_time, annot_url=annot_url,
    complete_int=complete_int)
  else:
    redirect('/unauthorized')

'''
*******************************************************************************
Display the log file for an annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>/log', method='GET', name="annotation_log")
def view_annotation_log(job_id):
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  s3 = boto3.client('s3', region_name=request.app.config['mpcs.aws.app_region'])
  dynamodb = boto3.resource('dynamodb', region_name=request.app.config['mpcs.aws.app_region'])
  ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])
  query_result = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
  job = query_result['Items'][0]
  logFile = s3.get_object(Bucket=request.app.config['mpcs.aws.s3.results_bucket'], Key=job['s3_key_log_file'])
  logText = logFile['Body'].read()
  return template(request.app.config['mpcs.env.templates'] + 'view_log',
  auth=auth, logText=logText, job_id=job_id)

'''
*******************************************************************************
Display the unauthorized page
*******************************************************************************
'''
@route('/unauthorized', method='GET')
def unauthorized():
  return template(request.app.config['mpcs.env.templates'] + 'unauthorized',
  auth=auth)

### EOF
