

$(document).ready(function () {

});

function onSignupClick() {
    let data =  {
        username: $('#inputUsername').val(),
        password: $('#inputPassword').val(),
        email: $('#inputEmail').val()
    };
    if (data.username === '' || data.password === '' || data.email === '')
        return;

    $.ajax({
        url: 'signup',
        method: 'POST',
        contentType: 'json',
        dataType: 'json',
        data: JSON.stringify(data),
        success: function(e) {
            if (e.result === 'success') {
                window.location.href="usercenter"
            } else {
                console.log(e.msg);
                $("#toast-body").html(e.msg);
                $('.toast').toast('show');
            }
        },
        error: function (e) {
            console.log(e);
        }
    })
}