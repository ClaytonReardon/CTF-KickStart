#!/usr/bin/env python3
#
# A python script to automate some of the recon I always do at the beginning of CTFs
# This script will run RustScan or Nmap to scan all ports, then run service and version enumeration on open ports
# It will then run Feroxbuster on any http(s) ports, as well as any subdomains found using Gobuster
#
import os
import re
import argparse
import subprocess
import requests
import time

# Set color codes. All colors have reset code at beginning to simplify script
grn = "\033[0m\033[0;32m"
bldgrn = "\033[0m\033[1;32m"
orng = "\033[0m\033[3;33m"
italic = "\033[0m\033[3m"
rst = "\033[0m"


# █▄█ █▀█ ▀█▀ █▀█   █▀▀ █ █ █▀█ █▀▀ ▀█▀ ▀█▀ █▀█ █▀█
# █ █ █▀█  █  █ █   █▀▀ █ █ █ █ █    █   █  █ █ █ █
# ▀ ▀ ▀ ▀ ▀▀▀ ▀ ▀   ▀   ▀▀▀ ▀ ▀ ▀▀▀  ▀  ▀▀▀ ▀▀▀ ▀ ▀
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--machine", help="Machine name")
    parser.add_argument("-i", "--ip", help="IP address")
    parser.add_argument("-n", "--nmap", help=f"Use Nmap for scanning {italic}(Rustscan is used by default, which is faster, and designed for CTFs){rst}", action="store_true")
    parser.add_argument("-a", "--auto", help="Automatically give default answers to all prompts", action="store_true")
    parser.add_argument("--no-ping", help=f"Skip pinging the machine to check if it is online {italic}(for testing purposes){rst}", action="store_true")
    args = parser.parse_args()

    # Check if machine and ip arguments are provided
    if not args.machine or not args.ip:
        print(f"{orng}Error: Machine and IP arguments are required\n{rst}")
        parser.print_help()
        exit(1)

    # Set variables
    machine = args.machine
    ip = args.ip
    auto = args.auto

    # Create directory structure and note files
    os.makedirs(f"{machine}/notes", exist_ok=True)
    os.makedirs(f"{machine}/www", exist_ok=True)
    os.makedirs(f"{machine}/notes/Screenshots", exist_ok=True)
    open(f"{machine}/notes/WriteUp.md", "w").close()
    open(f"{machine}/notes/portscan.md", "w").close()

    # Send pings to check if machine is online
    print(f"{grn}Pinging {bldgrn}{ip}{grn} to check if machine is online...")
    print(f"{grn}Pings Received: ", end='', flush=True)
    ping_count = 0
    while ping_count < 10:
        response = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if "1 packets transmitted, 1 received" in response.stdout.decode():
            ping_count += 1
            print(f"{bldgrn}{ping_count} ", end='', flush=True)
        time.sleep(1)
    print()

    # Run Nmap or RustScan depending on the --nmap argument
    if args.nmap:
        nmap_scan(ip, machine)
    else:
        rust_scan(ip, machine)
    
    # Add portscan.md to variable
    with open(f"{machine}/notes/portscan.md", "r") as file:
        portscan = file.read()

    # Extract the Port numbers and protocols of http(s) ports
    http_ports = re.findall(r'(\d+)/.*?(http|https)', portscan)

    # Run Feroxbuster on any http(s) ports
    for port, protocol in http_ports:
        if not auto:
            choice = input(f"\n{grn}Run Feroxbuster on port {bldgrn}{port}{grn}? (Y/n)") or "Y"
        else:
            print(f"\n{grn}Run Feroxbuster on port {bldgrn}{port}{grn}? (Y/n): {bldgrn}Y")
            choice = "Y"
        
        if choice.lower() == "y":
            if not auto:
                domain = input(f"{grn}Enter domain name ({bldgrn}{machine}.htb{grn}): ") or (f"{machine}.htb")
            else:
                print(f"{grn}Enter domain name: ")
                domain = (f"{machine}.htb")
        
            feroxbuster(http_ports, ip, machine, domain, protocol, port)

    # Run subdomain scan on any http(s) ports
    for port, protocol in http_ports:
        if not auto:
            choice = input(f"\n{grn}Run Subdomain scan on {bldgrn}{domain}{grn} port {bldgrn}{port}{grn}? (Y/n): ") or "Y"
        else:
            print(f"\n{grn}Run Subdomain scan on {bldgrn}{domain}{grn} port {bldgrn}{port}{grn}? (Y/n): {bldgrn}Y")
            choice = "Y"
        if choice.lower() == "y":
            vhost_scan(http_ports, ip, machine, domain, protocol, port, auto)


# █▀▄ █ █ █▀▀ ▀█▀ █▀▀ █▀▀ █▀█ █▀█
# █▀▄ █ █ ▀▀█  █  ▀▀█ █   █▀█ █ █
# ▀ ▀ ▀▀▀ ▀▀▀  ▀  ▀▀▀ ▀▀▀ ▀ ▀ ▀ ▀
def rust_scan(ip, machine):
    # Run RustScan to scan all ports
    print(f"\n{grn}Running RustScan on {bldgrn}{ip}{grn}...\n")
    
    # set rustscan command
    rustscan = f"sudo docker run -it --rm --name rustscan -v {os.getcwd()}/{machine}/notes:/notes rustscan/rustscan"
    
    # Allow rustscan to write to notes directory
    os.system(f"chmod -R 777 {machine}/notes")
    subprocess.run(f"{rustscan} -a {ip} -- -sC -sV -oN /notes/portscan.md ", shell=True)

    # Revert notes directory permissions
    os.system(f"chmod -R 755 {machine}/notes")


