# Migration

For doing migration for the first time,  <br>
`python3 db-migrate.py db init` <br>
This will create a new folder named migrations <br>

For updating a model,  <br>
`python3 db-migrate.py db migrate`  <br>
`python3 db-migrate.py db upgrade`

*Note: * When you add a table to the database, update the db-migrate.py file by importing that table there.
