# mpcs_utils.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import logging
from bottle import default_app

app = default_app()

'''
Configure logging infrastructure
'''
log_path=app.config['mpcs.env.logs_root']
log_filename=app.config['mpcs.env.log_file']

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create log file and set logging level for production
file_log = logging.FileHandler(log_path + log_filename, 'a')
file_log.setLevel(logging.INFO)

# Use console for development logging
console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)

# Specify log formatting:
formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(name)s (line %(lineno)s): %(message)s")
file_log.setFormatter(formatter)
console_log.setFormatter(formatter)

# Add console log to logger
log.addHandler(console_log)
log.addHandler(file_log)

# Set up Cork for authentication
import cork
cork_log = logging.getLogger('cork')
cork_log.addHandler(file_log)

# Set up the conenction to the auth database
auth_db = cork.sqlalchemy_backend.SqlAlchemyBackend(
	db_full_url=app.config['mpcs.auth.db_url'],
	users_tname='users', roles_tname='roles', pending_reg_tname='register', initialize=False)

# Instantiate an authn/authz provider
auth = cork.Cork(backend=auth_db,
	email_sender=app.config['mpcs.auth.email_sender'],
	smtp_url=app.config['mpcs.auth.smtp_url'])


### EOF