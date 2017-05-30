%include('views/header.tpl')

<div class="container">
        <div class="page-header">
                <h2>Annotation Details</h2>
        </div>
	<div class="details">
		<p><strong>Request ID: </strong>{{job_id}}</p>
		<p><strong>Request Time: </strong>{{request_time}}</p>
		<p><strong>VCF Input FIle: </strong>{{input_file_name}}</p>
		<p><strong>Status: </strong>{{job_status}}</p>
		<p><strong>Complete Time: </strong>{{complete_time}}</p>
	</div>
	<hr />
	<div class="files">
        % if complete_time != 'N/A':
	%   if auth.current_user.role == 'free_user':
        %     import time
        %     now = int(time.time())
        %     diff = now - int(complete_int)
        %     if diff > 1800:
                <p><strong>Annotated Results File: </strong><a href="{{get_url('subscribe')}}">Upgrade to Premium for download</a></p>
	%     else:
                <p><strong>Annotated Results File: </strong><a href="{{annot_url}}">download</a></p>
        %     end
	%   else:
                <p><strong>Annotated Results File: </strong><a href="{{annot_url}}">download</a></p>
        %   end
                <p><strong>Annotation Log File: </strong><a href="/annotations/{{job_id}}/log">view</a></p>
        % else:
                <p><strong>Annotated Results File: </strong>Job not yet completed</p>
                <p><strong>Annotation Log File: </strong>Job not yet completed</p>
        % end
	</div>
	<hr />
	<p><a href="/annotations"><span class="glyphicon glyphicon-backward"></span> back to annotations list</a></p>
</div> <!-- container -->

%rebase('views/base', title='GAS - Annotation Detail')
