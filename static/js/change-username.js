const loginForm = document.getElementById('Form');
const oldusername = document.getElementById('oldusername');
const newusername = document.getElementById('newusername');
const password = document.getElementById('password');


loginForm.addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(loginForm);

    fetch('/change-username', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/';
        } else {
            alert('Try again: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while logging in.');
    });
});
