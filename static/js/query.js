import { API } from './api.js';
import { STATE } from './config.js';
import { UI } from './ui.js';

export const Query = {
    async executeQuery() {
        const query = document.getElementById('sql-editor').value.trim();
        if (!query || !STATE.isRealDatabase) return;

        try {
            const res = await API.executeQuery(query, STATE.savedConnection?.connection_string);

            if (res.error) {
                UI.renderErrorMessage(res.error);
                return;
            }

            if (res.type === "SELECT") {
                const cols = res.columns;
                const vals = res.rows.map(r => cols.map(c => r[c]));
                UI.renderTableResult({ columns: cols, values: vals }, "");
            } else {
                UI.renderSuccessMessage("Success", res.affected_rows, "");
            }
        } catch (e) {
            UI.renderErrorMessage(e.message);
        }
    }
};
