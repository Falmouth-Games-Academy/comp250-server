#!/bin/bash

curl -u "edpowley" https://api.github.com/orgs/Falmouth-Games-Academy/members?per_page=100 >allowed_users.json
