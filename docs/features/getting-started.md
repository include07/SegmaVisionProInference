# Getting Started with SegmaVisionPro

This guide will walk you through cloning the SegmaVisionPro repository and getting the platform running using Docker Compose.

## Prerequisites

Before you begin, ensure you have completed the setup requirements:

- ✅ [Docker installed and running](../setup/docker-setup.md)
- ✅ [NVIDIA Container Toolkit configured](../setup/nvidia-toolkit.md) (for GPU support)
- ✅ [NGC CLI configured](../setup/ngc-setup.md) (for model downloads)
- ✅ [Pre-deployment checklist completed](../setup/pre-deployment-checklist.md)

## Step 1: Clone the Repository

First, clone the SegmaVisionPro repository to your local machine:

```bash
# Clone the repository
git clone https://github.com/your-org/SegmaVisionPro.git

# Navigate to the project directory
cd SegmaVisionPro
```

### Alternative: Download as ZIP

If you prefer not to use Git, you can download the repository as a ZIP file:

1. Visit the [SegmaVisionPro GitHub repository](https://github.com/your-org/SegmaVisionPro)
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your desired location

## Step 2: Project Structure Overview

After cloning, you'll see the following structure:

```
SegmaVisionPro/
├── docker-compose.yml          # Main orchestration file
├── backend/                    # Python FastAPI backend
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── package.json
│   ├── Dockerfile.dev
│   └── src/
├── inference/                  # Model inference components
│   ├── pre_trained_models/
│   └── specs/
└── docs/                      # Documentation (this site)
```

## Step 3: Environment Configuration

Create environment configuration files for your deployment:

### Backend Environment

Create a `.env` file in the project root:

```bash
# Create environment file
touch .env
```

Add the following configuration to `.env`:

```bash
# Database Configuration
POSTGRES_DB=segmavision
POSTGRES_USER=segmavision_user
POSTGRES_PASSWORD=your_secure_password_here

# Backend Configuration
BACKEND_SECRET_KEY=your_secret_key_here
BACKEND_DEBUG=false
BACKEND_CORS_ORIGINS=http://localhost:3000

# GPU Configuration
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Storage Paths
UPLOAD_PATH=/app/uploads
MODEL_PATH=/app/models
```

### Frontend Environment

Create a `.env` file in the `frontend/` directory:

```bash
# Navigate to frontend directory
cd frontend

# Create frontend environment file
touch .env
```

Add the following to `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Step 4: Download Pre-trained Models

Before starting the services, download the required pre-trained models:

```bash
# Navigate to the inference directory
cd inference/pre_trained_models

# Make the download script executable
chmod +x download_models.sh

# Download models (this may take several minutes)
./download_models.sh
```

Expected output:
```
Downloading GroundingDINO model...
✅ GroundingDINO model downloaded successfully
Downloading SAM model...
✅ SAM model downloaded successfully
All models downloaded successfully!
```

## Step 5: Start with Docker Compose

Now you're ready to start the SegmaVisionPro platform:

### Quick Start (Recommended)

```bash
# Return to project root
cd /path/to/SegmaVisionPro

# Start all services in detached mode
docker-compose up -d
```

### Development Mode

For development with live reloading:

```bash
# Start in development mode with logs visible
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production Mode

For production deployment:

```bash
# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Step 6: Verify Installation

After starting the services, verify everything is running correctly:

### Check Service Status

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

### Check Service Health

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

### Access the Application

Open your web browser and navigate to:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Step 7: First Login

1. Open [http://localhost:3000](http://localhost:3000) in your browser
2. Click "Register" to create a new account
3. Fill in your details and register
4. Login with your new credentials

## Common Docker Compose Commands

Here are essential Docker Compose commands for managing your SegmaVisionPro deployment:

### Starting Services

```bash
# Start all services
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start specific service
docker-compose up backend

# Start with rebuilt images
docker-compose up --build
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ This will delete your data!)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Monitoring Services

```bash
# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines of logs
docker-compose logs --tail=100
```

### Service Management

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Execute command in running container
docker-compose exec backend bash

# Scale a service (for load balancing)
docker-compose up --scale backend=3
```

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

### Permission Issues

```bash
# Fix permission issues with uploaded files
sudo chown -R $USER:$USER ./backend/uploads/
sudo chmod -R 755 ./backend/uploads/
```

### Database Connection Issues

```bash
# Reset database
docker-compose down
docker volume rm segmavisionpro_postgres_data
docker-compose up -d db
# Wait for database to initialize, then start other services
docker-compose up backend frontend
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

## Performance Optimization

### Resource Allocation

Edit `docker-compose.yml` to adjust resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'
```

### Storage Optimization

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Next Steps

Now that SegmaVisionPro is running, you can:

1. **Upload your first dataset** - Learn how to prepare and upload training data
2. **Train your first model** - Start training custom computer vision models
3. **Run inference** - Use pre-trained or custom models for predictions
4. **Explore the API** - Integrate SegmaVisionPro with your applications

## Getting Help

If you encounter issues:

- Check the [Troubleshooting sections](../setup/pre-deployment-checklist.md#troubleshooting) in setup guides
- Review container logs: `docker-compose logs [service-name]`
- Visit our [GitHub Issues](https://github.com/your-org/SegmaVisionPro/issues)
- Check the [API documentation](http://localhost:8000/docs) when running

## Security Considerations

For production deployments:

1. **Change default passwords** in `.env` file
2. **Use HTTPS** with proper SSL certificates
3. **Configure firewall** to restrict access to necessary ports
4. **Regular backups** of your data volumes
5. **Keep Docker images updated** with security patches

Happy coding with SegmaVisionPro! 🚀
