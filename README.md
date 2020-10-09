# CC-Project
Project for Computer Communications subject

### Installing 

> Default Virtual Environment instalation

```bash
python3 -m venv ccproject-env

# Windows
ccproject-env\Scripts\activate.bat

# Unix / MacOS
source ccproject-env/bin/activate

pip install -r requirements.txt
```

### Executing

```
python3 src/anon_gw.py [options]
```

#### Options
```
-target-server
    Targeted server that this protocol is operating on.

-port
    TCP receive port (Usually is the default port of the protocol using TCP).

-overlay-peers
    Overlay peers (IPv4 of nodes running instances of AnonGW). This argument must be the last and parses every string in front of it as IPv4
```