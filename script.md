# 1. Docker Setup Guide

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

## Step 4: Add Docker’s Official GPG Key

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

For more details, see the [official Docker documentation](https://docs.docker.com/engine/install/ubuntu/).

# 2. nvidia-container-toolkit Setup Guide

This guide will help you install the NVIDIA Container Toolkit, which enables Docker containers to utilize the GPU on your system.

## Prerequisites

- NVIDIA GPU with supported drivers installed
- Docker installed and running (see previous section)

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

- Ensure your NVIDIA drivers are up to date.
- If you encounter issues, see the [official NVIDIA Container Toolkit documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

# 3. NGC Model Download Setup Guide

This guide will help you set up NGC CLI and download the required pre-trained models for the Mask Grounding DINO project.

## Prerequisites

- Linux system (Ubuntu/Debian recommended)
- Internet connection
- NVIDIA NGC account (free registration required)

## Step 1: Create NGC Account

1. Go to [NVIDIA NGC](https://ngc.nvidia.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

## Step 2: Generate NGC API Key

1. Log into your NGC account
2. Go to [NGC Setup](https://ngc.nvidia.com/setup/api-key)
3. Click "Generate API Key"
4. **Important:** Copy and save your API key securely (you won't see it again)

## Step 3: Install NGC CLI

### Option A: Using wget (Recommended)
```bash
# Download NGC CLI
wget -O ngccli_linux.zip https://ngc.nvidia.com/downloads/ngccli_linux.zip

# Extract and install
unzip -o ngccli_linux.zip
chmod u+x ngc
sudo mv ngc /usr/local/bin/

# Clean up
rm ngccli_linux.zip
```

### Option B: Manual Download
1. Download from [NGC CLI Downloads](https://ngc.nvidia.com/downloads/ngccli_linux.zip)
2. Extract the zip file
3. Make executable: `chmod +x ngc`
4. Move to system path: `sudo mv ngc /usr/local/bin/`

## Step 4: Configure NGC CLI

```bash
# Configure NGC with your API key
ngc config set

# You'll be prompted for:
# - API Key: [paste your API key from Step 2]
# - CLI output format: ascii (default)
# - org: [leave blank for default]
# - team: [leave blank for default]
# - ace: [leave blank for default]
```

## Step 5: Verify Installation

```bash
# Check if NGC is working
ngc --version

# Test authentication
ngc config current
```

You should see your configuration details without errors.

## Step 6: Download Models

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/SegmaVisionProInference/inference/pre_trained_models/
   ```

2. **Make the download script executable:**
   ```bash
   chmod +x download_models.sh
   ```

3. **Run the download script:**
   ```bash
   ./download_models.sh
   ```

## What the Script Downloads

The script will download two models:

1. **Mask Grounding DINO**: `mask_grounding_dino_swin_tiny_commercial_trainable_v1.0`
2. **Grounding DINO**: `grounding_dino_swin_tiny_commercial_trainable_v1.0`

Both models will be saved as `.pth` files in the same directory as the script.

## Troubleshooting

### NGC CLI Not Found
If you get "command not found" errors:

1. **Restart your terminal** or VS Code completely
2. **Check if NGC is in PATH:**
   ```bash
   echo $PATH | grep -o '/usr/local/bin'
   ```
3. **Add to PATH manually:**
   ```bash
   echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Authentication Issues
If you get authentication errors:
```bash
# Reconfigure NGC
ngc config set

# Check current config
ngc config current
```

### Download Failures
- Ensure stable internet connection
- Check if your NGC account has access to TAO models
- Verify API key is correct

## Expected Output

When successful, you should see:
```
✓ Mask Grounding DINO model saved to: /path/to/grounding_dino_swin_tiny_commercial_trainable.pth
✓ Grounding DINO model saved to: /path/to/grounding_dino_swin_tiny_commercial_trainable.pth
All downloads complete!
```

## File Structure After Download

```
pre_trained_models/
├── download_models.sh
├── grounding_dino_swin_tiny_commercial_trainable.pth
└── [another_model_file].pth
```

## Next Steps

After successful download, you can use these models in your training configuration by updating the `pretrained_model_path` in your `train.yaml` file to point to the downloaded models.

## Support

- [NGC Documentation](https://docs.nvidia.com/ngc/)
- [NGC CLI User Guide](https://docs.nvidia.com/ngc/ngc-cli-user-guide/index.html)
- [TAO Toolkit Documentation](https://docs.nvidia.com/tao/tao-toolkit/)

# 4.  Pre-Docker Compose Checklist

Before running the Docker Compose project, ensure the following steps are completed:

## 1. Clone the Project Repository

If you haven't already, clone the SegmaVisionPro project to your local machine:

```bash
git clone https://github.com/your-org/SegmaVisionPro.git
cd SegmaVisionPro
```

## 2. Prepare Environment Files

Check if your project requires environment variables (e.g., `.env` file). If so:

- Copy the example file if provided:
   ```bash
   cp .env.example .env
   ```
- Edit `.env` and update values as needed.

## 3. Download Required Models

Follow the instructions in the "NGC Model Download Setup Guide" above to ensure all necessary pre-trained models are downloaded and placed in the correct directory.

## 4. Verify GPU Access (If Needed)

If your project uses GPU acceleration, confirm that Docker can access your GPU:

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi
```

## 5. Check Docker Compose Installation

Ensure Docker Compose is installed and available:

```bash
docker compose version
```

## 6. (Optional) Build Docker Images

If your `docker-compose.yml` requires building images locally:

```bash
docker compose build
```

## 7. Review and Update Configuration

- Review `docker-compose.yml` for any paths, ports, or volumes that may need adjustment for your environment.
- Ensure any required data directories exist and have correct permissions.

Once these steps are complete, you can proceed to run your Docker Compose project.