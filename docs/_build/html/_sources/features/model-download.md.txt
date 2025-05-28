# Model Download Guide

After cloning the SegmaVisionPro repository, you need to download the required pre-trained models before starting the Docker containers. This guide will walk you through downloading the AI models using NGC CLI.

## Prerequisites

- ✅ [SegmaVisionPro repository cloned](getting-started.md#step-1-clone-the-repository)
- ✅ [NGC CLI configured](../setup/ngc-setup.md)

## Step 1: Navigate to Models Directory

```bash
# Navigate to the pre-trained models directory
cd inference/pre_trained_models/
```

## Step 2: Download Required Models

The project uses a convenient script to download both required models:

```bash
# Make the download script executable
chmod +x download_models.sh

# Run the download script
./download_models.sh
```

## What Gets Downloaded

The script will download two essential models:

1. **Mask Grounding DINO**: `mask_grounding_dino_swin_tiny_commercial_trainable_v1.0`
2. **Grounding DINO**: `grounding_dino_swin_tiny_commercial_trainable_v1.0`

Both models will be saved as `.pth` files in the `inference/pre_trained_models/` directory.

## Expected Output

When successful, you should see:

```
Downloading Mask Grounding DINO model...
✓ Mask Grounding DINO model saved to: /path/to/mask_grounding_dino_swin_tiny_commercial_trainable.pth
Downloading Grounding DINO model...
✓ Grounding DINO model saved to: /path/to/grounding_dino_swin_tiny_commercial_trainable.pth
All downloads complete!
```

## File Structure After Download

After successful download, your directory structure will look like:

```
SegmaVisionPro/
└── inference/
    └── pre_trained_models/
        ├── download_models.sh
        ├── grounding_dino_swin_tiny_commercial_trainable.pth
        └── mask_grounding_dino_swin_tiny_commercial_trainable.pth
```

## Troubleshooting

### NGC Authentication Issues

If you get authentication errors:
```bash
# Check if you're logged in
ngc config current

# If not configured, run setup again
ngc config set
```

### Download Failures

Common issues and solutions:

- **Network Issues**: Ensure stable internet connection
- **Disk Space**: Models are large (~500MB each), ensure sufficient disk space
- **Account Access**: Verify your NGC account has access to TAO models
- **API Key**: Double-check your API key is correct

### Permission Issues

If you get permission errors:
```bash
# Ensure script is executable
chmod +x download_models.sh

# Check directory permissions
ls -la
```

## Next Steps

Once the models are downloaded successfully:

1. Return to the main project directory: `cd ../..`
2. Continue with [Docker Compose setup](getting-started.md#step-2-start-with-docker-compose)

## Need Help?

- Check the [NGC Setup Guide](../setup/ngc-setup.md) for NGC CLI configuration
- Visit our [GitHub Issues](https://github.com/include07/SegmaVisionPro/issues) for support
