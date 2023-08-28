window.addEventListener('DOMContentLoaded', event => {
    const customerDataTable = document.getElementById('customerDataTable');
    if (customerDataTable) {
        new simpleDatatables.DataTable(customerDataTable);
    }
});
