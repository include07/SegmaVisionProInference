# Pre-Deployment Checklist

Before running the Docker Compose project, ensure the following steps are completed:

## Prerequisites Verification

```{admonition} Important
Complete all setup steps before proceeding with deployment to avoid issues.
```

### 1. System Requirements

- [ ] **Operating System**: Ubuntu 20.04 or later
- [ ] **Memory**: At least 8GB RAM (16GB recommended)
- [ ] **Storage**: At least 20GB free space
- [ ] **Network**: Stable internet connection for downloads

### 2. Docker Setup

- [ ] **Docker Engine** installed and running
- [ ] **Docker Compose** plugin installed
- [ ] **User permissions** configured (user in docker group)

**Verification:**
```bash
docker --version
docker compose version
docker run hello-world
```

### 3. GPU Support (Optional but Recommended)

- [ ] **NVIDIA GPU** with compatible drivers
- [ ] **NVIDIA Container Toolkit** installed and configured
- [ ] **GPU access** verified in Docker

**Verification:**
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi
```

### 4. NGC CLI Setup

- [ ] **NGC account** created and verified
- [ ] **NGC CLI** installed and configured
- [ ] **API key** generated and configured
- [ ] **Pre-trained models** downloaded

**Verification:**
```bash
ngc --version
ngc config current
ls inference/pre_trained_models/*.pth
```

## Project Setup

### 1. Clone the Repository

If you haven't already, clone the SegmaVisionPro project:

```bash
git clone https://github.com/your-org/SegmaVisionPro.git
cd SegmaVisionPro
```

### 2. Environment Configuration

Check if your project requires environment variables:

- [ ] Copy example environment file (if exists):
   ```bash
   cp .env.example .env
   ```
- [ ] Edit `.env` file with your specific configuration
- [ ] Verify all required environment variables are set

### 3. Directory Structure

Ensure the following directories exist with proper permissions:

- [ ] `backend/uploads/` - for file uploads
- [ ] `backend/output/` - for training outputs
- [ ] `inference/pre_trained_models/` - for model files

```bash
# Create directories if they don't exist
mkdir -p backend/uploads backend/output
mkdir -p inference/pre_trained_models

# Set proper permissions
chmod 755 backend/uploads backend/output
```

### 4. Model Files

- [ ] **Pre-trained models** downloaded via NGC CLI
- [ ] **Model files** placed in correct directory
- [ ] **File permissions** set correctly

**Expected files:**
```
inference/pre_trained_models/
├── download_models.sh
├── grounding_dino_swin_tiny_commercial_trainable.pth
└── mask_grounding_dino_swin_tiny_commercial_trainable.pth
```

### 5. Configuration Files

Review and update configuration files as needed:

- [ ] **docker-compose.yml** - ports, volumes, environment
- [ ] **backend/requirements.txt** - Python dependencies
- [ ] **frontend/package.json** - Node.js dependencies
- [ ] **inference/specs/*.yaml** - model training/inference configs

## Pre-Deployment Tests

### 1. Build Docker Images (Optional)

If your `docker-compose.yml` requires building images locally:

```bash
docker compose build
```

### 2. Network Configuration

- [ ] **Ports available**: Check that required ports (usually 3000, 8000) are not in use
- [ ] **Firewall rules**: Ensure Docker can access the internet for downloads

```bash
# Check if ports are available
netstat -tuln | grep -E ':(3000|8000|5000)'
```

### 3. Volume Mounts

- [ ] **Host directories exist** and have proper permissions
- [ ] **Docker can access** mounted volumes
- [ ] **No conflicts** with existing containers

## Final Checklist

Before running `docker compose up`:

- [ ] All prerequisites completed
- [ ] Environment variables configured
- [ ] Model files downloaded and in place
- [ ] Required directories created
- [ ] Docker and GPU access verified
- [ ] Network ports available
- [ ] Configuration files reviewed

## Troubleshooting

If you encounter issues during setup:

1. **Check system logs**: `journalctl -u docker`
2. **Verify permissions**: `ls -la` on project directories
3. **Test components individually**: Run each service separately
4. **Review documentation**: Check specific setup guides for each component

## Next Steps

Once all items are checked:

1. You're ready to deploy SegmaVisionPro!
2. Use `docker-compose up -d` to start all services
3. Access the web interface at `http://localhost:3000`

## Getting Help

If you encounter issues:

- Review the troubleshooting sections in each setup guide
- Check the logs: `docker-compose logs [service-name]`
- Create an issue on [GitHub](https://github.com/your-org/SegmaVisionPro/issues)
