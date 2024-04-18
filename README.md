# Drumpler

`Drumpler` is an advanced framework engineered to streamline the development of secure RESTful APIs that facilitate custom post-processing of incoming HTTP requests. Built on the robust foundations of Flask and SQLAlchemy, Drumpler not only captures and stores HTTP requests but also seamlessly integrates with PostgreSQL to ensure scalable data management. With Drumpler, you can focus on solely crafting the logic of your desired workflow while it handles the intricacies of API management and job orchestration through its companion component, Mammoth. [Mammoth](https://github.com/KarelOmab/Drumpler-Mammoth) leverages the structure established by Drumpler to process queued jobs, allowing developers to specify custom workflow(s) that respond dynamically to incoming data.

## High Level Overview 
The framework consists of two main components: 

 1. `drumpler.py` that manages RESTful API requests and facilitates database transactions.
 2. `drumpler-mammoth.py`: Handles querying the API and processing jobs asynchronously based on some payload. 
 
![Drumpler Framework Overview](https://github.com/KarelOmab/Drumpler/blob/main/model/Drumpler%20Framework.png?raw=true)

  
## Features
-  **RESTful API Endpoints**: Secure and scalable endpoints for handling HTTP requests including POST, GET, PUT, and DELETE operations.
-  **Database Integration**: Uses SQLAlchemy for ORM-based interactions, specifically designed for PostgreSQL.
-  **Job Processing**: Supports multithreading and multiprocessing for efficient job handling.
-  **Dynamic Event Logging**: Implements detailed logging for all interactions, which facilitates monitoring and debugging.

  
## Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.6 or later
- PostgreSQL

## Installation
Install Drumpler via pip:
`pip install Drumpler`

## Configuration

Although Drumpler will work out of the box with default configuration for localhost it is **not recommended to use default values**. Instead you should create a `.env` file in the root directory of the application and replace the placeholder values:

```
AUTHORIZATION_KEY=AUTH_KEY_HERE	# expected Bearer Token value
DRUMPLER_HOST=IP_HERE	    #i.e. localhost
DRUMPLER_PORT=PORT_HERE	    #i.e. 5000
DRUMPLER_DEBUG=BOOL_FLAG	# True/False
DB_NAME=DB_NAME_HERE	    #i.e. drumpler
DB_HOST=DB_HOST_HERE	    #i.e. localhost
DB_USER=DB_USER_HERE	    #i.e. myuser
DB_PASS=DB_PASS_HERE	    #i.e. mypassword
DATABASE_URI=postgresql://DB_USER_HERE:DB_PASS_HERE@DB_HOST_HERE/DB_NAME_HERE
```

### API Endpoints

The following is an exhaustive list of endpoints exposed by Drumpler for interacting with its system - these could be used for development-debugging purposes. Please note that the framework is designed such that Mammoth will be facilitaing all the required HTTP requests for you, there should be no need to make manual requests:

### API Endpoints
1.  **Root Endpoint (Hello World)**
    -   **GET** `/`: Returns a simple "Hello Drumpler {version}!" message.
2.  **Request Handling Endpoints**
    -   **POST** `/request`: Submit a new request for processing.
    -   **GET** `/request/<int:request_id>`: Retrieve a specific request by its ID.
    -   **PUT** `/request/<int:request_id>`: Update an existing request.
    -   **DELETE** `/request/<int:request_id>`: Delete a specific request.
3.  **Job Processing Endpoints**
    -   **GET** `/jobs/next-pending`: Fetch the next pending job that hasn't been handled.
    -   **PUT** `/jobs/<int:job_id>`: Update an existing job.
    -   **PUT** `/jobs/<int:job_id>/update-status`: Update the status of a job (e.g., from "Pending" to "Completed").
    -   **PUT** `/jobs/<int:job_id>/mark-handled`: Mark a request as handled, indicating that no further action is needed.
4.  **Event Creation Endpoint**
    -   **POST** `/events`: Create a new event associated with a job, useful for logging and tracking purposes.

 These endpoints collectively support a robust system for handling requests, managing jobs, and logging events within the Drumpler framework. They allow for a versatile set of operations from simple retrieval and submission of requests to detailed job management and event logging, making it suitable for a wide range of applications in workflow automation and data processing.

## Using the framework - Drumpler

To create a `Drumpler` RESTful server, the following is a sample implementation:

```
import os
import drumpler		# requires pip install Drumpler

# Configuration values can be hardcoded, loaded from an environment variable, or loaded from a .env file manually

# Uncomment these two lines if you are using .env file
#from dotenv import load_dotenv	# requires pip install python-dotenv
#load_dotenv('.env')  # Optional but highly recommended

authorization_key = os.getenv('AUTHORIZATION_KEY', 'default_key')
host = os.getenv('DRUMPLER_HOST', 'http://127.0.0.1')
port = int(os.getenv('DRUMPLER_PORT', 5000))
debug = os.getenv('DRUMPLER_DEBUG', 'True').lower() in ['true', '1', 't']
database_uri = os.getenv('DATABASE_URI', 'sqlite:///myproject.db')

# Create an instance of Drumpler with the specified configuration
drumpler_instance = drumpler.Drumpler(authorization_key, host, port, debug, database_uri)
app = drumpler_instance.app

if __name__ == "__main__":
	app.run()
```

## Request and Job Handling

### Authorization and Request Logging

-   **Unauthorized Requests**: Requests that are missing the required `Authorization` key are **not captured** in the `requests` table, ensuring that only authenticated interactions are logged and processed.
-   **Request Logging**: All requests that include the required header(s) and payload are recorded in the `requests` table, irrespective of their content.
-   **Job Creation**: Only requests that include a `custom_value` parameter will spawn a new job record. This parameter is indicative of a need for additional processing by the Mammoth component, which handles asynchronous tasks.

## Database Schemas
### Requests Table
| Field        | Type        | Description                                |
|--------------|-------------|--------------------------------------------|
| id           | Integer     | Primary key                                |
| timestamp    | DateTime    | Timestamp when the request was received    |
| source_ip    | String(128) | IP address of the requester                |
| user_agent   | String(256) | User agent of the requester's device       |
| method       | String(8)   | HTTP method used                           |
| request_url  | String(256) | URL of the request                         |
| request_raw  | Text        | Raw data of the request                    |
| custom_value | String(256) | Custom data for triggering additional jobs |
| is_handled   | Integer     | Flag indicating if the request has been handled |

### Jobs Table
| Field          | Type          | Description                                  |
|----------------|---------------|----------------------------------------------|
| id             | Integer       | Primary key                                  |
| request_id     | Integer       | Foreign key linking to the Requests table    |
| created_date   | DateTime      | Creation timestamp                           |
| modified_date  | DateTime      | Timestamp of last modification               |
| finished_date  | DateTime      | Completion timestamp (if any)                |
| status         | String        | Current status of the job                    |
| events         | Relationship  | Link to associated events                    |

### Events Table
| Field     | Type      | Description                                |
|-----------|-----------|--------------------------------------------|
| id        | Integer   | Primary key                                |
| job_id    | Integer   | Foreign key linking to the Jobs table      |
| timestamp | DateTime  | Timestamp when the event was recorded      |
| message   | Text      | Description or message of the event        |


## TLDR

 - `Drumpler` is a framework for rapidly developing secure RESTful APIs using flask-postgres
	 - **Drumpler** records incoming HTTP requests and requires **three** variables from the end end user
		 - **Bearer Token: authorization key** - requests without this key will be ignored
		 - **request_raw** - put your desired payload here. This can be utilized by Mammoth(s) to do something meaningful or you can just simply store some data.
		 - **custom_value** - this will be utilized by Mammoth(s) to request specific jobs.
	 - **Mammoth** fetches pending jobs **from Drumpler** and **exposes a method** for some developer to implement their desired workflow(s) 
		 - Mammoth is designed to automatically handle all communications with Drumpler so the end user can simply focus on processing the desired payload.

## Sample Mammoth implementation

To create a `Mammoth` (job-processor), the following is a sample implementation:
```
import  os
from  drumpler_mammoth  import  Mammoth

# comment 3 lines below if not using .env file
from dotenv import load_dotenv #pip install python-dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Optional: Offline-logging mechanism is also shipped with Mammoth, feel free to use it
#mammoth  =  None  # This global variable can be shared among all scopes

def  custom_process_function(request) -> bool:
  # I shall write my custom job-processing logic here
  
  # offline logging
  #mammoth.logger.info(f"I could utilize mammoth's logger for <info> messages") #optional
  #mammoth.logger.error(f"I could utilize mammoth's logger for <error> messages") #optional
  
  # online logging
  #mammoth.insert_event(request.job_id, "My event message goes here")
  
  # I shall return True in a success-scenario or 	# => job.status = 'Completed'
  # I shall return False in a failure-scenario	# => job.status = 'Error'
  
  pass

if  __name__  ==  "__main__":
  # the constructor parameters are MANDATORY
  drumpler_host  =  os.environ.get("DRUMPLER_HOST", "localhost")
  authorization_key  =  os.environ.get("AUTHORIZATION_KEY", "AUTH_KEY_HERE")
  custom_value  =  "ApplicationName"
  num_workers  =  None  # None implies os.cpu_count(), otherwise you can manually specify
  
  # initialize mammoth
  mammoth  =  Mammoth(drumpler_url=drumpler_host, authorization_key=authorization_key, custom_value=custom_value,   process_request_data=custom_process_function, num_workers=num_workers)
  
  print("Starting Mammoth... Press CTRL+C to stop.")
  
  try:
      mammoth.run()
  except  KeyboardInterrupt:
      print("Shutdown signal received")
      mammoth.stop()
      print("Mammoth application stopped gracefully")
```

Please visit [Mammoth's repository](https://github.com/KarelOmab/Drumpler-Mammoth) to learn more about it.

## Contributing
Contributions to `Drumpler` are welcome! Please follow the standard fork-branch-PR workflow.

## License
This project is licensed under the MIT License - see the LICENSE file for details.