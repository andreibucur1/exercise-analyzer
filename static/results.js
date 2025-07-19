window.addEventListener('DOMContentLoaded', function() {

    const urlParams = new URLSearchParams(window.location.search);
    const mark = urlParams.get('mark');
    const message = urlParams.get('message');
    

    const storedMark = mark || sessionStorage.getItem('analysisMark');
    const storedMessage = message || sessionStorage.getItem('analysisMessage');
    
    if (storedMark && storedMessage) {
        setTimeout(() => {
            showResults(parseFloat(storedMark), storedMessage);
            // Clear stored data
            sessionStorage.removeItem('analysisMark');
            sessionStorage.removeItem('analysisMessage');
        }, 1500);
    } else {
        // No results found, redirect back to upload after 3 seconds
        setTimeout(() => {
            document.getElementById('loading').innerHTML = 
                '<div class="loading-text">No analysis data found. Redirecting...</div>';
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }, 1000);
    }
});

function showResults(mark, message) {

    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    

    const scoreValue = document.getElementById('scoreValue');
    scoreValue.textContent = mark.toFixed(1);
    

    const scoreCircle = document.getElementById('scoreCircle');
    if (mark >= 8) {
        scoreCircle.className = 'score-circle score-excellent';
    } else if (mark >= 5) {
        scoreCircle.className = 'score-circle score-good';
    } else {
        scoreCircle.className = 'score-circle score-poor';
    }
    

    document.getElementById('statScore').textContent = mark.toFixed(1);
    document.getElementById('statAccuracy').textContent = Math.round((mark/10) * 100) + '%';
    

    let grade;
    if (mark >= 8) {
        grade = 'A';
    } else if (mark >= 6) {
        grade = 'B';
    } else if (mark >= 4) {
        grade = 'C';
    } else {
        grade = 'D';
    }
    document.getElementById('statGrade').textContent = grade;

    document.getElementById('feedbackMessage').textContent = message;
}

