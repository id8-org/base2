# Database Initialization

This project initializes the database directly from SQLAlchemy models defined in `app/models.py`, without using Alembic migrations.

## How It Works

### Database Schema Creation

The database tables are created automatically from the SQLModel class definitions in `app/models.py` using:

```python
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)
```

This approach:
- Creates all tables defined in models.py
- Handles relationships and foreign keys automatically
- Ensures schema matches the current model definitions

### Initialization Process

1. **Container Startup**: When the Docker container starts, it runs `scripts/prestart.sh`
2. **Database Connection**: The script first waits for the database to be ready via `app/backend_pre_start.py`
3. **Schema Creation**: The script runs `app/initial_data.py` which calls `init_db()` to:
   - Create all database tables from models
   - Create the initial superuser account

### Files Involved

- `app/models.py` - Contains all SQLModel table definitions
- `app/core/db.py` - Contains the `init_db()` function for database initialization
- `app/initial_data.py` - Script that calls init_db() to set up the database
- `scripts/prestart.sh` - Container startup script that initializes the database
- `app/backend_pre_start.py` - Waits for database to be ready before initialization

## Migration Strategy

Since this project no longer uses Alembic:

- **Schema Changes**: Update the models in `app/models.py` directly
- **Database Updates**: For production deployments, you'll need to manually handle schema changes
- **Data Migration**: Any data transformations must be handled separately through custom scripts

## Development Workflow

1. Make changes to models in `app/models.py`
2. Restart the development environment (containers will recreate tables)
3. The database will be initialized with the new schema automatically

## Production Considerations

- **Backup**: Always backup your database before deploying schema changes
- **Schema Changes**: Plan schema modifications carefully as there's no automatic migration
- **Testing**: Test schema changes thoroughly in staging environments
- **Rollback**: Keep previous model versions for potential rollbacks