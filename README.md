Use alembic for migrating the database:

    alembic revision --autogenerate -m "name" # verify output
    alembic upgrade head
    alembic downgrade -1
    alembic history
    
Create the database from scratch and set alembic head to current state

    python scripts/create_database.py

Test server page:

    http://127.0.0.1:5000/1041036125894082621