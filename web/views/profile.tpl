%include('views/header.tpl')

<div class="container">
        <div class="page-header">
                <h2>{{auth.current_user.username}} Profile</h2>
        </div>
	<hr />
	<div class="user-info">
		<p><strong>Full Name: </strong>{{auth.current_user.description}}</p>
		<p><strong>Username: </strong>{{auth.current_user.username}}</p>
	% if auth.current_user.role == 'free_user':
		<p><strong>You are currently a free user.</strong></p>
	</div>
	<div class="form-actions">
        	<form action="{{get_url('subscribe')}}">
                        <input class="btn btn-lg btn-primary" type="submit" value="Upgrade to Premium" />
                </form>
	</div>
	% else:
		<p><strong>You are currently a premium user.</strong></p>
	</div>
	% end
</div> <!-- container -->

%rebase('views/base', title='GAS - User Profile')
