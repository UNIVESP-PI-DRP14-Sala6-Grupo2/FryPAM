document.addEventListener('DOMContentLoaded', function() {
    var loginModal = document.getElementById('loginModal');
    if (loginModal) {
        var myModal = new bootstrap.Modal(loginModal, {
            backdrop: 'static',
            keyboard: false
        });
        myModal.show();
    }
});
