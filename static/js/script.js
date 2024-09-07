const socket = io();

// Handle incoming messages
socket.on('message', function (msg) {
    // Assuming msg is a JSON string
    const data = JSON.parse(msg);

    // Update the weather information with received data
    document.querySelector('#weather_wrapper .temp').textContent = data.temp + '°';
    document.querySelector('#weather_wrapper .humidity').textContent = data.humidity + ' %';
    document.querySelector('#weather_wrapper .carbon').textContent = data.carbon + ' ppm';
    document.querySelector('#weather_wrapper .conditions').textContent = data.node;
});

function sendMessage() {
    const message = document.getElementById('message').value;
    socket.send(message);  // Send message to the server
    document.getElementById('message').value = '';  // Clear input
}

// Example of emitting a custom event
socket.emit('custom_event', { data: 'Hello, server!' });

socket.on('response_event', function (data) {
    console.log(data.response);
});