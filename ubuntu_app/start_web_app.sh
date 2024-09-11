#!/bin/bash

acquisition_url="http://127.0.0.1:5000"
site_url="http://localhost:8000"

check_site_active() {
    if curl -s --head --request GET "$site_url" | grep "200 OK" > /dev/null; then
        return 0 # Site is active
    else
        return 1 # site is not active
    fi
}

# loop unitl the site becomes active
while ! check_site_active; do
    echo "not active"
    sleep 1
done

echo "open firefox with woodbod"
firefox --new-window "$site_url"