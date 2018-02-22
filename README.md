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

git clone https://github.com/Falmouth-Games-Academy/comp250-server.git

cd comp250-server
./run_server.sh
```

## Setup (on Windows -- no longer supported)

* Install prerequisites:
	* Python 3.x
	* MongoDB community edition
	* Git command-line tools
	* Java JDK version 1.8
	* Apache Ant (unzip `apache-ant-1.10.1` to the `..` directory relative to the server scripts)
* `pip install` required packages:
	* `flask`
	* `Twisted`
	* `Twisted[windows_platform]`
	* `pymongo`
* Execute `run_mongod.bat`
* Execute `run_server.bat`

## References

For `run_server.bat`:
* http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/
* https://stackoverflow.com/questions/40012956/flask-app-is-not-start-over-twisted-16-4-x-as-wsgi
* https://github.com/robgjansen/onionperf/issues/26

