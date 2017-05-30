%include('views/header.tpl')
<style>
.log-detail {
    white-space: pre-wrap;
}
</style>

<div class="container">
        <div class="page-header">
                <h2>Log Details</h2>
        </div>
	<hr />
	<div class="log-detail">
		<p>{{logText}}</p>
	</div>
	<hr />
	<p><a href="/annotations/{{job_id}}">back to annotation details</a></p>
	
</div> <!-- container -->

%rebase('views/base', title='GAS - Log Detail')
