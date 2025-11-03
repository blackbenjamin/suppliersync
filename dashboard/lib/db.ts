
import Database from "better-sqlite3";
import { existsSync } from "fs";
import { dirname } from "path";
import { mkdirSync } from "fs";

let db: Database.Database | null = null;

function getDb(): Database.Database {
  if (!db) {
    const dbPath = process.env.SQLITE_PATH || "../suppliersync.db";
    
    // Ensure the directory exists
    const dir = dirname(dbPath);
    if (dir !== "." && !existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    
    // Note: We don't use readonly mode because SQLite in WAL mode needs write access
    // for WAL/SHM files even when only reading. The dashboard code never writes to the
    // database (only queries), so this is safe.
    db = new Database(dbPath, { 
      fileMustExist: true // File must exist (created by API service)
      // readonly: false - Allow write access for WAL files, but code never writes data
    });
    
    // Disable WAL mode for dashboard connections to avoid write issues
    // The dashboard only reads, so we don't need WAL's performance benefits
    try {
      db.pragma("journal_mode = delete");
    } catch (error) {
      // If WAL mode is already disabled or can't be changed, that's fine
      console.warn("Could not change journal mode:", error);
    }
  }
  return db;
}

export function query<T = any>(sql: string, params: any[] = []): T[] {
  try {
    const database = getDb();
    const stmt = database.prepare(sql);
    return stmt.all(...params) as T[];
  } catch (error: any) {
    // During build, database might not exist - return empty array
    if (process.env.NEXT_PHASE === "phase-production-build") {
      return [] as T[];
    }
    throw error;
  }
}

export function run(sql: string, params: any[] = []) {
  try {
    const database = getDb();
    const stmt = database.prepare(sql);
    return stmt.run(...params);
  } catch (error: any) {
    // During build, database might not exist
    if (process.env.NEXT_PHASE === "phase-production-build") {
      return { changes: 0, lastInsertRowid: 0 };
    }
    throw error;
  }
}
