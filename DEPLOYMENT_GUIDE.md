# Financial RAG System - Deployment Guide

## 🚀 Complete Deployment Instructions

This guide covers multiple deployment options from local development to production cloud deployment.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Streamlit Cloud](#streamlit-cloud-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Google Cloud Platform](#gcp-deployment)
6. [Environment Variables](#environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.9+
- pip
- 2GB+ free disk space
- OpenAI API key

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/financial-rag-system.git
cd financial-rag-system
```

### Step 2: Automated Setup

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create virtual environment
- Install all dependencies
- Set up directory structure
- Create .env file
- Generate helper scripts

### Step 3: Configure API Key

Edit `.env` file:
```bash
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 4: Add Documents

Place PDF files in `data/raw/`:
```
data/raw/Apple_2024_Q3.pdf
data/raw/Microsoft_2024_Q2.pdf
```

### Step 5: Process Documents

```bash
python scripts/process_documents.py
```

### Step 6: Run Application

**Option A: Streamlit UI**
```bash
./run.sh streamlit
```
Access at: http://localhost:8501

**Option B: FastAPI**
```bash
./run.sh api
```
Access at: http://localhost:8000/docs

---

## Docker Deployment

### Single Container (Streamlit)

```bash
# Build image
docker build -t financial-rag-system .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key \
  -v $(pwd)/data:/app/data \
  financial-rag-system
```

### Multi-Container (Docker Compose)

```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Streamlit UI: http://localhost:8501
- FastAPI: http://localhost:8000

### Production Docker Build

```bash
# Build production image
docker build -t financial-rag:prod \
  --build-arg ENVIRONMENT=production .

# Run with resource limits
docker run -d \
  --name financial-rag \
  -p 8501:8501 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  --memory="2g" \
  --cpus="1.0" \
  financial-rag:prod
```

---

## Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- OpenAI API key

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Financial RAG System"
git branch -M main
git remote add origin https://github.com/yourusername/financial-rag-system.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set main file: `src/streamlit_app.py`
5. Click "Advanced settings"
6. Add secrets:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
7. Click "Deploy"

### Step 3: Configure (Optional)

Create `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

### Step 4: Access Your App

Your app will be available at:
`https://yourusername-financial-rag-system.streamlit.app`

---

## AWS Deployment

### Option 1: AWS ECS (Elastic Container Service)

#### Prerequisites
- AWS account
- AWS CLI installed
- Docker Hub account (or AWS ECR)

#### Step 1: Build and Push Image

```bash
# Build image
docker build -t financial-rag:latest .

# Tag for ECR
docker tag financial-rag:latest \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/financial-rag:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Push to ECR
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/financial-rag:latest
```

#### Step 2: Create ECS Task Definition

`task-definition.json`:
```json
{
  "family": "financial-rag",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "financial-rag",
      "image": "YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/financial-rag:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "sk-your-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/financial-rag",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 3: Deploy to ECS

```bash
# Create cluster
aws ecs create-cluster --cluster-name financial-rag-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster financial-rag-cluster \
  --service-name financial-rag-service \
  --task-definition financial-rag \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 2: AWS Lambda + API Gateway

For API-only deployment using Lambda:

```bash
# Install serverless framework
npm install -g serverless

# Create serverless.yml
serverless deploy --region us-east-1
```

---

## GCP Deployment

### Cloud Run Deployment

#### Step 1: Install gcloud CLI

```bash
# Install gcloud (if not installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### Step 2: Build and Deploy

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/financial-rag

# Deploy to Cloud Run
gcloud run deploy financial-rag \
  --image gcr.io/YOUR_PROJECT_ID/financial-rag \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-your-key \
  --memory 2Gi \
  --cpu 1
```

#### Step 3: Access Application

Cloud Run will provide a URL:
`https://financial-rag-xxx-uc.a.run.app`

### App Engine Deployment

Create `app.yaml`:
```yaml
runtime: python39
env: standard
instance_class: F2

entrypoint: streamlit run src/streamlit_app.py --server.port $PORT

env_variables:
  OPENAI_API_KEY: "sk-your-key"

automatic_scaling:
  min_instances: 0
  max_instances: 2
```

Deploy:
```bash
gcloud app deploy
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB path | `./data/chroma_db` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |

### Setting Environment Variables

**Local (.env file):**
```bash
OPENAI_API_KEY=sk-your-key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Docker:**
```bash
docker run -e OPENAI_API_KEY=sk-key -e LOG_LEVEL=DEBUG ...
```

**Kubernetes:**
```yaml
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: openai-secret
        key: api-key
```

---

## Production Checklist

### Security
- [ ] API keys stored in secrets manager (not .env)
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled

### Performance
- [ ] Caching configured
- [ ] Database indexed
- [ ] Resource limits set
- [ ] Load balancing configured
- [ ] CDN for static assets

### Monitoring
- [ ] Logging enabled
- [ ] Error tracking (e.g., Sentry)
- [ ] Performance monitoring
- [ ] Cost alerts configured
- [ ] Uptime monitoring

### Backup
- [ ] Vector database backed up
- [ ] Configuration versioned
- [ ] Disaster recovery plan
- [ ] Data retention policy

---

## Troubleshooting

### Issue: Container won't start

**Check:**
```bash
docker logs financial-rag
```

**Common causes:**
- Missing API key
- Port already in use
- Insufficient memory

### Issue: High costs

**Solutions:**
- Enable caching
- Reduce `max_tokens` in config
- Use cheaper models (gpt-3.5-turbo)
- Set daily cost limits

### Issue: Slow responses

**Solutions:**
- Reduce `top_k` in config
- Use smaller chunk sizes
- Enable CDN
- Increase container resources

### Issue: Out of memory

**Solutions:**
- Increase Docker memory limit
- Reduce batch sizes
- Clear ChromaDB cache
- Use pagination for large queries

---

## Monitoring & Logging

### Streamlit Logs
```bash
# View logs
tail -f logs/financial_rag_*.log

# Docker logs
docker-compose logs -f streamlit
```

### Cost Monitoring

Access cost dashboard in Streamlit:
- Navigate to Analytics tab
- View cost summary
- Set budget alerts

### Performance Metrics

Track in application:
- Average latency per query
- Token usage
- Cache hit rate
- Error rate

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (AWS ALB, GCP Load Balancer)
- Multiple container instances
- Shared vector database (consider managed service)

### Vertical Scaling
- Increase CPU/memory
- Faster disk I/O
- Better network bandwidth

### Database Scaling
- Consider managed vector DB (Pinecone, Weaviate)
- Implement sharding for large datasets
- Use read replicas

---

## Support & Resources

- **Documentation**: See README.md and QUICKSTART.md
- **Issues**: Open GitHub issue
- **Email**: your.email@example.com

---

**Built by Febin Varghese**
Senior Data Scientist | ML Engineer
