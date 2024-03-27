
# Noggin

Noggin simplifies setting up a RESTful API server with Flask, focusing on the efficient handling and storage of HTTP requests. Designed to work out of the box, it allows developers to quickly integrate and store incoming requests in a SQLite database without worrying about the underlying details.

## Features

-   **Flexible Request Handling**: Accepts any raw JSON payload for POST requests.
-   **Automatic Metadata Extraction**: Dynamically extracts and stores request metadata such as source IP, user agent, and request method.
-   **SQLite Database Integration**: Seamlessly stores request data and metadata in a SQLite database for easy retrieval and management.
-   **Simple Configuration**: Easy to set up with minimal configuration required.
-   **Thread-safe**: Built to handle multiple requests concurrently without data loss.

## Getting Started

### Prerequisites

Ensure you have Python 3.6 or later installed on your system.

### Installation

1.  Clone this repository or download the `noggin.py` module into your project directory.
2.  Create a `.env` file in the root of your project directory with the following content, replacing `YourAuthorizationKeyHere` with your desired authorization key:

`AUTHORIZATION_KEY=YourAuthorizationKeyHere`

3.  Install the required dependencies:

`pip install -r requirements.txt`

### Usage

To use Noggin in your project:

```
from noggin import Noggin 

app = Noggin(host='127.0.0.1', port=5000, debug=True) 
app.run()
```

This will start a Flask server configured to handle requests as specified by the Noggin application.

## API Endpoints

Noggin provides the following endpoints:

-   **POST `/request`**: Accepts any raw JSON payload and stores it along with request metadata.
-   **GET `/request/<request_id>`**: Retrieves a specific request and its metadata by ID.
-   **PUT `/request/<request_id>`**: Updates the `is_handled` status of a specific request.
-   **DELETE `/request/<request_id>`**: Deletes a specific request.


### Examples

#### POST `/request`

To create a new request with any raw JSON payload:

`curl -X POST  "http://localhost:5000/request"  \ -H  "Content-Type: application/json"  \ -H  "Authorization: Bearer YourAuthorizationKey"  \ -d  '{"foo": "bar", "number": 123}'`

#### GET `/request/<request_id>`

To retrieve a specific request by ID (replace `1` with the actual request ID you want to retrieve):

`curl -X GET  "http://localhost:5000/request/1"  \ -H  "Authorization: Bearer YourAuthorizationKey"`

#### PUT `/request/<request_id>`

To update the `is_handled` status of a specific request (replace `1` with the request ID you want to update):

`curl -X PUT  "http://localhost:5000/request/1"  \ -H  "Content-Type: application/json"  \ -H  "Authorization: Bearer YourAuthorizationKey"  \ -d  '{"is_handled": 1}'`

This request marks the request with ID `1` as handled.

#### DELETE `/request/<request_id>`

To delete a specific request by ID (replace `1` with the request ID you want to delete):

`curl -X DELETE  "http://localhost:5000/request/1"  \ -H  "Authorization: Bearer YourAuthorizationKey"`

### Note:

-   In all the examples, `YourAuthorizationKey` should be replaced with the actual authorization key you've defined.
-   The JSON payload for the POST request can be any valid JSON structure. The examples use a simple object for demonstration.
-   The `is_handled` field in the PUT request example is set to `1`, indicating the request has been processed. Adjust this as needed based on your application's logic.
## Development

Noggin abstracts the complexities of request handling, making it straightforward to integrate into your existing Python projects. It's designed as a black box, but understanding its internal workings can help in extending its capabilities or troubleshooting.

### Testing

Refer to the `test_noggin.py` file for examples on how to write tests for your Noggin application. To run the tests, ensure you have the following packages installed:

`pip install pytest coverage Flask-Testing`

Then, execute the tests with:

`coverage run --branch -m pytest && coverage report -m`

## Contribution

Contributions to Noggin are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License

Noggin is open-source software licensed under the MIT license.