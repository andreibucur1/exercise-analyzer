function createChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: '2-digit'
    });
}



fetch('/api/exercise-data', {
    method: 'GET',}
)
.then(response => response.json())
.then(data => {
    const bicepData = data.results.filter(result => result.exercise === 'bicepCurl');
    const tricepData = data.results.filter(result => result.exercise === 'tricepExtension');
    const shoulderData = data.results.filter(result => result.exercise === 'lateralRaise');

    if (bicepData.length > 0) {
        const bicepDates = bicepData.map(result => formatDate(result.timestamp));
        createChart('bicepCurlChart', bicepDates, bicepData.map(result => result.mark));
        document.getElementById('bicepCurlAvg').textContent = 
            (bicepData.reduce((sum, r) => sum + r.mark, 0) / bicepData.length).toFixed(1);
        document.getElementById('bicepCurlBest').textContent = 
            Math.max(...bicepData.map(r => r.mark)).toFixed(1);
        document.getElementById('bicepCurlTotal').textContent = 
            bicepData.length;
    }

    if (tricepData.length > 0) {
        const tricepDates = tricepData.map(result => formatDate(result.timestamp));
        createChart('tricepExtensionChart', tricepDates, tricepData.map(result => result.mark));
        document.getElementById('tricepExtensionAvg').textContent = 
            (tricepData.reduce((sum, r) => sum + r.mark, 0) / tricepData.length).toFixed(1);
        document.getElementById('tricepExtensionBest').textContent = 
            Math.max(...tricepData.map(r => r.mark)).toFixed(1);
        document.getElementById('tricepExtensionTotal').textContent = 
            tricepData.length;
    }

    if (shoulderData.length > 0) {
        const shoulderDates = shoulderData.map(result => formatDate(result.timestamp));
        createChart('lateralRaiseChart', shoulderDates, shoulderData.map(result => result.mark));
        document.getElementById('lateralRaiseAvg').textContent = 
            (shoulderData.reduce((sum, r) => sum + r.mark, 0) / shoulderData.length).toFixed(1);
        document.getElementById('lateralRaiseBest').textContent = 
            Math.max(...shoulderData.map(r => r.mark)).toFixed(1);
        document.getElementById('lateralRaiseTotal').textContent = 
            shoulderData.length;
    }
})