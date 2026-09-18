import { CONFIG } from './config.js';

export const API = {
    async post(endpoint, data) {
        const res = await fetch(`${CONFIG.API_BASE}/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    testConnection(connStr) {
        return this.post("test-connection", { connection_string: connStr });
    },

    executeQuery(query, connStr) {
        return this.post("execute-query", { query, connection_string: connStr });
    },

    getSchema(connStr) {
        return this.post("schema", { connection_string: connStr });
    }
};
