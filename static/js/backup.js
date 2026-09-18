/**
 * Backup and vault operations
 */

import { API } from './api.js';
import { STATE } from './config.js';
import { Helpers } from './helpers.js';
import { UI } from './ui.js';

export const Backup = {
    handleAutoBackup(sqlQuery) {
        // Auto-backup is handled during real database query execution in query.js
        // This is a placeholder for local database operations (now deprecated)
        return null;
    },

    clearVault() {
        if (confirm('Clear all backups from vault?')) {
            STATE.backupVault = [];
            STATE.totalProtectedRows = 0;
            localStorage.setItem('vault', JSON.stringify(STATE.backupVault));
            UI.updateVaultUI(STATE.backupVault, STATE.totalProtectedRows);
            alert('✅ Vault cleared!');
        }
    },

    copyRollbackSQL() {
        if (!STATE.activeRollbackSql) {
            alert('No rollback SQL available');
            return;
        }
        navigator.clipboard.writeText(STATE.activeRollbackSql);
        alert('✅ Rollback SQL copied to clipboard!');
    },

    downloadRollbackSQL() {
        if (!STATE.activeRollbackSql) {
            alert('No rollback SQL available');
            return;
        }
        Helpers.downloadText(STATE.activeRollbackSql, `rollback_${Date.now()}.sql`, 'text/sql');
        alert('✅ Rollback SQL downloaded!');
    },

    openRollbackModal(idx) {
        const item = STATE.backupVault[idx];
        if (!item) return;

        STATE.activeRollbackSql = item.rollbackSql;
        document.getElementById('rollback-sql-text').value = item.rollbackSql;
        document.getElementById('rollback-affected-rows').innerText = `${item.rowsCount} row${item.rowsCount !== 1 ? 's' : ''}`;
        document.getElementById('modal-rollback').classList.remove('hidden');
    },

    async applyRollback() {
        if (!STATE.activeRollbackSql) {
            alert('No rollback SQL available');
            return;
        }

        if (!STATE.isRealDatabase) {
            alert('❌ Database not connected');
            return;
        }

        try {
            const connStr = STATE.savedConnection?.connection_string;
            const response = await API.executeQuery(STATE.activeRollbackSql, true, connStr);
            alert('✅ Rollback applied successfully!');
            document.getElementById('modal-rollback').classList.add('hidden');
            STATE.activeRollbackSql = null;
        } catch (err) {
            alert('❌ Rollback failed: ' + err.message);
        }
    }
};
