/**
  * lab.js - Live telemetry polling
  */
document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // TELEMETRY DIALS POLLING
    // -------------------------------------------------------------
    const cpuDial = document.getElementById('cpu-dial');
    const cpuVal = document.getElementById('cpu-val');
    const memoryDial = document.getElementById('memory-dial');
    const memoryVal = document.getElementById('memory-val');
    const networkDial = document.getElementById('network-dial');
    const networkVal = document.getElementById('network-val');
    const activeConnections = document.getElementById('active-connections');
    const dbRecords = document.getElementById('db-records');

    const statusDot = document.getElementById('system-status-dot');
    const statusText = document.getElementById('system-status-text');

    function updateDial(dialElement, value, color) {
        if (!dialElement) return;
        // Apply conic gradient based on percent
        dialElement.style.background = `conic-gradient(${color} 0%, ${color} ${value}%, rgba(0, 0, 0, 0.05) ${value}%, rgba(0, 0, 0, 0.05) 100%)`;
    }

    function fetchTelemetry() {
        fetch('/api/stats')
            .then(res => {
                if (!res.ok) throw new Error('Gateway Offline');
                return res.json();
            })
            .then(data => {
                // Update text values
                if (cpuVal) cpuVal.textContent = data.total_fill_rate.toFixed(1);
                if (memoryVal) memoryVal.textContent = data.popular_fill_rate.toFixed(1);
                if (networkVal) networkVal.textContent = data.open_workshops;
                if (activeConnections) activeConnections.textContent = data.connections;
                if (dbRecords) dbRecords.textContent = data.db_records;

                // Update dial styles
                updateDial(cpuDial, data.total_fill_rate, '#4285f4');
                updateDial(memoryDial, data.popular_fill_rate, '#107c91');
                updateDial(networkDial, (data.open_workshops / 7) * 100, '#f9ab00'); // scale of 7 workshops total

                // System Status Header
                if (statusDot && statusText) {
                    statusDot.style.backgroundColor = '#34a853';
                    statusDot.style.boxShadow = '0 0 8px #34a853';
                    statusDot.style.animation = 'pulse-green 1.5s infinite';
                    statusText.textContent = data.status;
                    statusText.className = 'text-cyan';
                }
            })
            .catch(err => {
                console.error('[ERR] Telemetry sync failure:', err);
                if (statusDot && statusText) {
                    statusDot.style.backgroundColor = '#ff5f56';
                    statusDot.style.boxShadow = '0 0 8px #ff5f56';
                    statusDot.style.animation = 'none';
                    statusText.textContent = 'OFFLINE';
                    statusText.className = 'text-purple';
                }
            });
    }

    // Run first telemetry immediately and set interval for every 2.5 seconds
    fetchTelemetry();
    setInterval(fetchTelemetry, 2500);
});
