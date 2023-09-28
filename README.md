# ASGrab

## Introduction

A python script to scan(with zmap), probe(with zmap & lzr) or grab scalable web pages with zmap, lzr and zgrab2.

LZR was modified to output port info in -feedZGrab mode.

ZGrab2 was modified to grab content on different ports in one round.

## Iptables filter

Add a rule to drop RST(out):

```
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s $(source-ip) -j DROP
```

Check the line number of rule:

```
sudo iptables -L --line-numbers
```

Delete specific rule by line number:

```
sudo iptables -D OUTPUT <line_number>
```

## Resources

Use `awk` to convert specific IP set to IP ranges for ASGrab.

Extract CIDR:

```
awk 'NR>2 {print $4}' china_telecom.tsv > allowlist.txt
```

Convert IP range to CIDR and extract:

```
awk 'NR>3 {print $1,$2}' Shandong_Jinan.tsv | xargs netmask -c | sed 's/^[ \t]*//g' > allowlist.txt
```