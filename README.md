To run:

cd into both directories(server and proxy) in sepearte terminal sessions.
Run the server.py and proxy.py using python2.7


For browser:
set all proxy protocols to go through localhost port 12345


For terminal
export http_proxy=localhost:12345
export https_proxy=localhost:12345

(Make sure to unset all other proxy. Possibly using proxy_off function(if written) )

