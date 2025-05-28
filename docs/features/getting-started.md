# Getting Started with SegmaVisionPro

This guide will walk you through cloning the SegmaVisionPro repository and getting the platform running using Docker Compose in just a few simple steps.

## Prerequisites

Before you begin, ensure you have completed the setup requirements:

- ✅ [Docker installed and running](../setup/docker-setup.md)
- ✅ [NVIDIA Container Toolkit configured](../setup/nvidia-toolkit.md) (for GPU support)
- ✅ [NGC CLI configured](../setup/ngc-setup.md) (for model downloads)
- ✅ [Pre-deployment checklist completed](../setup/pre-deployment-checklist.md)

## Step 1: Clone the Repository

Clone the SegmaVisionPro repository to your local machine:

```bash
# Clone the repository
git clone https://github.com/include07/SegmaVisionPro.git

# Navigate to the project directory
cd SegmaVisionPro
```

### Alternative: Download as ZIP

If you prefer not to use Git:

1. Visit the [SegmaVisionPro GitHub repository](https://github.com/include07/SegmaVisionPro)
2. Click the green "Code" button → "Download ZIP"
3. Extract the ZIP file to your desired location

## Step 2: Download Pre-trained Models

Before starting the Docker containers, you need to download the required AI models:

```bash
# Navigate to the models directory
cd inference/pre_trained_models/

# Make the download script executable and run it
chmod +x download_models.sh && ./download_models.sh

# Return to the main project directory
cd ../..
```

For detailed instructions and troubleshooting, see the [Model Download Guide](model-download.md).

## Step 3: Start with Docker Compose

SegmaVisionPro comes with pre-configured environment settings that work out-of-the-box. Simply start the application using Docker Compose:

```bash
# Start all services in detached mode
docker-compose up -d
```

This will start all the required services:
- **Backend API** (FastAPI) on port 8000
- **Frontend** (React) on port 3000
- **Database** (PostgreSQL) for data storage

## Step 4: Verify Installation

Check that all services are running:

```bash
# Check running containers
docker-compose ps
```

Expected output:
```
Name                    Command               State           Ports
------------------------------------------------------------------------
segmavision_backend     python app.py                    Up      0.0.0.0:8000->8000/tcp
segmavision_frontend    npm start                        Up      0.0.0.0:3000->3000/tcp
segmavision_db         docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp
```

## Step 5: Access the Application

Open your web browser and navigate to:

**Frontend**: [http://localhost:3000](http://localhost:3000)

You should see the SegmaVisionPro login page.

## Step 6: Create Your Account

1. **Click "Register"** on the login page
2. **Fill in your details**:
   - Full Name
   - Email Address
   - Password
   - Confirm Password
3. **Click "Register"** to create your account
4. **Login** with your new credentials

## Step 7: Start Using SegmaVisionPro

Once logged in, you have two main options:

### Option A: Quick Inference (Recommended for first-time users)

1. **Navigate to the Inference section**
2. **Upload an image** (supports JPG, PNG formats)
3. **Select a pre-trained model**:
   - GroundingDINO (object detection)
   - SAM (segmentation)
4. **Click "Run Inference"**
5. **View results** with detected objects and confidence scores

### Option B: Dataset Upload and Fine-tuning

1. **Navigate to the Fine-tune section**
2. **Prepare your dataset** in COCO format:
   ```
   your-dataset/
   ├── annotations/
   │   ├── instances_train.json
   │   └── instances_val.json
   ├── train/
   │   ├── image1.jpg
   │   ├── image2.jpg
   │   └── ...
   └── val/
       ├── image1.jpg
       ├── image2.jpg
       └── ...
   ```
3. **Upload your dataset** using the upload form
4. **Configure training parameters**:
   - Model architecture
   - Epochs
   - Learning rate
   - Batch size
5. **Start training** and monitor progress
6. **Use your trained model** for inference

## Essential Docker Compose Commands

### Managing Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs backend
```

### Troubleshooting Commands

```bash
# Check if ports are available
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Check container status
docker-compose ps

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Quick Start Summary

The streamlined workflow is:

1. **Clone** → `git clone https://github.com/include07/SegmaVisionPro.git`
2. **Download Models** → `cd inference/pre_trained_models && ./download_models.sh`
3. **Start** → `cd ../.. && docker-compose up -d`
4. **Register** → Visit http://localhost:3000 and create account
5. **Login** → Use your credentials to access the platform
6. **Use** → Start with inference or upload datasets for training

## Troubleshooting

### Service Won't Start

1. **Check port conflicts**:
   ```bash
   # Check if ports are already in use
   sudo netstat -tulpn | grep :3000
   sudo netstat -tulpn | grep :8000
   ```

2. **Check Docker daemon**:
   ```bash
   # Ensure Docker is running
   sudo systemctl status docker
   ```

3. **Check container logs**:
   ```bash
   # View specific service logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

### GPU Not Detected

1. **Verify NVIDIA runtime**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

2. **Check container GPU access**:
   ```bash
   docker-compose exec backend nvidia-smi
   ```

## Getting Help

If you encounter issues:

- Check the troubleshooting sections in the individual setup guides
- Review container logs: `docker-compose logs [service-name]`
- Visit our [GitHub Issues](https://github.com/include07/SegmaVisionPro/issues)
- Check the [API documentation](http://localhost:8000/docs) when running

Happy coding with SegmaVisionPro! 🚀
