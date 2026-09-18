export const UI = {
    switchTab(id) {
        document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
        document.getElementById(id).style.display = 'flex';
    },

    updateConnectionStatus(label, connected) {
        const btn = document.getElementById('btn-open-conn-modal');
        btn.innerText = label;
        btn.className = connected ? "text-emerald-400" : "text-rose-400";
    },

    renderTableResult(result, time) {
        const cont = document.getElementById('result-container');
        const cols = result.columns || [];
        const rows = result.values || [];

        let html = '<table class="w-full"><tr>';
        cols.forEach(c => html += `<th class="p-2 border">${c}</th>`);
        html += '</tr>';
        rows.forEach(r => {
            html += '<tr>';
            r.forEach(v => html += `<td class="p-2 border">${v || 'NULL'}</td>`);
            html += '</tr>';
        });
        html += '</table>';
        cont.innerHTML = html;
    },

    renderSuccessMessage(type, count, time) {
        document.getElementById('result-container').innerHTML = `<div class="p-4 text-emerald-400">✅ ${count} rows affected</div>`;
    },

    renderErrorMessage(msg) {
        document.getElementById('result-container').innerHTML = `<div class="p-4 text-rose-400">❌ ${msg}</div>`;
    },

    updateVaultUI(vault, total) {}
};
