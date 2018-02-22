# comp250-server

## Setup (on Ubuntu)

```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer

sudo apt-get install python3-pip python3-twisted mongodb git ant
pip3 install flask pymongo

sudo ufw enable
sudo ufw allow 8000

git clone https://github.com/Falmouth-Games-Academy/comp250-microrts.git
cd comp250-microrts
ant clean build jar
cd ..

mkdir tournament
mkdir tournament/matches

git clone https://github.com/Falmouth-Games-Academy/comp250-server.git
```

Now go into `comp250-server` and run `./run_server.sh` and `python3 run_matches.py`.

