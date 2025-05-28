# NGC CLI Setup Guide

This guide will help you set up NVIDIA NGC CLI for downloading pre-trained models. NGC CLI is required for accessing NVIDIA's model registry.

## Prerequisites

- Linux system (Ubuntu/Debian recommended)
- Internet connection
- NVIDIA NGC account (free registration required)

## Step 1: Create NGC Account

1. Go to [NVIDIA NGC](https://ngc.nvidia.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

## Step 2: Generate NGC API Key

```{warning}
Your API key is sensitive information. Store it securely and never share it publicly.
```

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

## Next Steps

After successful NGC CLI setup:

1. **Continue with the getting started guide** to clone the repository
2. **Use the model download guide** to download required AI models
3. **Start the application** with Docker Compose

## Additional Resources

- [NGC Documentation](https://docs.nvidia.com/ngc/)
- [NGC CLI User Guide](https://docs.nvidia.com/ngc/ngc-cli-user-guide/index.html)
- [TAO Toolkit Documentation](https://docs.nvidia.com/tao/tao-toolkit/)
