# NVIDIA Container Toolkit Setup Guide

This guide will help you install the NVIDIA Container Toolkit, which enables Docker containers to utilize the GPU on your system.

## Prerequisites

- NVIDIA GPU with supported drivers installed
- Docker installed and running (see [Docker Setup Guide](docker-setup.md))

## Step 1: Set Up the Package Repository

```bash
# Add the package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
   sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
   sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

## Step 2: Install NVIDIA Container Toolkit

```bash
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

## Step 3: Configure Docker to Use the NVIDIA Runtime

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Step 4: Test the Installation

Run the following command to verify that Docker can access the GPU:

```bash
sudo docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi
```

You should see the output of `nvidia-smi` showing your GPU details.

## Troubleshooting

### Common Issues

1. **NVIDIA drivers not installed or outdated**
   - Ensure your NVIDIA drivers are up to date
   - Check driver version: `nvidia-smi`

2. **Docker not restarted after installation**
   - Restart Docker service: `sudo systemctl restart docker`

3. **Permission issues**
   - Ensure your user is in the docker group: `sudo usermod -aG docker $USER`
   - Log out and back in, or run: `newgrp docker`

### Verification Commands

```bash
# Check NVIDIA driver version
nvidia-smi

# Check Docker can access GPU
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi

# Test with a simple CUDA container
docker run --rm --gpus all nvidia/cuda:12.0.0-devel-ubuntu20.04 nvcc --version
```

## Next Steps

After setting up the NVIDIA Container Toolkit:
- [Configure NGC CLI](ngc-setup.md) for downloading pre-trained models
- [Review the pre-deployment checklist](pre-deployment-checklist.md)

## Additional Resources

- [Official NVIDIA Container Toolkit documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [NVIDIA Container Toolkit GitHub](https://github.com/NVIDIA/nvidia-container-toolkit)
