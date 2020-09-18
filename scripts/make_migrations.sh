#!/bin/bash

if [ "$1" != "" ]; then
    alembic revision --autogenerate -m "$1"
else
    alembic revision --autogenerate
fi
