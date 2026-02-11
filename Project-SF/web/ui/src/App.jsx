import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const API_BASE = "http://localhost:8000";

const App = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/data/device_01?minutes=10`);
            // Sort by time
            const sorted = response.data.sort((a, b) => new Date(a.time) - new Date(b.time));
            setData(sorted);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching data:", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const sendCommand = async (action) => {
        try {
            await axios.post(`${API_BASE}/api/control`, {
                device_id: "device_01",
                component: "fan",
                action: action
            });
            alert(`Command ${action} sent!`);
        } catch (error) {
            console.error("Error sending command:", error);
            alert("Failed to send command");
        }
    };

    const chartData = {
        labels: data.map(d => new Date(d.time).toLocaleTimeString()),
        datasets: [
            {
                label: 'Temperature (°C)',
                data: data.map(d => d.temperature),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
            {
                label: 'Humidity (%)',
                data: data.map(d => d.humidity),
                borderColor: 'rgb(53, 162, 235)',
                backgroundColor: 'rgba(53, 162, 235, 0.5)',
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Device 01 Environment Data',
            },
        },
    };

    return (
        <div className="container">
            <header>
                <h1>IoT Control Dashboard</h1>
            </header>

            <main>
                <section className="card">
                    <h2>Live Monitor</h2>
                    {loading ? <p>Loading...</p> : <Line options={options} data={chartData} />}
                </section>

                <section className="card controls">
                    <h2>Controls</h2>
                    <div className="button-group">
                        <button className="btn on" onClick={() => sendCommand("ON")}>Turn Fan ON</button>
                        <button className="btn off" onClick={() => sendCommand("OFF")}>Turn Fan OFF</button>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default App;
