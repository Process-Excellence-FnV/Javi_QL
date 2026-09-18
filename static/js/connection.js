import { API } from './api.js';
import { STATE } from './config.js';
import { Helpers } from './helpers.js';
import { UI } from './ui.js';

export const Connection = {
    async saveAndConnect() {
        try {
            const driver = document.getElementById('conn-driver').value;
            const host = document.getElementById('conn-host').value.trim();
            const port = document.getElementById('conn-port').value.trim();
            const database = document.getElementById('conn-database').value.trim();
            const username = document.getElementById('conn-username').value.trim();
            const password = document.getElementById('conn-password').value.trim();

            const connStr = Helpers.buildConnectionString(driver, host, port, database, username, password, "");

            const res = await API.testConnection(connStr);
            if (!res.success) {
                alert("Connection failed: " + (res.error || "Unknown error"));
                return;
            }

            localStorage.setItem('connection', JSON.stringify({
                driver, host, port, database, username, password,
                connection_string: connStr
            }));

            STATE.savedConnection = { driver, host, port, database, username, password, connection_string: connStr };
            STATE.isRealDatabase = true;
            UI.updateConnectionStatus('Connected', true);

            document.getElementById('modal-connection').classList.add('hidden');
            location.reload();
        } catch (e) {
            alert("Error: " + e.message);
        }
    }
};
