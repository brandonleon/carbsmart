# CarbSmart Notes

## Database Abstraction
- Persistence is handled via SQLAlchemy in `app/db.py` and repository functions.
- Current default is SQLite: `sqlite:///./carbsmart.db`.
- Pans are unique by `name` + `capacity_label` (capacity can be volume or pan size).
- Schema changes should use Alembic migrations: `alembic upgrade head`.

## Moving to Postgres
- Set `DATABASE_URL` to a Postgres DSN, for example:
  - `postgresql+psycopg://user:password@host:5432/carbsmart`
- Add a Postgres driver to dependencies (recommended: `psycopg`):
  - `psycopg[binary]`
- No code changes should be needed for pan CRUD; only the DSN and driver.
- For schema migrations later, add Alembic and generate migrations from `app/db_models.py`.
