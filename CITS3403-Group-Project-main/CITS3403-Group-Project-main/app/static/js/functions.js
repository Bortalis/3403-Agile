function renderDashboardCharts(chartLabels, incomeSeries, expenseSeries, categoryLabels, categoryValues) {
  const lineCtx = document.getElementById('lineChart').getContext('2d');
  const pieCtx = document.getElementById('pieChart').getContext('2d');

  // Line Chart: Monthly Income vs Expenses
  new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: chartLabels,
      datasets: [
        {
          label: 'Income',
          data: incomeSeries,
          borderColor: 'green',
          backgroundColor: 'rgba(34,197,94,0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Expense',
          data: expenseSeries,
          borderColor: 'red',
          backgroundColor: 'rgba(239,68,68,0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Monthly Income vs Expenses'
        },
        legend: {
          labels: {
            usePointStyle: true
          }
        }
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45,
            autoSkip: true,
            maxTicksLimit: 6
          },
          title: {
            display: true,
            text: 'Month'
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          },
          title: {
            display: true,
            text: 'Amount'
          }
        }
      }
    }
  });

  // Pie Chart: Expense Breakdown by Category
  new Chart(pieCtx, {
    type: 'pie',
    data: {
      labels: categoryLabels,
      datasets: [{
        label: 'Expenses',
        data: categoryValues,
        backgroundColor: [
          '#f87171', '#facc15', '#4ade80', '#60a5fa',
          '#a78bfa', '#f472b6', '#34d399', '#fb923c',
          '#38bdf8', '#c084fc'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Expense Breakdown by Category'
        }
      }
    }
  });
}
