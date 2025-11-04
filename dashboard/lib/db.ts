
import Database from "better-sqlite3";
import { existsSync } from "fs";
import { dirname } from "path";
import { mkdirSync } from "fs";

let db: Database.Database | null = null;

function getDb(): Database.Database {
  if (!db) {
    const dbPath = process.env.SQLITE_PATH || "../suppliersync.db";
    
    // In Vercel/production, database is not accessible - return null
    // The dashboard should fetch data from the Railway API instead
    if (process.env.VERCEL || !existsSync(dbPath)) {
      return null as any; // Will be handled by query function
    }
    
    // Ensure the directory exists
    const dir = dirname(dbPath);
    if (dir !== "." && !existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    
    try {
      db = new Database(dbPath, { 
        fileMustExist: false // Allow database to not exist (will return empty arrays)
      });
      
      // Disable WAL mode for dashboard connections to avoid write issues
      try {
        db.pragma("journal_mode = delete");
      } catch (error) {
        console.warn("Could not change journal mode:", error);
      }
    } catch (error) {
      console.warn("Database connection failed:", error);
      return null as any;
    }
  }
  return db;
}

export function query<T = any>(sql: string, params: any[] = []): T[] {
  try {
    // In Vercel/production, database is not accessible - return empty array
    if (process.env.VERCEL) {
      return [] as T[];
    }
    
    const database = getDb();
    if (!database) {
      return [] as T[];
    }
    
    const stmt = database.prepare(sql);
    return stmt.all(...params) as T[];
  } catch (error: any) {
    // During build or if database not available, return empty array
    console.warn("Database query error:", error.message);
    return [] as T[];
  }
}

export function run(sql: string, params: any[] = []) {
  try {
    // In Vercel/production, database is not accessible - return empty result
    if (process.env.VERCEL) {
      return { changes: 0, lastInsertRowid: 0 };
    }
    
    const database = getDb();
    if (!database) {
      return { changes: 0, lastInsertRowid: 0 };
    }
    
    const stmt = database.prepare(sql);
    return stmt.run(...params);
  } catch (error: any) {
    // During build or if database not available, return empty result
    console.warn("Database run error:", error.message);
    return { changes: 0, lastInsertRowid: 0 };
  }
}
