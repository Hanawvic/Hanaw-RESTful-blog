$(document).ready(function() {
    $('#contactForm').submit(function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: "/publish", // access the variable here
            data: $(this).serialize(),
            dataType: 'json',
            success: function(data) {
                if (data.error) {
                    $('#errorMessage').text(data.error);
                    $('#errorAlert').removeClass('d-none');
                    $('#successAlert').addClass('d-none');
                } else {
                    $('#successMessage').text(data.success);
                    $('#successAlert').removeClass('d-none');
                    $('#errorAlert').addClass('d-none');
                }
            },
            error: function() {
                $('#errorMessage').text('An error occurred while publishing the post. Please try again later.');
                $('#errorAlert').removeClass('d-none');
                $('#successAlert').addClass('d-none');
            }
        });
    });
});