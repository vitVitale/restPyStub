#!/bin/bash

HOST="0.0.0.0"
uvicorn app.$(echo "$TYPE" | tr '[:upper:]' '[:lower:]'):app --host ${HOST} --port ${PORT}