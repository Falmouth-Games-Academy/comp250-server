# comp250-server

## Setup (on Ubuntu)

Install Oracle Java:
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```

Install required packages:
```
sudo apt-get install python3-pip python3-twisted python3-dateutil mongodb git ant curl libcap2-bin
pip3 install flask pymongo
```

Allow the server to listen on port 80 without root access (see https://serverfault.com/a/394136):
```
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.6
```

Clone and build MicroRTS:
```
git clone https://github.com/Falmouth-Games-Academy/comp250-microrts.git
cd comp250-microrts
ant clean build jar
cd ..
```

Create empty directories for the tournament:
```
mkdir tournament
mkdir tournament/matches
```

Clone the server:
```
git clone https://github.com/Falmouth-Games-Academy/comp250-server.git
cd comp250-server
./get_allowed_users.sh
```

If you are not edpowley, you will need to edit the username in `get_allowed_users.sh` before running it.
Also `get_allowed_users.sh` will need rewriting when `Falmouth-Games-Academy` has more than 100 members,
as this is the maximum number of records that the GitHub API will return at once.

Run the server:
```
./run_all.sh
```

Stop the server:
```
./stop_all.sh
```
