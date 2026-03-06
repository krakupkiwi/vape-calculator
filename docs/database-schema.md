# Database Schema

Database: SQLite, managed via SQLModel + Alembic migrations.
File location inside container: `/data/vape.db`

---

## Tables

### `flavors`
Ingredient database — flavor concentrates.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| name | TEXT | e.g. "Strawberry" |
| manufacturer | TEXT | e.g. "TFA", "CAP", "FA", "FLV", "INW" |
| abbreviation | TEXT | e.g. "TFA SB" |
| base_pg | REAL | PG fraction (0.0–1.0), default 1.0 |
| base_vg | REAL | VG fraction, default 0.0 |
| density | REAL | g/ml for weight mixing, default 1.0 |
| cost_per_ml | REAL | User-set price, default 0.0 |
| notes | TEXT | Optional flavor notes |
| is_custom | INTEGER | 1 = user-added, 0 = seeded |
| created_at | TEXT | ISO datetime |

Unique index: `(name, manufacturer)`

---

### `nic_bases`
Nicotine base solutions.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| name | TEXT | e.g. "100mg PG Nic" |
| strength_mg | REAL | mg/ml concentration |
| base_pg | REAL | PG fraction |
| base_vg | REAL | VG fraction |
| cost_per_ml | REAL | |
| notes | TEXT | |

---

### `recipes`
Saved recipes.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| name | TEXT | Recipe name |
| author | TEXT | Default: "Local User" |
| description | TEXT | Short summary |
| notes | TEXT | Markdown supported |
| batch_size_ml | REAL | Target batch size |
| target_nic_mg | REAL | Target nicotine strength mg/ml |
| nic_base_id | INTEGER FK | References nic_bases.id |
| pg_ratio | REAL | PG fraction (0.0–1.0) |
| vg_ratio | REAL | VG fraction |
| rating | INTEGER | 1–5, nullable |
| is_public | INTEGER | Reserved for future sharing |
| parent_id | INTEGER FK | Self-referential, set on clone |
| created_at | TEXT | ISO datetime |
| updated_at | TEXT | ISO datetime |

---

### `recipe_flavors`
Join table: flavors used in a recipe (each row = one flavor line).

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| recipe_id | INTEGER FK | References recipes.id CASCADE DELETE |
| flavor_id | INTEGER FK | References flavors.id, nullable |
| custom_name | TEXT | If flavor not in DB, store name here |
| percentage | REAL | 0.0–100.0 |
| sort_order | INTEGER | Display order |

---

### `recipe_ratings`
Per-recipe ratings and notes (supports multiple ratings over time).

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| recipe_id | INTEGER FK | References recipes.id CASCADE DELETE |
| rating | INTEGER | 1–5 (CHECK constraint) |
| note | TEXT | Optional tasting note |
| created_at | TEXT | ISO datetime |

---

### `label_templates`
Uploaded or seeded label HTML templates.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto |
| name | TEXT | Display name |
| file_path | TEXT | Path under /data/templates/ |
| description | TEXT | |
| is_default | INTEGER | 1 = shown first in picker |
| created_at | TEXT | ISO datetime |

---

## Full DDL

```sql
CREATE TABLE flavors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    abbreviation TEXT,
    base_pg     REAL DEFAULT 1.0,
    base_vg     REAL DEFAULT 0.0,
    density     REAL DEFAULT 1.0,
    cost_per_ml REAL DEFAULT 0.0,
    notes       TEXT,
    is_custom   INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE nic_bases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    strength_mg REAL NOT NULL,
    base_pg     REAL NOT NULL,
    base_vg     REAL NOT NULL,
    cost_per_ml REAL DEFAULT 0.0,
    notes       TEXT
);

CREATE TABLE recipes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    author          TEXT DEFAULT 'Local User',
    description     TEXT,
    notes           TEXT,
    batch_size_ml   REAL NOT NULL,
    target_nic_mg   REAL NOT NULL DEFAULT 0,
    nic_base_id     INTEGER REFERENCES nic_bases(id),
    pg_ratio        REAL NOT NULL DEFAULT 0.3,
    vg_ratio        REAL NOT NULL DEFAULT 0.7,
    rating          INTEGER DEFAULT NULL,
    is_public       INTEGER DEFAULT 0,
    parent_id       INTEGER REFERENCES recipes(id),
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE recipe_flavors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    flavor_id   INTEGER REFERENCES flavors(id),
    custom_name TEXT,
    percentage  REAL NOT NULL,
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE recipe_ratings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    rating      INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    note        TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE label_templates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    file_path   TEXT NOT NULL,
    description TEXT,
    is_default  INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_recipe_flavors_recipe ON recipe_flavors(recipe_id);
CREATE INDEX idx_recipes_created ON recipes(created_at DESC);
CREATE UNIQUE INDEX idx_flavors_name_mfg ON flavors(name, manufacturer);
```
