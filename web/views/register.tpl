<!--
register.tpl - Gets new user details and submits registration request
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
  	<h2>Register</h2>
  </div>

    %if alert:

    	%if success:
		    <div class="alert alert-success">
		      <strong>Thanks for signing up!</strong><br />
		      Please look for an e-mail to confirm your registration.
		    </div>
		   %else:
		    <div class="alert alert-danger">
		      <strong>Registration failed.</strong><br />
		      Error message received: {{error_message}}
		    </div>
		  %end

	  %else:
		
			<p>Please provide the information below to register.</p>

	    <div class="form-wrapper">
		    <form role="form" action="{{get_url('register_submit')}}" method="post" name="register_submit">

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="name">Name</label>
		                <input class="form-control input-lg required" type="text" name="name" id="name" 
		                  value="{{name}}" placeholder="Enter your full name" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="email_address">E-mail Address</label>
		                <input class="form-control input-lg required" type="text" name="email_address" id="email_address" 
		                  value="{{email}}" placeholder="Enter your e-mail address" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-4">
			            <label for="name">Username</label>
		                <input class="form-control input-lg required" type="text" name="username" id="username" 
		                  value="{{username}}" placeholder="Enter a username" />
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-4">
			            <label for="password">Password</label>
		                <input class="form-control input-lg password required" type="password" name="password" id="password" placeholder="Enter a password" />
		            </div>
		        </div>		        		        

		        <br />
		        <div class="form-actions">
		            <input class="btn btn-lg btn-primary" type="submit" value="Register" />
		        </div>        
		    </form>
	    </div>
		%end

</div> <!-- container -->

%rebase('views/base', title='GAS - Register')
