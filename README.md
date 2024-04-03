
# `Drumpler`

`Drumpler` is a general-purpose application designed to facilitate efficient workflow automation through RESTful API interactions and job processing. Built on Flask and SQLAlchemy, this application serves as a robust backend for capturing, storing, and processing HTTP requests in a scalable manner. The application is split into two main components: `drumpler.py` for handling RESTful API requests and `mammoth.py` for querying the API and processing jobs asynchronously.

## Features

-   **RESTful API Endpoints**: Secure and scalable endpoints for handling HTTP requests, including POST, GET, PUT, and DELETE operations.
-   **Database Integration**: Utilizes SQLAlchemy for ORM-based interactions with the database, supporting a variety of database systems.
-   **Job Processing**: Facilitates the asynchronous processing of tasks with support for multi-threading and multi-processing, ensuring efficient workflow automation.
-   **Event Logging**: Detailed event logging for each job processed, allowing for easy tracking and management of tasks.

## Prerequisites

Before you begin, ensure you have the following installed:

-   Python 3.6 or later
-   Flask
-   SQLAlchemy
-   Requests

Additionally, you will need:

-   A PostgreSQL database or any SQL database supported by SQLAlchemy.
-   An `.env` file configured with your database URI and authorization key.

## Installation

Install Drumpler via pip:
`pip install drumpler`

## Configuration

Create a `.env` file in the root directory of the application with the following contents:
```
DATABASE_URI=your_database_uri_here 
AUTHORIZATION_KEY=your_authorization_key_here 
Drumpler_HOST=0.0.0.0 
Drumpler_PORT=5000 
Drumpler_DEBUG=True
```

Replace `your_database_uri_here` and `your_authorization_key_here` with your actual database URI and desired authorization key.

## Running the Application

To start the `Drumpler` API server:
`python drumpler.py`

To initiate `mammoth` for processing jobs:
`python mammoth.py`

Ensure that `mammoth.py` is customized to include your specific job processing logic within the `process_request_data` function.

## API Endpoints

The application exposes several endpoints for interacting with the system:

-   **POST** `/request`: Submit a new request for processing.
-   **GET** `/request/<int:request_id>`: Retrieve a specific request by its ID.
-   **GET** `/request/next-unhandled`: Fetch the next unhandled request.
-   **PUT** `/request/<int:request_id>`: Update the status of a request.
-   **DELETE** `/request/<int:request_id>`: Delete a specific request.

## Contributing

Contributions to `Drumpler` are welcome! Please follow the standard fork-branch-PR workflow.

## License

This project is licensed under the MIT License - see the LICENSE file for details.