# █▀█ █▄█ █▀█ █▀█   █▀▀ █▀▀ █▀█ █▀█
# █ █ █ █ █▀█ █▀▀   ▀▀█ █   █▀█ █ █
# ▀ ▀ ▀ ▀ ▀ ▀ ▀     ▀▀▀ ▀▀▀ ▀ ▀ ▀ ▀
def nmap_scan(ip, machine):
    print(f"\n{grn}Running Nmap on all ports on {bldgrn}{ip}{grn}...\n")

    # Run Nmap on all ports
    process = subprocess.Popen(f"sudo nmap -v -p- --min-rate=1000 -T4 {ip}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Save Nmap output to all_ports and print to STDOUT
    all_ports = ""
    while True:
        output = process.stdout.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            all_ports += output
    rc = process.poll()

    # Run Nmap with -sC & -sV on open ports
    print(f"\n{grn}Running Nmap on open ports on {ip}...\n")

    # Extract open ports from all_ports
    open_ports = ",".join(re.findall(r'(\d+)/tcp open', all_ports))
    subprocess.run(f"sudo nmap -sC -sV -p{open_ports} {ip} -oN {machine}/notes/portscan.md", shell=True)


# █▀▄ ▀█▀ █▀▄ █▀▀ █▀▀ ▀█▀ █▀█ █▀▄ █ █   █▀▄ █ █ █▀▀ ▀█▀
# █ █  █  █▀▄ █▀▀ █    █  █ █ █▀▄  █    █▀▄ █ █ ▀▀█  █ 
# ▀▀  ▀▀▀ ▀ ▀ ▀▀▀ ▀▀▀  ▀  ▀▀▀ ▀ ▀  ▀    ▀▀  ▀▀▀ ▀▀▀  ▀ 
def feroxbuster(http_ports, ip, machine, domain, protocol, port):
    # Run Feroxbuster on any http(s) ports
    print(f"\n{grn}Directory Busting on {bldgrn}{domain}{grn}...\n")

    for port, protocol in http_ports:
            # Add domain to /etc/hosts
            subprocess.run(f"sudo bash -c 'echo {ip} {domain} >> /etc/hosts'", shell=True)

            # Set feroxbuster options
            options = (f"-k -n -o {machine}/notes/{domain}_port-{port}.md")

            # Fuzz for different extensions & add to Feroxbuster options
            extensions = ['html', 'php', 'asp', 'aspx']
            for ext in extensions:
                try:
                    response = requests.get(f"{protocol}://{domain}:{port}/index.{ext}")
                    if response.status_code == 200:
                        options += f" -x {ext}"
                        break
                except requests.exceptions.RequestException:
                    pass
            
            # Run feroxbuster
            subprocess.run(f"feroxbuster -u {protocol}://{domain}:{port} {options}", shell=True)


#  █▀▀ █ █ █▀▄ █▀▄ █▀█ █▄█ █▀█ ▀█▀ █▀█   █▀▀ █▀▀ █▀█ █▀█
#  ▀▀█ █ █ █▀▄ █ █ █ █ █ █ █▀█  █  █ █   ▀▀█ █   █▀█ █ █
#  ▀▀▀ ▀▀▀ ▀▀  ▀▀  ▀▀▀ ▀ ▀ ▀ ▀ ▀▀▀ ▀ ▀   ▀▀▀ ▀▀▀ ▀ ▀ ▀ ▀
def vhost_scan(http_ports, ip, machine, domain, protocol, port, auto):
    # Scan for subdomains using Gobuster
    print(f"\n{grn}Scanning Subdomains on {bldgrn}{domain}{grn}...\n")
    
    for port, protocol in http_ports:
        wordlist = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt"
        options = "--append-domain --random-agent -k --threads 40 --no-color"
        subprocess.run(f"gobuster vhost -u {protocol}://{domain}:{port} -w {wordlist} -o {machine}/notes/subdomains.md {options}", shell=True)
    
    # Extract subdomains from the Gobuster output
    with open(f"{machine}/notes/subdomains.md", "r") as file:
        sub_names = file.read()
    subdomains = re.findall(r'\b\w+\.\w+\.\w+\b', sub_names)
    
    # Send found subdomains to Feroxbuster
    for subdomain in subdomains:
        if not auto:
            choice = input(f"\n{grn}Run Feroxbuster on found subdomain {bldgrn}{subdomain}{grn}? (Y/n): ") or "Y"
        else:
            print(f"\n{grn}Run Feroxbuster on found subdomain {bldgrn}{subdomain}{grn}? (Y/n): {bldgrn}Y")
            choice = "Y"
        if choice.lower() == "y":
            feroxbuster(http_ports, ip, machine, subdomain, protocol, port)
    
if __name__ == "__main__":
    main()