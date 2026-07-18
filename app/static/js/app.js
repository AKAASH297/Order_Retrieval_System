/**
 * Order Portal - Client-side JavaScript
 * Handles "Get Orders" AJAX, delete confirmations, and flash message auto-dismiss.
 */
(function () {
    'use strict';

    // ===== GET ORDERS =====
    const getOrdersBtn = document.getElementById('get-orders-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const ordersTableContainer = document.getElementById('orders-table-container');
    const tableWrapper = document.getElementById('table-wrapper');
    const resultsInfo = document.getElementById('results-info');

    if (getOrdersBtn) {
        getOrdersBtn.addEventListener('click', function () {
            // Show loading, hide previous results and errors
            loadingSpinner.style.display = 'flex';
            errorMessage.style.display = 'none';
            ordersTableContainer.style.display = 'none';

            fetch('/orders/fetch')
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { status: response.status, data: data };
                    });
                })
                .then(function (result) {
                    loadingSpinner.style.display = 'none';

                    if (result.data.error) {
                        errorText.textContent = result.data.error;
                        errorMessage.style.display = 'flex';
                        return;
                    }

                    if (result.data.columns && result.data.rows) {
                        buildTable(result.data.columns, result.data.rows);
                    }
                })
                .catch(function (err) {
                    loadingSpinner.style.display = 'none';
                    errorText.textContent = 'An unexpected error occurred. Please try again.';
                    errorMessage.style.display = 'flex';
                });
        });
    }

    /**
     * Build an HTML table from column names and row data, then insert into the DOM.
     */
    function buildTable(columns, rows) {
        var html = '<table class="data-table">';

        // Header
        html += '<thead><tr>';
        for (var i = 0; i < columns.length; i++) {
            html += '<th>' + escapeHtml(columns[i]) + '</th>';
        }
        html += '</tr></thead>';

        // Body
        html += '<tbody>';
        for (var r = 0; r < rows.length; r++) {
            html += '<tr>';
            for (var c = 0; c < rows[r].length; c++) {
                var val = rows[r][c];
                if (val === null || val === undefined) {
                    html += '<td></td>';
                } else {
                    html += '<td>' + escapeHtml(String(val)) + '</td>';
                }
            }
            html += '</tr>';
        }
        html += '</tbody>';

        html += '</table>';

        tableWrapper.innerHTML = html;
        resultsInfo.textContent = 'Showing ' + rows.length + ' order(s)';
        ordersTableContainer.style.display = 'block';
    }

    /**
     * Escape HTML special characters to prevent XSS.
     */
    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // ===== FLASH MESSAGE AUTO-DISMISS =====
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.classList.add('flash-fade-out');
            setTimeout(function () {
                if (msg.parentElement) {
                    msg.remove();
                }
            }, 400);
        }, 5000);
    });

})();
