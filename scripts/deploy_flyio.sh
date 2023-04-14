#!/bin/bash

# This script is used to deploy the the plugin as a fly.io app
# Must read firt!
# https://github.com/openai/chatgpt-retrieval-plugin/blob/main/docs/deployment/flyio.md

# login
flyctl auth login

flyctl launch

flyctl secrets set OPENAI_API_KEY=$OPENAI_API_KEY \
    WEAVIATE_HOST=$WEAVIATE_HOST \
    ENV=prod \
    BEARER_TOKEN=$BEARER_TOKEN

# deploy the app
flyctl deploy