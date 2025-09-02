## Task Manager API with Database

This project is a RESTful API for managing tasks, built with Flask, SQLAlchemy, and Marshmallow. It demonstrates a robust and production-ready architecture using a modular application factory pattern, proper database integration, and centralized error handling.

## Features

RESTful Endpoints: Full CRUD (Create, Read, Update, Delete) functionality for tasks.
Database Integration: Uses SQLAlchemy as an ORM to interact with an SQLite database.
Data Serialization & Validation: Marshmallow is used to define API schemas, ensuring data is validated on input and consistently formatted on output.
Modular Architecture: The project uses a blueprint and application factory pattern, making it scalable and well-organized.
Centralized Error Handling: Global error handlers are implemented to provide consistent, JSON-formatted error responses for all exceptions, including validation errors and HTTP status codes.
Automatic Input Normalization: Input data is automatically stripped and normalized before validation to ensure data consistency.
HATEOAS Links: API responses are enriched with hypermedia links to make the API more discoverable and robust.
Logging: Basic logging is configured to capture application events and errors.

## Technologies

Python: The core programming language.
Flask: A lightweight web server framework.
Flask-SQLAlchemy: Flask extension for easy SQLAlchemy integration.
Marshmallow: An ORM/ODM/framework-agnostic library for converting complex objects to and from native Python datatypes.
Werkzeug: A WSGI utility library used by Flask.

## Project Structure

.
├── app/
│ ├── **init**.py # Application factory and configuration
│ ├── errors.py # Global error handlers
│ ├── models.py # SQLAlchemy ORM models
│ ├── routes.py # RESTful API endpoints (blueprint)
│ ├── schemas.py # Marshmallow schemas for data validation and serialization
│ └── templates/ # (Optional) HTML templates
├── instance/
│ └── tasks.db # SQLite database file (created by SQLAlchemy)
├── requirements.txt # Project dependencies
└── run.py # Application entry point

## Getting Started

1. Clone the repository
   sh
   git clone https://github.com/yofil7/task-manager-api-db.git
   cd task-manager-api-db

2. Create and activate a virtual environment
   sh
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   sh
   pip3 install -r requirements.txt

4. Run the application
   sh
   python3 run.py

# API Endpoints

The API serves requests on http://127.0.0.1:5000/tasks.

Create a new task
Endpoint: POST /tasks/
Request Body: {"title": "Buy groceries", "done": false}
Response: 201 Created

Retrieve all tasks
Endpoint: GET /tasks/
Response: 200 OK with a list of tasks.

Retrieve a single task
Endpoint: GET /tasks/<int:task_id>
Response: 200 OK with the task object or 404 Not Found.

Update a task
Endpoint: PUT /tasks/<int:task_id>
Request Body: {"title": "Updated title"} (partial update is supported)
Response: 200 OK with the updated task.

Mark a task as complete
Endpoint: POST /tasks/<int:task_id>/complete
Response: 200 OK with the updated task.

Delete a task
Endpoint: DELETE /tasks/<int:task_id>
Response: 204 No Content
