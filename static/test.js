$(document).ready(function() {
    $('#reload-button').click(function(event) {
        jQuery.ajax({
            url: '//sk3.mygps.ge:8000/',
            type: 'POST',
            dataType: 'json',
            data: {
                action: 'reload',
            },          
            success: function() {
		if (true){
		setTimeout(function(){
                location.reload(true);
		}, 1000);
		}
            }
        });
    });
});
