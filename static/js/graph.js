document.addEventListener('DOMContentLoaded', function () {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const dates = data.map(item => item.date);
            const temperatures = data.map(item => item.temperature);
            const humidities = data.map(item => item.humidity);
            const carbons = data.map(item => item.carbon);

            // Temperature Chart
            const tempCtx = document.getElementById('temperatureChart').getContext('2d');
            new Chart(tempCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: temperatures,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                color: '#fff' // White color for X-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        },
                        y: {
                            ticks: {
                                color: '#fff' // White color for Y-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff' // White color for legend labels
                            }
                        }
                    }
                }
            });

            // Humidity Chart
            const humidityCtx = document.getElementById('humidityChart').getContext('2d');
            new Chart(humidityCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Humidity (%)',
                        data: humidities,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                color: '#fff' // White color for X-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        },
                        y: {
                            ticks: {
                                color: '#fff' // White color for Y-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff' // White color for legend labels
                            }
                        }
                    }
                }
            });

            // Carbon Chart
            const carbonCtx = document.getElementById('carbonChart').getContext('2d');
            new Chart(carbonCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Carbon Levels (ppm)',
                        data: carbons,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            ticks: {
                                color: '#fff' // White color for X-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        },
                        y: {
                            ticks: {
                                color: '#fff' // White color for Y-axis labels
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.2)' // White grid lines
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff' // White color for legend labels
                            }
                        }
                    }
                }
            });
        });
});
