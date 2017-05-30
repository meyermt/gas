<!--
login.tpl - Attempts to log user into the GAS
NOTE: On failure, no error messages are displayed
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h2>Login</h2>
	</div>

	<div class="form-wrapper">
    <form role="form" action="{{get_url('login_submit')}}" method="post" name="login_submit">
        <div class="row">
	        <div class="form-group col-md-4">
	            <label for="username">Username</label>
	            <input class="form-control input-lg" type="text" name="username" id="username" 
	              placeholder="Enter your GAS username" />
	        </div>
        </div>
        <div class="row">
	        <div class="form-group col-md-4">
	            <label for="password">Password</label>
	            <small><a class="pull-right" href="#">forgot password?</a></small>
	            <input class="form-control input-lg" type="password" name="password" id="password" 
	              placeholder="Enter your password" />
	        </div>
        </div>
        
        <input type="hidden" name="redirect_url" value="{{redirect_url}}" />
        
        <br />
        <div class="form-actions">        
            <input class="btn btn-lg btn-primary" type="submit" value="Login" />&nbsp;&nbsp;&nbsp;
        </div>
    </form>

		<div class="row">
			<hr />
			Don't have a GAS account? <a href="{{get_url('register')}}"><strong>Register now!</strong></a>
		</div>
  </div>
</div> <!-- container -->

%rebase('views/base', title='GAS - Login')
