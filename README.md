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
usage: KickStart.py [-h] [-m MACHINE] [-i IP] [-n] [-a] [-s SECLISTS] [-dw DIRECTORY_WORDLIST] [-sw SUBDOMAIN_WORDLIST] [--no-ping]

options:
  -h, --help                                show this help message and exit
  -m MACHINE, --machine MACHINE             Machine name
  -i IP, --ip IP                            IP address
  -n, --nmap                                Use Nmap for scanning (Rustscan is used by default, which is faster, and designed for CTFs)
  -a, --auto                                Automatically give default answers to all prompts
  -s SECLISTS, --seclists SECLISTS          Path to SecLists directory (default: /usr/share/seclists)
  -dw WORDLIST, --dir-wordlist WORDLIST     Path to directory wordlist (default: /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt)
  -sw WORDLIST, --sub-wordlist WORDLIST     Path to subdomain wordlist (default: /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt)
  --no-ping                                 Skip pinging the machine to check if it is online (for testing purposes)
```