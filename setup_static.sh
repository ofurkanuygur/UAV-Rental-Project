#!/bin/bash

# Create necessary directories
mkdir -p static/vendor/bootstrap/bootstrap-5.3.2-dist
mkdir -p static/vendor/jquery

# Download Bootstrap
curl -L https://github.com/twbs/bootstrap/releases/download/v5.3.2/bootstrap-5.3.2-dist.zip -o bootstrap.zip
unzip bootstrap.zip -d static/vendor/bootstrap/
mv static/vendor/bootstrap/bootstrap-5.3.2-dist/* static/vendor/bootstrap/bootstrap-5.3.2-dist/
rm bootstrap.zip

# Download jQuery
curl -L https://code.jquery.com/jquery-3.7.1.min.js -o static/vendor/jquery/jquery.min.js

# Run Django collectstatic
python manage.py collectstatic --noinput 