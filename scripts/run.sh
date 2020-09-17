#!/bin/bash

gunicorn -w 4 -k uvicorn.workers.UvicornWorker --log-level warning school_picker_starlette_server.app:app
