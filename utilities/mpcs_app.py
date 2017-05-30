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
from boto3.dynamodb.conditions import Key

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
  pass

# Process the subscription request
@route('/subscribe', method='POST', name="subscribe_submit")
def subscribe_submit():
  pass


'''
*******************************************************************************
Display the user's profile with subscription link for Free users
*******************************************************************************
'''
@route('/profile', method='GET', name="profile")
def user_profile():
  pass


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
    encryption=encryption, acl=acl, policy=policy, signature=signature)


'''
*******************************************************************************
Accepts the S3 redirect GET request, parses it to extract 
required info, saves a job item to the database, and then
publishes a notification for the annotator service.
*******************************************************************************
'''
@route('/annotate/job', method='GET')
def create_annotation_job_request():
  pass


'''
*******************************************************************************
List all annotations for the user
*******************************************************************************
'''
@route('/annotations', method='GET', name="annotations_list")
def get_annotations_list():
  pass


'''
*******************************************************************************
Display details of a specific annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>', method='GET', name="annotation_details")
def get_annotation_details(job_id):
  pass


'''
*******************************************************************************
Display the log file for an annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>/log', method='GET', name="annotation_log")
def view_annotation_log(job_id):
  pass


### EOF
