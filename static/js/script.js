document.addEventListener('DOMContentLoaded', function() {
    fetch('/status')
    .then(response => response.json())
    .then(data => {
        document.getElementById('miner-status').textContent = `Miner is ${data.status}`;
    })
    .catch(error => console.error('Error fetching status:', error));
    fetchSettings();
});

function fetchSettings() {
    fetch('/settings')
    .then(response => response.json())
    .then(data => {
        document.getElementById('before').value = data.do_not_mine_before;
        document.getElementById('after').value = data.do_not_mine_after;
        document.getElementById('maxTime').value = data.max_switch_time_milli;
    });
}

function updateSettings() {
    const settings = {
        do_not_mine_before: parseInt(document.getElementById('before').value),
        do_not_mine_after: parseInt(document.getElementById('after').value),
        max_switch_time_milli: parseInt(document.getElementById('maxTime').value)
    };

    fetch('/settings', {
        method: 'PUT', // or 'POST'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        alert('Settings updated successfully!');
        fetchSettings(); // Refresh settings fields to show updated values
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while updating the settings.');
    });
}