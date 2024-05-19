# CTF-KickStart
A python script to automate some of the recon I always do at the beginning of CTFs. It runs [Rustscan](https://github.com/RustScan/RustScan) on all ports and a service and version (`-sC -sV`) scan on open ports. If you don't want to to use Rustscan, Nmap can be used instead. If any ports are found to be running HTTP(S), it will add the domain name to `/etc/hosts` and run [Feroxbuster](https://github.com/epi052/feroxbuster) on them. It will the run a subdomain scan with [Gobuster](https://github.com/OJ/gobuster), add any found subdomains to `/etc/hosts` and run Feroxbuster on them.

This is a pretty simple script, and isn't aimed at going super in depth the way something like [TireFire](https://github.com/CoolHandSquid/TireFire) does. This just takes the things I almost always do at the beginning of a ctf and automates them.

### Requirements
This script requires, [Rustscan](https://github.com/RustScan/RustScan), Nmap, [Feroxbuster](https://github.com/epi052/feroxbuster), and [Gobuster](https://github.com/OJ/gobuster) to be installed.

Rustscan should be installed using the [Docker method](https://github.com/RustScan/RustScan/wiki/Installation-Guide)

### Wordlists
This script also assumes you have [Seclists](https://github.com/danielmiessler/SecLists) installed in `/usr/share/seclists`, though a different directory can be specified.

By default, directory busting uses the [raft-medium-directories.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/raft-medium-directories.txt) wordlist, and subdomain scanning uses the [subdomains-top1million-20000.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-20000.txt) wordlist, but these can both be changed.

### Usage
```
```