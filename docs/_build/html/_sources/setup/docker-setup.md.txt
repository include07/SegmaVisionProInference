# Docker Setup Guide

This section will guide you through installing Docker on Ubuntu and setting it up for use.

## Prerequisites

- Ubuntu 20.04 or later (other distributions may require different steps)
- Sudo privileges

## Step 1: Uninstall Old Versions (Optional)

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

## Step 2: Update Package Index

```bash
sudo apt-get update
```

## Step 3: Install Required Packages

```bash
sudo apt-get install \
   ca-certificates \
   curl \
   gnupg \
   lsb-release
```

## Step 4: Add Docker's Official GPG Key

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

## Step 5: Set Up the Docker Repository

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## Step 6: Install Docker Engine

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Step 7: Verify Docker Installation

```bash
sudo docker run hello-world
```

You should see a message confirming Docker is installed and working.

## Step 8: Manage Docker as a Non-root User (Optional)

1. Add your user to the `docker` group:
   ```bash
   sudo usermod -aG docker $USER
   ```
2. Log out and log back in, or run:
   ```bash
   newgrp docker
   ```
3. Test Docker without `sudo`:
   ```bash
   docker run hello-world
   ```

## Step 9: Install Docker Compose Plugin

Docker Compose is now included as a plugin for Docker Engine. If you installed Docker using the steps above, the plugin should already be installed. To verify or install it manually:

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

Check the installation:

```bash
docker compose version
```

You should see the Docker Compose version output.

## Useful Commands

- Check Docker version: `docker --version`
- Start Docker service: `sudo systemctl start docker`
- Enable Docker on boot: `sudo systemctl enable docker`
- Check Docker status: `sudo systemctl status docker`

## Next Steps

After installing Docker, proceed to:
- [NVIDIA Container Toolkit Setup](nvidia-toolkit.md) (for GPU support)
- [NGC CLI Setup](ngc-setup.md) (for downloading pre-trained models)

## Additional Resources

For more details, see the [official Docker documentation](https://docs.docker.com/engine/install/ubuntu/).
