/**
 * Consolidated helper functions to reduce duplication
 */

export const Helpers = {
    /**
     * Generate CSV from columns and values
     */
    generateCSV(columns, values) {
        const header = columns.map(c => `"${c.replace(/"/g, '""')}"`).join(',');
        const rows = values.map(row =>
            row.map(val => {
                if (val === null) return '""';
                return `"${String(val).replace(/"/g, '""')}"`;
            }).join(',')
        );
        return [header, ...rows].join('\n');
    },

    /**
     * Convert object array to CSV
     */
    convertToCSV(columns, rows) {
        const header = columns.map(c => `"${c.replace(/"/g, '""')}"`).join(',');
        const rowStrings = rows.map(row =>
            columns.map(col => {
                const val = row[col];
                if (val === null) return '""';
                return `"${String(val).replace(/"/g, '""')}"`;
            }).join(',')
        );
        return [header, ...rowStrings].join('\n');
    },

    /**
     * Generate SQL rollback script
     */
    generateRollbackSQL(type, table, cols, rows) {
        if (type === "DELETE") {
            return this._generateInsertRollback(table, cols, rows);
        } else if (type === "UPDATE") {
            return this._generateUpdateRollback(table, cols, rows);
        }
        return "-- No automated rollback available";
    },

    _generateInsertRollback(table, cols, rows) {
        const colNames = cols.join(', ');
        const insertStatements = rows.map(row => {
            const formattedVals = row.map(val => {
                if (val === null) return "NULL";
                if (typeof val === 'number') return val;
                return `'${String(val).replace(/'/g, "''")}'`;
            }).join(', ');
            return `INSERT INTO ${table} (${colNames}) VALUES (${formattedVals});`;
        });
        return insertStatements.join('\n');
    },

    _generateUpdateRollback(table, cols, rows) {
        const pkIndex = cols.indexOf('id') !== -1 ? cols.indexOf('id') : 0;
        const updateStatements = rows.map(row => {
            const setPairs = cols.map((col, idx) => {
                const val = row[idx];
                const valStr = val === null ? "NULL" : typeof val === 'number' ? val : `'${String(val).replace(/'/g, "''")}'`;
                return `${col} = ${valStr}`;
            }).join(', ');
            const pkVal = row[pkIndex];
            const pkValStr = typeof pkVal === 'number' ? pkVal : `'${pkVal}'`;
            return `UPDATE ${table} SET ${setPairs} WHERE ${cols[pkIndex]} = ${pkValStr};`;
        });
        return updateStatements.join('\n');
    },

    /**
     * Download file
     */
    downloadFile(url, filename) {
        const tempLink = document.createElement('a');
        tempLink.href = url;
        tempLink.setAttribute('download', filename);
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
    },

    /**
     * Download text as file
     */
    downloadText(text, filename, mimeType = 'text/plain') {
        const blob = new Blob([text], { type: mimeType });
        const url = URL.createObjectURL(blob);
        this.downloadFile(url, filename);
    },

    /**
     * Extract table and where clause from SQL query
     */
    extractTableName(sqlQuery) {
        const cleanQuery = sqlQuery.trim();
        const queryType = cleanQuery.split(/\s+/)[0].toUpperCase();

        if (queryType === "UPDATE") {
            const match = cleanQuery.match(/UPDATE\s+([^\s]+)/i);
            return match ? match[1].replace(/[`"']/g, '') : null;
        } else if (queryType === "DELETE") {
            const match = cleanQuery.match(/DELETE\s+FROM\s+([^\s]+)/i);
            return match ? match[1].replace(/[`"']/g, '') : null;
        } else if (queryType === "SELECT") {
            const match = cleanQuery.match(/FROM\s+([^\s]+)/i);
            return match ? match[1].replace(/[`"']/g, '') : null;
        }
        return null;
    },

    /**
     * Extract WHERE clause from SQL query
     */
    extractWhereClause(sqlQuery) {
        const match = sqlQuery.match(/WHERE\s+(.+?)(?:;)?$/i);
        return match ? match[1] : "";
    },

    /**
     * Build database connection string
     */
    buildConnectionString(driver, host, port, database, username, password, sqlitePath) {
        if (driver === 'sqlite') {
            if (!sqlitePath) throw new Error('Enter SQLite file path');
            return `sqlite:///${sqlitePath}`;
        }

        if (!host || !database || !username) {
            throw new Error('Fill all required fields');
        }

        const encodedUsername = encodeURIComponent(username);
        const encodedPassword = encodeURIComponent(password);

        if (driver === 'postgres') {
            const p = port || '5432';
            return `postgresql://${encodedUsername}:${encodedPassword}@${host}:${p}/${database}`;
        } else if (driver === 'mysql') {
            const p = port || '3306';
            return `mysql+pymysql://${encodedUsername}:${encodedPassword}@${host}:${p}/${database}`;
        }

        throw new Error('Unknown database driver');
    },

    /**
     * Format timestamp consistently
     */
    formatTimestamp(date = new Date()) {
        return date.toLocaleTimeString();
    },

    /**
     * Get query type (SELECT, INSERT, UPDATE, DELETE, etc)
     */
    getQueryType(sqlQuery) {
        const cleanQuery = sqlQuery.trim();
        return cleanQuery.split(/\s+/)[0].toUpperCase();
    }
};
