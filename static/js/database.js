/**
 * Database operations - SQLite disabled
 * Using email-only auth with localStorage instead
 */

export const Database = {
    async initialize() {
        console.log("📝 Using email authentication (no local SQLite needed)");
        return false;
    }
};
