# web_server.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Configures the web application and starts the WSGI server
#
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import os
import sys
from bottle import app, SimpleTemplate, run
from bottle import ServerAdapter, server_names
from beaker.middleware import SessionMiddleware

'''
*******************************************************************************
Configure CherryPy WSGI server (cheroot) to replace the default Bottle server
*******************************************************************************
'''
class SSLWebServer(ServerAdapter):
	def run(self, handler):
		from cheroot import wsgi
		from cheroot.ssl.pyopenssl import pyOpenSSLAdapter

		server = wsgi.WSGIServer((self.host, self.port), handler)
		server.ssl_adapter = pyOpenSSLAdapter(certificate="ucmpcs.org.crt",
    	                                    private_key="ucmpcs.org.key")

		try:
			print "Starting secure web application server using CherryPy..."
			server.start()
		except:
			print "Received STOP (or failed to start secure server!)..."
			server.stop()


'''
*******************************************************************************
Configure application
*******************************************************************************
'''
def config_app(app):
	# Load application configuration
 	config_path = os.path.dirname(os.path.abspath(__file__))
	app.config.load_config(config_path + '/' + 'mpcs.conf')

	# Add environment variable-based settings
	app.config['mpcs.env.host'] = os.environ['MPCS_APP_HOST']
	app.config['mpcs.env.port'] = os.environ['MPCS_APP_PORT']
	app.config['mpcs.env.static_root'] = os.environ['MPCS_STATIC_ROOT']
	app.config['mpcs.env.logs_root'] = os.environ['MPCS_LOGS_ROOT']
	app.config['mpcs.env.log_file'] = os.environ['MPCS_LOG_FILE']
	app.config['mpcs.env.templates'] = os.environ['MPCS_TEMPLATES_ROOT']
	app.config['mpcs.env.debug'] = False or os.environ['MPCS_DEBUG']

	return (app)


'''
*******************************************************************************
Main
*******************************************************************************
'''
if __name__ == '__main__':

	# Create a Bootle app instance
	app = app() 

	# Set app configuration
	app = config_app(app)

	# Enable get_url function to be used inside templates to lookup static files
	SimpleTemplate.defaults['get_url'] = app.get_url
	SimpleTemplate.defaults['debug'] = app.config['mpcs.env.debug']

	# Import the application routes (controllers)
	import mpcs_app

	# Add session middleware to the Bottle app
	session_options = {'session.type': 'cookie',
										 'session.cookie_expires': True,
										 'session.timeout': app.config['mpcs.session.timeout'],
										 'session.encrypt_key': app.config['mpcs.session.encrypt_key'],
										 'session.validate_key': app.config['mpcs.session.validate_key'],
										 'session.httponly': True}
	# NOTE: After wrapping the Bottle app in SessionMiddleware, use app.wrap_app to
	# access any of the Bottle objects such as "config"
	app = SessionMiddleware(app, session_options)

	# Start WSGI server; uses default Bootle server - change this for production use
	server_names['sslwebserver'] = SSLWebServer
	run(app=app,
			host=app.wrap_app.config['mpcs.env.host'],
			port=app.wrap_app.config['mpcs.env.port'],
			debug=app.wrap_app.config['mpcs.env.debug'],
			reloader=True,
			server="sslwebserver")


### EOF