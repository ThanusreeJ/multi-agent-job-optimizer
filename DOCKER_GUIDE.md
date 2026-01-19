# 🐳 Podman/Docker Deployment Guide

## Prerequisites

- **Podman** installed on your system
- **`.env` file** configured with your API keys

---

## 🚀 Quick Start with Podman

### **1. Build the Image**

```bash
# Navigate to project directory
cd D:\Downloads\new_n8n-job-optimizer-main\n8n-job-optimizer-main\job-optimizer

# Build the image with Podman
podman build -t job-optimizer:latest .
```

### **2. Run the Container**

#### **Option A: Using Podman Directly**

```bash
# Run with environment variables from .env file
podman run -d \
  --name job-optimizer \
  -p 8501:8501 \
  --env-file .env \
  -v ./sample_jobs.csv:/app/sample_jobs.csv:Z \
  job-optimizer:latest
```

#### **Option B: Using Podman Compose (Recommended)**

```bash
# Install podman-compose if not already installed
pip install podman-compose

# Start the application
podman-compose up -d

# View logs
podman-compose logs -f

# Stop the application
podman-compose down
```

### **3. Access the Application**

Open your browser at: **http://localhost:8501**

---

## 🔧 Podman Commands

### **View Running Containers**
```bash
podman ps
```

### **View Logs**
```bash
podman logs -f job-optimizer
```

### **Stop Container**
```bash
podman stop job-optimizer
```

### **Start Container**
```bash
podman start job-optimizer
```

### **Remove Container**
```bash
podman rm -f job-optimizer
```

### **Remove Image**
```bash
podman rmi job-optimizer:latest
```

### **Shell into Container (Debugging)**
```bash
podman exec -it job-optimizer /bin/bash
```

---

## 🔍 Troubleshooting

### **Issue: "Permission denied" errors**

Add `:Z` flag to volume mounts (SELinux relabeling):
```bash
podman run -d \
  --name job-optimizer \
  -p 8501:8501 \
  --env-file .env \
  -v ./sample_jobs.csv:/app/sample_jobs.csv:Z \
  job-optimizer:latest
```

### **Issue: Container won't start**

Check logs:
```bash
podman logs job-optimizer
```

Common fixes:
- Verify `.env` file exists and has valid API keys
- Check port 8501 is not already in use: `netstat -an | findstr 8501`
- Rebuild image: `podman build --no-cache -t job-optimizer:latest .`

### **Issue: Can't access application**

Verify container is running:
```bash
podman ps
```

Test health:
```bash
podman exec job-optimizer curl http://localhost:8501/_stcore/health
```

---

## 📦 Production Deployment

### **Build Production Image (No Dev Volumes)**

Edit `docker-compose.yml` and comment out volume mounts:
```yaml
volumes:
  # Mount local code for development (optional - comment out for production)
  # - ./ui:/app/ui
  # - ./agents:/app/agents
  # - ./models:/app/models
  # - ./utils:/app/utils
  - ./sample_jobs.csv:/app/sample_jobs.csv
```

Then run:
```bash
podman-compose up -d
```

### **Push to Registry (Optional)**

```bash
# Tag for registry
podman tag job-optimizer:latest your-registry.com/job-optimizer:latest

# Push to registry
podman push your-registry.com/job-optimizer:latest
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use secrets management** in production (Vault, AWS Secrets Manager)
3. **Run as non-root user** - Already configured in Dockerfile
4. **Scan for vulnerabilities**:
   ```bash
   podman scan job-optimizer:latest
   ```

---

## 🆚 Podman vs Docker

Podman commands are identical to Docker:
- `podman` = `docker`
- `podman-compose` = `docker-compose`

If you have Docker installed elsewhere, the same Dockerfile and docker-compose.yml work with both!

---

## 📊 Resource Limits (Optional)

Limit CPU and memory:
```bash
podman run -d \
  --name job-optimizer \
  -p 8501:8501 \
  --env-file .env \
  --cpus="2" \
  --memory="2g" \
  job-optimizer:latest
```

Or in `docker-compose.yml`:
```yaml
services:
  job-optimizer:
    # ... other settings ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## ✅ Verification Checklist

After deployment, verify:
- [ ] Container is running: `podman ps`
- [ ] Logs show no errors: `podman logs job-optimizer`
- [ ] Health check passes: `podman inspect job-optimizer --format='{{.State.Health.Status}}'`
- [ ] Web UI accessible at http://localhost:8501
- [ ] Can upload `sample_jobs.csv` and run optimization
- [ ] AI agents execute successfully (check logs for LLM calls)

---

## 🎓 Next Steps

- **Kubernetes Deployment**: Convert to K8s manifests with `podman generate kube`
- **CI/CD Integration**: Automate builds with GitHub Actions
- **Multi-Architecture**: Build for ARM/AMD64 with `podman buildx`
