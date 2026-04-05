-- Hopper Ops — Database Schema
-- PostgreSQL 16, database: hopper_ops, user: hopperops

CREATE TABLE IF NOT EXISTS components (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL, -- infrastructure, runtime, sdk, anthropic, security, service
  current_version VARCHAR(50),
  eol_date DATE,
  eol_source VARCHAR(100), -- endoflife.date, manual, vendor
  risk_level VARCHAR(10) NOT NULL DEFAULT 'green', -- red, yellow, green
  project VARCHAR(100), -- traillog, escapevelocity, mpf, n8n, etc.
  notes TEXT,
  last_checked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(name, project)
);

CREATE TABLE IF NOT EXISTS risk_items (
  id SERIAL PRIMARY KEY,
  component_id INTEGER REFERENCES components(id) ON DELETE SET NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  risk_level VARCHAR(10) NOT NULL DEFAULT 'yellow', -- red, yellow, green
  category VARCHAR(50) NOT NULL, -- eol, security, deprecation, drift, other
  deadline DATE,
  status VARCHAR(20) NOT NULL DEFAULT 'open', -- open, in_progress, resolved, accepted
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS action_items (
  id SERIAL PRIMARY KEY,
  risk_item_id INTEGER REFERENCES risk_items(id) ON DELETE SET NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- critical, high, medium, low
  status VARCHAR(20) NOT NULL DEFAULT 'open', -- open, in_progress, done, dismissed
  source_module VARCHAR(100),
  due_date DATE,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS module_runs (
  id SERIAL PRIMARY KEY,
  module_name VARCHAR(100) NOT NULL,
  module_type VARCHAR(20) NOT NULL, -- deterministic, llm
  ran_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  success BOOLEAN NOT NULL DEFAULT TRUE,
  duration_ms INTEGER,
  result_data JSONB,
  brief_text TEXT,
  error_message TEXT
);

CREATE TABLE IF NOT EXISTS feed_entries (
  id SERIAL PRIMARY KEY,
  module_name VARCHAR(100) NOT NULL,
  entry_type VARCHAR(50) NOT NULL, -- status, incident, release, deprecation, news, interesting, eol
  title VARCHAR(500) NOT NULL,
  body TEXT,
  source_url VARCHAR(500),
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sbom_snapshots (
  id SERIAL PRIMARY KEY,
  snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
  data JSONB NOT NULL,
  diff_from_previous JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scan_history (
  id SERIAL PRIMARY KEY,
  scan_type VARCHAR(50) NOT NULL, -- full_audit, version_check, eol_check
  ran_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  results JSONB,
  changes_detected BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS sessions (
  sid VARCHAR NOT NULL PRIMARY KEY,
  sess JSONB NOT NULL,
  expire TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions (expire);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_components_risk ON components (risk_level);
CREATE INDEX IF NOT EXISTS idx_components_category ON components (category);
CREATE INDEX IF NOT EXISTS idx_risk_items_status ON risk_items (status);
CREATE INDEX IF NOT EXISTS idx_risk_items_level ON risk_items (risk_level);
CREATE INDEX IF NOT EXISTS idx_action_items_status ON action_items (status);
CREATE INDEX IF NOT EXISTS idx_action_items_priority ON action_items (priority);
CREATE INDEX IF NOT EXISTS idx_module_runs_name ON module_runs (module_name, ran_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_entries_type ON feed_entries (entry_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_entries_created ON feed_entries (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sbom_snapshots_date ON sbom_snapshots (snapshot_date DESC);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_components_updated BEFORE UPDATE ON components FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_risk_items_updated BEFORE UPDATE ON risk_items FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_action_items_updated BEFORE UPDATE ON action_items FOR EACH ROW EXECUTE FUNCTION update_updated_at();
