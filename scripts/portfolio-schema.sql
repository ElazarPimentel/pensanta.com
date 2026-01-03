-- Portfolio Projects Database Schema
-- SQLite database to manage all Pensanta projects

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  url TEXT,
  description_es TEXT,
  description_en TEXT,
  type TEXT DEFAULT 'client',  -- 'client', 'internal', 'demo', 'personal'
  category TEXT,               -- 'e-commerce', 'professional-site', 'web-app', 'automation'
  tech_stack TEXT,             -- JSON array: '["NextJS","MariaDB","TypeScript"]'
  year INTEGER NOT NULL,
  screenshot_path TEXT,        -- relative: 'portfolio/slug-800x500.webp'
  include_in_portfolio BOOLEAN DEFAULT 0,
  client_name TEXT,
  sort_order INTEGER DEFAULT 999,
  live_status TEXT DEFAULT 'active', -- 'active', 'archived', 'offline'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast portfolio queries
CREATE INDEX IF NOT EXISTS idx_portfolio ON projects(include_in_portfolio, sort_order);
CREATE INDEX IF NOT EXISTS idx_slug ON projects(slug);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_timestamp
AFTER UPDATE ON projects
FOR EACH ROW
BEGIN
  UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
