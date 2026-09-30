/**
 * Main Application Client Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (sidebarToggle && sidebar && backdrop) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            backdrop.classList.toggle('show');
        });

        backdrop.addEventListener('click', () => {
            sidebar.classList.remove('show');
            backdrop.classList.remove('show');
        });
    }

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // 3. Edit Modals Pre-fill Helpers
    // Incomes
    document.querySelectorAll('.btn-edit-income').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const title = btn.getAttribute('data-title');
            const amount = btn.getAttribute('data-amount');
            const source = btn.getAttribute('data-source');
            const date = btn.getAttribute('data-date');
            const notes = btn.getAttribute('data-notes');
            const isRecurring = btn.getAttribute('data-recurring') === 'True';

            const form = document.getElementById('editIncomeForm');
            if (form) {
                form.action = `/income/edit/${id}`;
                document.getElementById('edit_income_title').value = title;
                document.getElementById('edit_income_amount').value = amount;
                document.getElementById('edit_income_source').value = source;
                document.getElementById('edit_income_date').value = date;
                document.getElementById('edit_income_notes').value = notes || '';
                document.getElementById('edit_income_recurring').checked = isRecurring;
            }
        });
    });

    // Expenses
    document.querySelectorAll('.btn-edit-expense').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const title = btn.getAttribute('data-title');
            const amount = btn.getAttribute('data-amount');
            const category = btn.getAttribute('data-category');
            const paymentMethod = btn.getAttribute('data-payment');
            const date = btn.getAttribute('data-date');
            const notes = btn.getAttribute('data-notes');

            const form = document.getElementById('editExpenseForm');
            if (form) {
                form.action = `/expenses/edit/${id}`;
                document.getElementById('edit_expense_title').value = title;
                document.getElementById('edit_expense_amount').value = amount;
                document.getElementById('edit_expense_category').value = category;
                document.getElementById('edit_expense_payment').value = paymentMethod;
                document.getElementById('edit_expense_date').value = date;
                document.getElementById('edit_expense_notes').value = notes || '';
            }
        });
    });

    // Goals Edit
    document.querySelectorAll('.btn-edit-goal').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const title = btn.getAttribute('data-title');
            const target = btn.getAttribute('data-target');
            const current = btn.getAttribute('data-current');
            const category = btn.getAttribute('data-category');
            const deadline = btn.getAttribute('data-deadline');
            const notes = btn.getAttribute('data-notes');

            const form = document.getElementById('editGoalForm');
            if (form) {
                form.action = `/goals/edit/${id}`;
                document.getElementById('edit_goal_title').value = title;
                document.getElementById('edit_goal_target').value = target;
                document.getElementById('edit_goal_current').value = current;
                document.getElementById('edit_goal_category').value = category;
                document.getElementById('edit_goal_deadline').value = deadline;
                document.getElementById('edit_goal_notes').value = notes || '';
            }
        });
    });

    // Goals Contribute Modal
    document.querySelectorAll('.btn-contribute-goal').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const title = btn.getAttribute('data-title');
            const remaining = btn.getAttribute('data-remaining');

            const form = document.getElementById('contributeGoalForm');
            if (form) {
                form.action = `/goals/contribute/${id}`;
                document.getElementById('contribute_goal_title_text').textContent = title;
                document.getElementById('contribute_goal_remaining_text').textContent = `₹${parseFloat(remaining).toLocaleString('en-IN')}`;
            }
        });
    });
});
