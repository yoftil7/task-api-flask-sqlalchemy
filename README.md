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
User Management:

- Secure registration and login endpoints.
- Users are authenticated via JSON Web Tokens (JWT).
  Role-Based Access Control (RBAC):
- Users are assigned roles (`user` or `admin`).
- Specific routes are protected, allowing only users with the `admin` role to perform certain actions (e.g., deleting tasks).
  Dynamic Querying:
- Filtering: Filter tasks by their completion status (`?completed=true` or `?completed=false`).
- Sorting: Sort tasks by different fields (`?sort=priority`, `?sort=created_at`, `?sort=-id` for descending).
- Pagination: Retrieve task lists in pages (`?page=2&per_page=20`).

## Technologies

Python: The core programming language.
Flask: A lightweight web server framework.
Flask-JWT-Extended: Handles JWT authentication
Flask-SQLAlchemy: Flask extension for easy SQLAlchemy integration.
Alembic: Database migration tool
Marshmallow: An ORM/ODM/framework-agnostic library for converting complex objects to and from native Python datatypes.
Werkzeug: A WSGI utility library used by Flask.
Pytest: The testing framework used to validate the application.

## Testing

The project includes a comprehensive test suite built with `pytest`. Tests are configured to run in an isolated in-memory SQLite database, ensuring speed and reliability.

**To run the tests, execute the following command from the project root:**

```sh
pytest -v
```

## Project Structure

.
├── app/
│ ├── **init**.py # Application factory and configuration
│ ├── errors.py # Global error handlers
│ ├── models.py # SQLAlchemy ORM models
│ ├── routes.py # RESTful API endpoints (blueprint)
│ ├── schemas.py # Marshmallow schemas for data validation and serialization
│ └── templates/ # (Optional) HTML templates
├── tests/
│ ├── conftest.py # Pytest fixtures for test setup
│ ├── test_health.py # Tests for the health endpoint
│ └── test_task.py # Tests for the task CRUD endpoints
├── instance/
│ └── tasks.db # SQLite database file (created by SQLAlchemy)
├── requirements.txt # Project dependencies
└── run.py # Application entry point

## Getting Started

1. Clone the repository

   ```sh
   git clone https://github.com/yofil7/task-manager-api-db.git
   cd task-manager-api-db
   ```

2. Create and activate a virtual environment

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies

   ```sh
   pip3 install -r requirements.txt
   ```

4. **Initialize the database:**
   The application uses Alembic for database migrations. Run the following commands to create the `tasks.db` file and the necessary tables.

   ```sh
   flask db upgrade head
   ```

5. Run the application
   ```sh
   python3 run.py
   ```

## API Endpoints

All endpoints require a JWT access token in the `Authorization: Bearer <token>` header, except for the authentication routes.

### Authentication

**`POST /auth/register`**

- **Description:** Creates a new user.
- **Body:** `{"username": "your_username", "password": "your_password"}`
- **Response:** `201 Created` with an `access_token` and user details.

**`POST /auth/login`**

- **Description:** Authenticates a user and issues an access token.
- **Body:** `{"username": "your_username", "password": "your_password"}`
- **Response:** `200 OK` with an `access_token` and user details.

### Standard Task Management (User Role)

**`POST /tasks`**

- **Description:** Creates a new task for the authenticated user.
- **Required Role:** `user`
- **Body:** `{"description": "Task description", "priority": 1}`
- **Response:** `201 Created` with the new task object.

**`GET /tasks`**

- **Description:** Retrieves a list of tasks for the authenticated user with optional filtering, sorting, and pagination.
- **Required Role:** `user`
- **Query Parameters:**
  - `page`: (int, default=1)
  - `per_page`: (int, default=10, max=100)
  - `completed`: (bool) Filter by completion status (`true` or `false`).
  - `sort_by`: (string) Sort by `id`, `priority`, or `created_at`.
  - `sort_order`: (string) Sorting order (`asc` or `desc`).
- **Example:** `GET /tasks?completed=false&sort_by=priority&sort_order=desc&page=2`

**`GET /tasks/<int:task_id>`**

- **Description:** Retrieves a single task if it belongs to the authenticated user.
- **Required Role:** `user`
- **Response:** `200 OK` with the task object. `404 Not Found` if the task does not exist or does not belong to the user.

**`PUT /tasks/<int:task_id>`**

- **Description:** Updates a task. Supports partial updates (`PATCH`).
- **Required Role:** `user`
- **Body:** `{"description": "Updated text", "priority": 2}`
- **Response:** `200 OK` with the updated task object.

**`POST /tasks/<int:task_id>/complete`**

- **Description:** Marks a task as complete.
- **Required Role:** `user`
- **Response:** `200 OK` with the updated task object.

**`DELETE /tasks/<int:task_id>`**

- **Description:** Deletes a task. This route restricts users to deleting only their own tasks.
- **Required Role:** `user`
- **Response:** `204 No Content`.

### Role-Based Access Control (Admin & Manager)

**`DELETE /admin/tasks/<int:task_id>`**

- **Description:** Deletes any task by its ID, regardless of the owner.
- **Required Role:** `admin`
- **Response:** `204 No Content`.

**`GET /admin/dashboard`**

- **Description:** An example of a route accessible only by administrators.
- **Required Role:** `admin`
- **Response:** `{"message": "adminstrator dashboard"}`

**`GET /reports`**

- **Description:** An example of a route accessible by both administrators and managers.
- **Required Roles:** `admin`, `manager`
- **Response:** `{"message": "Reports visible for admins & managers"}`

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
