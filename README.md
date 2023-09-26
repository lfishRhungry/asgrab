# ASGrab

## Introduction

A python script to scan(with zmap), probe(with zmap & lzr) or grab scalable web pages with zmap, lzr and zgrab2.

LZR was modified to output port info in -feedZGrab mode.

ZGrab2 was modified to grab content on different ports in one round.

## Resources

Use `awk` to convert specific IP set to IP ranges for ASGrab:

```
awk '{print $4}' china_telecom.tsv > allowlist.txt
```