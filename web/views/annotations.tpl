%include('views/header.tpl')
% import time

<div class="container">

	<div class="page-header">
  		<h2>My Annotations</h2>
	</div>
	<div class="form-actions">
		<form action="/annotate">
        		<input class="btn btn-lg btn-primary" type="submit" value="Request New Annotation" />
        	</form>
	</div>
	<br></br>
	<div class="ann-requests">
		<table class="table table-bordered">
			<thead>
				<tr>
					<th>Request ID</th>
					<th>Request Time</th>
					<th>VCF File Name</th>
					<th>Status</th>
				</tr>
			</thead>
			% for item in items:
			%   submit_time = time.ctime(item['submit_time'])
			%   job_id = item['job_id']
			<tbody>
				<tr>
					<td><a href="/annotations/{{job_id}}">{{job_id}}</a></td>
					<td>{{submit_time}}</td>
					<td>{{item['input_file_name']}}</td>
					<td>{{item['job_status']}}</td>
				</tr>
			</tbody>
			% end
		</table>
	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - My Annotations')
