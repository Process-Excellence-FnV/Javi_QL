import { API } from './api.js';
import { STATE } from './config.js';
import { UI } from './ui.js';
import { Connection } from './connection.js';
import { Query } from './query.js';

class App {
    checkAuth() {
        const user = localStorage.getItem('user');
        if (!user) {
            window.location.href = '/login.html';
            return false;
        }
        STATE.currentUser = JSON.parse(user);
        return true;
    }

    async loadConnection() {
        const conn = localStorage.getItem('connection');
        if (conn) {
            STATE.savedConnection = JSON.parse(conn);
            const res = await API.testConnection(STATE.savedConnection.connection_string);
            if (res.success) {
                STATE.isRealDatabase = true;
                UI.updateConnectionStatus('Connected', true);
                const schema = await API.getSchema(STATE.savedConnection.connection_string);
                STATE.currentSchema = schema.schema || {};
            }
        }
    }

    setupListeners() {
        document.getElementById('btn-run-sql')?.addEventListener('click', () => Query.executeQuery());
        document.getElementById('btn-open-conn-modal')?.addEventListener('click', () => {
            document.getElementById('modal-connection').classList.remove('hidden');
        });
        document.getElementById('btn-save-connection')?.addEventListener('click', () => Connection.saveAndConnect());
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.addEventListener('click', () => UI.switchTab(b.getAttribute('data-tab')));
        });
    }

    async init() {
        if (!this.checkAuth()) return;
        await this.loadConnection();
        this.setupListeners();
    }
}

document.addEventListener('DOMContentLoaded', () => new App().init());
