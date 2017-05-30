<!--
subscribe.tpl - Get user's credit card details to send to Stripe service
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')
<!-- Captures the user's credit card information and uses Javascript to send to Stripe -->

<div class="container">
	<div class="page-header">
		<h2>Subscribe</h2>
	</div>

	<p>You are subscribing to the GAS Premium plan. Please enter your credit card details to complete your subscription.</p><br />

	<form role="form" action="/subscribe" method="post" id="subscribe_form" name="subscribe_submit" >
		<div class="form-group">
			<label>Name on Credit Card</label>
			<input type="text" class="form-control input-lg required" placeholder="Enter name" data-stripe="name">
		</div>
                <div class="form-group">
                        <label>Credit Card Number</label>
                        <input type="text" class="form-control input-lg required" placeholder="Enter number" data-stripe="number">
                </div>
                <div class="form-group">
                        <label>Credit Card Verification Code</label>
                        <input type="text" class="form-control input-lg required" placeholder="Enter cvc" data-stripe="cvc">
                </div>
                <div class="form-group">
                        <label>Credit Card Expiration Month</label>
                        <input type="text" class="form-control input-lg required" placeholder="Enter month" data-stripe="exp-month">
                </div>
                <div class="form-group">
                        <label>Credit Card Expiration Year</label>
                        <input type="text" class="form-control input-lg required" placeholder="Enter year" data-stripe="exp-year">
                </div>
		<input id="bill-me" class="btn btn-lg btn-primary" type="submit" value="Subscribe">
	</form>

</div> <!-- container -->

%rebase('views/base', title='GAS - Subscribe')
