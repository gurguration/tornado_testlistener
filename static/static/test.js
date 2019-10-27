$(document).ready(function() {
    $('#reload-button').click(function(event) {
        jQuery.ajax({
            url: '//localhost:8000/',
            type: 'POST',
            dataType: 'json',
            data: {
                action: 'reload',
            },          
            success: function() {
                window.location.reload(true);
            }
        });
    });
});