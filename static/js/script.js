// Connect to the MQTT broker
const client = mqtt.connect('ws://13.214.222.110:9001');

// Handle successful connection
client.on('connect', function () {
    console.log('Connected to MQTT broker');
    client.subscribe('iot/message', function (err) {
        if (!err) {
            console.log('Subscribed to topic "iot/message"');
        } else {
            console.error('Subscription error:', err);
        }
    });
});

// Handle incoming messages
client.on('message', function (topic, message) {
    // Assuming message is a JSON string
    try {
        const data = JSON.parse(message.toString());

        const temp = data.temp;
        const tempElement = document.querySelector('#weather_wrapper .temp');
        const humidityElement = document.querySelector('#weather_wrapper .humidity');
        const carbonElement = document.querySelector('#weather_wrapper .carbon');
        const conditionsElement = document.querySelector('#weather_wrapper .conditions');
        if (tempElement) {
            tempElement.textContent = data.temp + '°';
        }
        if (humidityElement) {
            humidityElement.textContent = data.humidity + ' %';
        }
        if (carbonElement) {
            carbonElement.textContent = data.carbon + ' ppm';
        }
        if (conditionsElement) {
            conditionsElement.textContent = data.node;
        }

        // Update temperature status
        const tempStatus = document.getElementById('tempStatus');
        const tempMessage = document.getElementById('tempMessage');
        if (temp < 10) {
            tempStatus.textContent = 'Cold';
            tempMessage.textContent = 'အေးခဲသည်၊၊';
            tempStatus.className = 'badge badge-info';
        } else if (temp >= 10 && temp < 17) {
            tempStatus.textContent = 'Cool';
            tempMessage.textContent = 'အေးမြသည်၊၊';
            tempStatus.className = 'badge badge-primary';
        } else if (temp >= 17 && temp < 30) {
            tempStatus.textContent = 'Warm';
            tempMessage.textContent = 'နွေးထွေးသည်။';
            tempStatus.className = 'badge badge-warning';
        } else if (temp >= 30 && temp < 35) {
            tempStatus.textContent = 'Hot';
            tempMessage.textContent = 'ပူသည်။';
            tempStatus.className = 'badge badge-danger';
        } else if (temp >= 35 && temp < 40) {
            tempStatus.textContent = 'Very hot';
            tempMessage.textContent = 'အလွန်ပူသည်။';
            tempStatus.className = 'badge badge-danger';
        } else if (temp >= 40 && temp < 45) {
            tempStatus.textContent = 'Extreme hot';
            tempMessage.textContent = 'အလွန်အမင်းပူနေသည်။';
            tempStatus.className = 'badge badge-danger';
        } else if (temp >= 45) {
            tempStatus.textContent = 'Lethal heat';
            tempMessage.textContent = 'သေနိုင်လောက်သောအပူဖြစ်သည်။';
            tempStatus.className = 'badge badge-dark';
        }

        // Update humidity status
        const humidity = data.humidity;
        const humidityStatus = document.getElementById('humidityStatus');
        const humidityMessage = document.getElementById('humidityMessage');
        if (humidity < 25) {
            humidityStatus.textContent = 'Poor low humidity levels';
            humidityMessage.textContent = 'စိုထိုင်းဆနိမ့်သောအဆင့်ဖြစ်သည်၊၊';
            humidityStatus.className = 'badge badge-danger';
        } else if (humidity >= 25 && humidity < 30) {
            humidityStatus.textContent = 'Fair';
            humidityMessage.textContent = 'စိုထိုင်းဆ သင့်တင့်သည်၊၊';
            humidityStatus.className = 'badge badge-warning';
        } else if (humidity >= 30 && humidity < 60) {
            humidityStatus.textContent = 'Healthy levels';
            humidityMessage.textContent = 'ကျန်းမာစေသောအဆင့်ဖြစ်သည်။';
            humidityStatus.className = 'badge badge-success';
        } else if (humidity >= 60 && humidity < 70) {
            humidityStatus.textContent = 'Fair';
            humidityMessage.textContent = 'စိုထိုင်းဆ သင့်တင့်သည်၊၊';
            humidityStatus.className = 'badge badge-warning';
        } else if (humidity >= 70) {
            humidityStatus.textContent = 'Poor high humidity levels';
            humidityMessage.textContent = 'စိုထိုင်းဆမြင့်သောအဆင့်ဖြစ်သည်၊၊';
            humidityStatus.className = 'badge badge-danger';
        }

        // Update the carbon status
        const carbon = data.carbon;
        const carbonStatus = document.getElementById('carbonStatus');
        const carbonMessage = document.getElementById('carbonMessage');
        if (carbon < 350) {
            carbonStatus.textContent = 'Healthy outside air level';
            carbonMessage.textContent = 'ကျန်းမာသောပြင်ပလေထုအဆင့်။';
            carbonStatus.className = 'badge badge-success';
        } else if (carbon >= 350 && carbon < 600) {
            carbonStatus.textContent = 'Healthy indoor air level';
            carbonMessage.textContent = 'ကျန်းမာသောအိမ်တွင်းလေထုအဆင့်။';
            carbonStatus.className = 'badge badge-success';
        } else if (carbon >= 600 && carbon < 800) {
            carbonStatus.textContent = 'Acceptable level';
            carbonMessage.textContent = 'လက်ခံနိုင်သောလေထုအဆင့်။';
            carbonStatus.className = 'badge badge-warning';
        } else if (carbon >= 800 && carbon < 1000) {
            carbonStatus.textContent = 'Ventilation required';
            carbonMessage.textContent = 'လေဝင်လေထွက်လိုအပ်သောအခြေအနေ။';
            carbonStatus.className = 'badge badge-warning';
        } else if (carbon >= 1000 && carbon < 1200) {
            carbonStatus.textContent = 'Ventilation necessary';
            carbonMessage.textContent = 'လေဝင်လေထွက်မဖြစ်မနေလိုအပ်။';
            carbonStatus.className = 'badge badge-danger';
        } else if (carbon >= 1200 && carbon < 2000) {
            carbonStatus.textContent = 'Negative health effects';
            carbonMessage.textContent = 'အနုတ်လက္ခဏာကျန်းမာရေးသက်ရောက်မှု။';
            carbonStatus.className = 'badge badge-danger';
        } else if (carbon >= 2000 && carbon < 5000) {
            carbonStatus.textContent = 'Hazardous prolonged exposure';
            carbonMessage.textContent = 'ကြာရှည်နေလျှင် အန္တရာယ်ရှိသောအခြေအနေ။';
            carbonStatus.className = 'badge badge-dark';
        } else if (carbon >= 5000) {
            carbonStatus.textContent = 'Severe hazard';
            carbonMessage.textContent = 'အလွန်အန္တရာယ်ရှိသောအခြေအနေ။';
            carbonStatus.className = 'badge badge-dark';
        }

        // Update value displays
        const tempElement2 = document.getElementById('tempValue');
        const humidityElement2 = document.getElementById('humidityValue');
        const carbonElement2 = document.getElementById('carbonValue');
        if (tempElement2) {
            tempElement2.textContent = data.temp + '°C';
        }
        if (humidityElement2) {
            humidityElement2.textContent = data.humidity + ' %';
        }
        if (carbonElement2) {
            carbonElement2.textContent = data.carbon + ' ppm';
        }

    } catch (error) {
        console.error('Error processing message:', error);
    }
});

function sendMessage() {
    const message = document.getElementById('message').value;
    client.publish('your/topic', message);  // Publish message to the topic
    document.getElementById('message').value = '';  // Clear input
}

// Example of emitting a custom event (using publish instead)
client.publish('custom_event', JSON.stringify({ data: 'Hello, server!' }));

// Close the MQTT connection before the page unloads
window.addEventListener('beforeunload', function () {
    client.end();
});
