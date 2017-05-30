<!--
register_confirm.tpl - Confirms new user registration request was received
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">
	<div class="page-header">
  	<h2>Confirm Registration</h2>
  </div>

  %if success:
    <div class="row">
      <p>Thank you for registering! Please <a href="/login">click here</a> to login and start using the GAS.</p>
    </div>
  %else:
    <div class="alert alert-danger">
      <strong>Could not confirm registration.</strong><br />
      Error message received: {{error_message}}
    </div>
  %end

</div> <!-- container -->

%rebase('views/base', title='GAS - Registration Confirmed')
