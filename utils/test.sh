sudo ./zmap -w ../allowlist.txt -b ../blocklist.txt -p 80 --output-filter="success = 1 && repeat = 0" -f "saddr,daddr,sport,dport,seqnum,acknum,window" -O json -i ens33 -S 192.168.0.159 -G d4:da:21:5d:d8:38 | \
sudo ./lzr --handshakes http,tls -sendInterface ens33 -gatewayMac d4:da:21:5d:d8:38 -f lzr_results.json -feedZGrab | \
./zgrab2 multiple -c ./multi.ini -o grab_results.json
#60.30.0.0/16
