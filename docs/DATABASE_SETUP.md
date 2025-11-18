# Database Setup Verification

## Current Status ✅

- **Database**: `notes_db` (PostgreSQL)
- **Tables Created**: `notes`, `alembic_version`
- **Migrations Applied**: `86fff380304f` (head)
- **Trigger**: `notes_search_vector_update` (working correctly)

## Important: Database Name

⚠️ **The tables are in the `notes_db` database, NOT the `postgres` database!**

Your `.env` file correctly points to:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db
```

## Connecting to the Database

### Using Database Client (pgAdmin, DBeaver, etc.)

When connecting to PostgreSQL, make sure to:

1. **Host**: `localhost`
2. **Port**: `5432`
3. **Database**: `notes_db` ⬅️ **Important: Use `notes_db`, not `postgres`!**
4. **Username**: `postgres`
5. **Password**: `postgres`

### Using psql Command Line

```bash
psql -h localhost -p 5432 -U postgres -d notes_db
```

### Verify Tables Exist

Once connected to `notes_db`, you should see:
- `alembic_version` table (stores migration version)
- `notes` table with columns:
  - `id` (UUID)
  - `title` (VARCHAR 255)
  - `content` (TEXT)
  - `search_vector` (TSVECTOR)
  - `created_at` (TIMESTAMP WITH TIME ZONE)
  - `updated_at` (TIMESTAMP WITH TIME ZONE)

## About alembic.ini

The `alembic.ini` file has a placeholder URL (`driver://user:pass@localhost/dbname`), but this is **intentional and correct**. 

The `alembic/env.py` file automatically:
1. Reads the actual `DATABASE_URL` from your `.env` file via `app.config.settings`
2. Converts it from async (`postgresql+asyncpg://`) to sync (`postgresql+psycopg2://`) format
3. Overrides the placeholder URL in the config

So you don't need to manually update `alembic.ini` - it's handled automatically!

## Troubleshooting

### If you don't see tables:

1. **Check you're connected to the right database**: Make sure you're viewing `notes_db`, not `postgres`
2. **Verify PostgreSQL is running**: 
   ```bash
   docker ps | grep postgres
   ```
3. **Check migration status**:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   alembic current
   ```
4. **Re-run migrations if needed**:
   ```bash
   alembic upgrade head
   ```

### Test Database Connection

Run the verification script:
```bash
cd backend
.\venv\Scripts\Activate.ps1
python check_db.py
```

This will show:
- All tables in the database
- Current Alembic migration version
- Number of rows in notes table
- Trigger status

## Notes Table Structure

The `notes` table includes:
- **Full-text search**: Automatic `search_vector` updates via trigger
- **Indexes**: GIN index on `search_vector` for fast searches
- **UUID primary key**: Better for distributed systems

The trigger `notes_search_vector_update` automatically updates the `search_vector` column whenever `title` or `content` changes, enabling PostgreSQL's full-text search capabilities.

