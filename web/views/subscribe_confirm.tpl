<!--
subscribe_confirm.tpl - Confirmation that Stripe account was created and user is now Premium
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
  	<h2>Subscription Succeeded</h2>
  </div>

  <p>Thank you for subscribing! You are now a Premium user and have full access to your data that was previously locked up within the GAS (unfairly, we know). Please <a href="/annotations">click here</a> to view your annotation results.</p>

	<p>Your subscriber account number is <strong>{{stripe_id}}</strong>. Please make a note of this since the GAS service doesn't. Yes, we know we should, but at this stage we have your money and credit card details so we don't care much!</p>
  </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Subscription Succeeded')