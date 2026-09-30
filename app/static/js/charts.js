/**
 * Chart.js Visualizations for Dashboard and Reports
 */

const PALETTE = [
    '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4',
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#64748b',
    '#3b82f6', '#84cc16'
];

function initDashboardCharts(month, year) {
    const url = `/api/dashboard-charts?month=${month || ''}&year=${year || ''}`;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            renderCategoryChart(data.category_chart);
            renderTrendChart(data.trend_chart);
            if (document.getElementById('budgetBarChart')) {
                renderBudgetChart(data.budget_chart);
            }
        })
        .catch(err => console.error('Error loading dashboard chart data:', err));
}

function renderCategoryChart(catData) {
    const ctx = document.getElementById('categoryDoughnutChart');
    if (!ctx) return;

    if (!catData || !catData.labels || catData.labels.length === 0) {
        ctx.parentElement.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-pie-chart display-4 d-block mb-2 opacity-50"></i>
                <p>No expense data recorded for this period.</p>
            </div>
        `;
        return;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: catData.labels,
            datasets: [{
                data: catData.data,
                backgroundColor: PALETTE.slice(0, catData.labels.length),
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw || 0;
                            return ` ₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

function renderTrendChart(trendData) {
    const ctx = document.getElementById('trendLineChart');
    if (!ctx) return;

    if (!trendData || !trendData.labels || trendData.labels.length === 0) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trendData.labels,
            datasets: [
                {
                    label: 'Income (₹)',
                    data: trendData.income,
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderColor: '#10b981',
                    borderRadius: 6,
                    borderWidth: 1
                },
                {
                    label: 'Expenses (₹)',
                    data: trendData.expenses,
                    backgroundColor: 'rgba(239, 68, 68, 0.85)',
                    borderColor: '#ef4444',
                    borderRadius: 6,
                    borderWidth: 1
                },
                {
                    label: 'Net Savings (₹)',
                    data: trendData.savings,
                    type: 'line',
                    borderColor: '#4f46e5',
                    backgroundColor: '#4f46e5',
                    borderWidth: 3,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${(context.raw || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                        }
                    }
                }
            }
        }
    });
}

function renderBudgetChart(budgetData) {
    const ctx = document.getElementById('budgetBarChart');
    if (!ctx) return;

    if (!budgetData || !budgetData.labels || budgetData.labels.length === 0) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: budgetData.labels,
            datasets: [
                {
                    label: 'Budget Limit (₹)',
                    data: budgetData.budget,
                    backgroundColor: 'rgba(79, 70, 229, 0.25)',
                    borderColor: '#4f46e5',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Actual Spent (₹)',
                    data: budgetData.spent,
                    backgroundColor: budgetData.spent.map((s, idx) => 
                        s > budgetData.budget[idx] ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)'
                    ),
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${(context.raw || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                        }
                    }
                }
            }
        }
    });
}
