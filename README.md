

# service-hub
This service will listen on a specific local port and redirect the incoming raw traffic to the host and ports listed on a file (peer.lst). Doesn't handle peer's response.

### peer.lst

Should have a list of ip/hostname port like:
```
localhost 1234
192.168.0.1 1234
```
### run it
```
python hub.py
```
### requires
python2.7 or later
