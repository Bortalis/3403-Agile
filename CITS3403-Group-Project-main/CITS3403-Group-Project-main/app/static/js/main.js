// app/static/js/main.js

// 1) Wait for DOM
document.addEventListener('DOMContentLoaded', () => {
  attachLoginFormValidation();
  attachCsvUploadHandler();
  renderMiniCharts();
});

// 2) Simple login‐form check
function attachLoginFormValidation() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const email = form.username.value.trim();
    const pw = form.password.value.trim();
    if (!email || !pw) {
      e.preventDefault();
      showAlert('Email & password are required', 'warning');
    }
  });
}

// 3) AJAX CSV upload
function attachCsvUploadHandler() {
  const form = document.getElementById('csv-upload-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
      showAlert('Please select a CSV file first', 'warning');
      return;
    }

    const data = new FormData();
    data.append('file', fileInput.files[0]);

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        body: data,
      });
      if (!res.ok) throw new Error(await res.text());
      showAlert('CSV imported successfully!', 'success');
      // you could trigger a partial reload of the table here
    } catch (err) {
      showAlert(`Upload failed: ${err.message}`, 'danger');
    }
  });
}

// 4) Flash‐style alerts (Bootstrap 5)
function showAlert(message, type = 'info') {
  const container = document.getElementById('alert-container');
  const div = document.createElement('div');
  div.className = `alert alert-${type} alert-dismissible fade show`;
  div.role = 'alert';
  div.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  container.prepend(div);
  // auto‐dismiss after 5s
  setTimeout(() => div.classList.remove('show'), 5000);
}

// 5) Chart.js dynamic rendering
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

function renderMiniCharts() {
  // line
  const lineEl = document.getElementById('lineChart');
  if (lineEl && window.lineData) {
    new Chart(lineEl.getContext('2d'), {
      type: 'line',
      data: window.lineData,
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' }
        }
      }
    });
  }

  // pie
  const pieEl = document.getElementById('pieChart');
  if (pieEl && window.pieData) {
    new Chart(pieEl.getContext('2d'), {
      type: 'pie',
      data: window.pieData,
      options: { responsive: true }
    });
  }
}

// 6) Helper to pull our CSRF token from <meta>
function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]').content;
}
