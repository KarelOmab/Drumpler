
# `Drumpler`

`Drumpler` is a general-purpose application designed to facilitate efficient workflow automation through RESTful API interactions and job processing. Built on Flask and SQLAlchemy, this application serves as a robust backend for capturing, storing, and processing HTTP requests in a scalable manner. The application is split into two main components: `drumpler.py` for handling RESTful API requests and `mammoth.py` for querying the API and processing jobs asynchronously.

# High Level Overview

![Image Description](https://github.com/KarelOmab/Drumpler/blob/main/model/Drumpler%20Framework.png?raw=true)

## Features

-   **RESTful API Endpoints**: Secure and scalable endpoints for handling HTTP requests, including POST, GET, PUT, and DELETE operations.
-   **Database Integration**: Utilizes SQLAlchemy for ORM-based interactions with Postgres.
-   **Job Processing**: Facilitates the asynchronous processing of tasks with support for multi-threading and multi-processing, ensuring efficient workflow automation.
-   **Event Logging**: Detailed event logging for each HTTP request, job processing and related events, allowing for easy tracking and management of tasks.

## Prerequisites

Before you begin, ensure you have the following installed:

-   Python 3.6 or later
-   PostgreSQL

## Installation

Install Drumpler via pip:
`pip install Drumpler`

## Configuration

Create a `.env` file in the root directory of the application with the following contents:
```
AUTHORIZATION_KEY=AUTH_KEY_HERE
DRUMPLER_HOST=IP_HERE
DRUMPLER_PORT=PORT_HERE
DRUMPLER_DEBUG=BOOL_FLAG
DB_NAME=DB_NAME_HERE
DB_HOST=DB_HOST_HERE
DB_USER=DB_USER_HERE
DB_PASS=DB_PASS_HERE
```

Replace `your_database_uri_here` and `your_authorization_key_here` with your actual database URI and desired authorization key.

## Using the Application - Drumpler

To create a `Drumpler` RESTful server, the following is a sample implementation:
```
import drumpler

# Now, you can create an instance of the Drumpler class
app = drumpler.Drumpler(host="0.0.0.0", port=5000, debug=True)  # Adjust as necessary

# And call the run method on this instance
app.run()
```

### API Endpoints

Drumpler exposes the following endpoints for interacting with its system:

-   **POST** `/request`: Submit a new request for processing.
-   **GET** `/request/<int:request_id>`: Retrieve a specific request by its ID.
-   **GET** `/request/next-unhandled`: Fetch the next unhandled request.
-   **PUT** `/request/<int:request_id>`: Update the status of a request.
-   **DELETE** `/request/<int:request_id>`: Delete a specific request.

## Using the Application - Mammoth
To create a `Mammoth` (request-processor), the following is a sample implementation:
```
from drumpler.mammoth import Mammoth

def custom_process_function(session, request, job_id):
    # this is the driver method for your customized workflow
    pass

# Initialize Mammoth
DRUMPLER_HOST = "http://127.0.0.1"
DRUMPLER_PORT = 5000  # Adjust the URL/port as necessary
DRUMPLER_URL = f"{DRUMPLER_HOST}:{DRUMPLER_PORT}"  # Adjust the URL/port as necessary
MAMMOTH_WORKERS = 1
mammoth = Mammoth(process_request_data=custom_process_function, drumpler_url=DRUMPLER_URL, workers=MAMMOTH_WORKERS)

if __name__ == "__main__":
    print("Starting Mammoth... Press CTRL+C to stop.")
    mammoth.run()
```

## Contributing

Contributions to `Drumpler` are welcome! Please follow the standard fork-branch-PR workflow.

## License

This project is licensed under the MIT License - see the LICENSE file for details.