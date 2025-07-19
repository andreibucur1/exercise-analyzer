const form  = document.getElementById('uploadForm')

form.addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(form);

    const fileInput = form.querySelector('input[type="file"]');

 

    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {


            sessionStorage.setItem('analysisMark', data.mark);
            sessionStorage.setItem('analysisMessage', data.message);
            window.location.href = 'results';




        } else {
            alert('Error uploading video: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the video.');
    });
});