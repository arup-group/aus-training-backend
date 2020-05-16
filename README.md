# Training plan 2.0 backend

The code in this repository contains an API developed in Python and Django that can be used as the backend of the
Australasia Digital Training Plan website.

The service runs on a PostgreSQL database with a fairly simple data model, and the API is used for CRUD operations of the website's courses. The API also contains an endpoint that reads an .xls file for easily updating the database at once.

**TODO**: setup docker container for this service

### Install dependencies

Make sure to install all dependencies before running the application.

```bash 
pip install -r requirements.txt
````

### Setup the database

The initial migration needs to be done before we starting the service, in the top level folder run:

```bash 
python manage.py migrate
````

### Run the service 

After making the first migration, run the following command to start the server on the port specified in the .env file:

```bash 
python manage.py runserver
````