#!/bin/bash

# Configuration
HOST="http://localhost:5000"
AUTH_KEY="YourAuthorizationKeyHere"

# Function to create (POST) a new request
create_request() {
    curl -X POST "${HOST}/request" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${AUTH_KEY}" \
        -d '{
            "foo": "val1",
            "bar": 2,
            "flag": true
        }'
}

# Function to read (GET) a single request by ID
read_request() {
    local request_id=$1
    curl -X GET "${HOST}/request/${request_id}" \
        -H "Authorization: Bearer ${AUTH_KEY}"
}

# Function to update (PUT) the is_handled status of a specific request
update_request() {
    local request_id=$1
    curl -X PUT "${HOST}/request/${request_id}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${AUTH_KEY}" \
        -d '{"is_handled": 1}'
}

# Function to delete (DELETE) a specific request
delete_request() {
    local request_id=$1
    curl -X DELETE "${HOST}/request/${request_id}" \
        -H "Authorization: Bearer ${AUTH_KEY}"
}

# Uncomment the operation you want to perform and provide the necessary arguments
create_request
read_request 1
update_request 1
#delete_request 1
