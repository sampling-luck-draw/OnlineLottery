

$(document).ready(function () {

});

function onSignupClick() {
    let data =  {
        username: $('#inputEmail').val(),
        password: $('#inputPassword').val(),
    };
    if (data.username === '' || data.password === '')
        return;

    $.ajax({
        url: 'signin',
        method: 'POST',
        contentType: 'json',
        dataType: 'json',
        data: JSON.stringify(data),
        success: function(e) {
            if (e.result === 'success') {
                window.location.href="usercenter"
            } else {
                console.log(e.msg);
                let q = $("#signin-fail");
                q.html(e.msg);
                q.show();
                $("#toast-body").html(e.msg);
                $('.toast').toast('show');
            }
        },
        error: function (e) {
            console.log(e);
        }
    })
}