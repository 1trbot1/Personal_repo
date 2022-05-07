#!/usr/bin/python3
############################################################
# Anzu Minukube Rollout: Debian                            #
# Version: 1.0                                             #
#                                                          #
############################################################
#=========================Imports===========================
from re import sub
import subprocess
import os
import requests
#========================Variables==========================
Platform_Architecture = subprocess.run(['dpkg --print-architecture'], shell=True, capture_output=True, text=True ).stdout.strip("\n")
Release = subprocess.run(['lsb_release -cs'], shell=True, capture_output=True, text=True ).stdout.strip("\n")
Docker_Repo = f"deb [arch={Platform_Architecture} signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu {Release} stable \n"
Docker_Prerequisite_Packages = ["ca-certificates", "curl", "gnupg", "lsb-release"]
Docker_Packages = [ "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin" ]
#========================Functions==========================
def Package_Install(Packages):
    subprocess.run([f'apt update -y'],shell=True)
    for Package in Packages:
        print(f"\n Installing: {Package} \n")
        subprocess.run([f'apt install {Package} -y'],shell=True)
def Docker_Install():
    # Check if Docker Installed
    if not os.path.isfile("/usr/bin/docker"):
        # Install Prerequisite Packages
        Package_Install(Docker_Prerequisite_Packages)
        # Check If Docker Repo GPG Key Exist
        if not os.path.isfile("/usr/share/keyrings/docker-archive-keyring.gpg"):
            # Add Docker's Repository GPG Key
            subprocess.run([f'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg'],shell=True)
        # Add Docker Repository
        with open("/etc/apt/sources.list.d/docker.list", "w+") as Docker_Repo_File:
            Docker_Repo_File.write(Docker_Repo)
        # Install Docker
        Package_Install(Docker_Packages)
def Minikube_Install():
    # Check If Minikube Installed
    if not os.path.isfile("/usr/bin/minikube"):
        # Download Minikube Installer Package
        Package_File = requests.get("https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb")
        open("/tmp/minikube_install.deb", "wb").write(Package_File.content)
        # Install Minikube Package
        subprocess.run([f'dpkg -i /tmp/minikube_install.deb'],shell=True)
        # Run Minikube Start
        subprocess.run(['minikube start --force --driver=docker'])
        # Check If Kubernetes Repo GPG key exist
        if not os.path.isfile("/usr/share/keyrings/kubernetes-archive-keyring.gpg"):
            # Download Kubernetes Repo GPG key
            subprocess.run([f'curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg'],shell=True)
            # Add Kubernetes Repo
            with open("/etc/apt/sources.list.d/kubernetes.list", "w+") as Kubernete_Repo_File:
                Kubernete_Repo_File.write("deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main")
            # Install Kubectl
            Package_Install(["kubectl"])
def Prometeus_Deploy():
    pass

#==========================Main=============================
if __name__ == "__main__":
    Docker_Install()
    Minikube_Install()