const logsEl = document.getElementById('logs');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');

function getFormData() {
  const cities = Array.from(document.querySelectorAll('input[name="cities"]:checked')).map(x => x.value);
  const mode = document.querySelector('input[name="mode"]:checked').value;
  const headless = document.getElementById('headless').checked;
  const pages = parseInt(document.getElementById('pages').value || '50', 10);
  const include_pdp = document.getElementById('include_pdp').checked;
  return { cities, mode, headless, pages, include_pdp };
}

let evtSource = null;

async function startRun() {
  const payload = getFormData();
  const res = await fetch('/api/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const data = await res.json();
  if (!data.ok) {
    alert('Failed to start: ' + (data.error || 'unknown error'));
    return;
  }
  attachLogs();
}

async function stopRun() {
  await fetch('/api/stop', { method: 'POST' });
  if (evtSource) { evtSource.close(); evtSource = null; }
}

function attachLogs() {
  if (evtSource) evtSource.close();
  evtSource = new EventSource('/api/logs');
  evtSource.onmessage = (e) => {
    logsEl.textContent += e.data + '\n';
    logsEl.scrollTop = logsEl.scrollHeight;
  };
}

startBtn.addEventListener('click', startRun);
stopBtn.addEventListener('click', stopRun);

// Auto-attach logs on load
attachLogs();

