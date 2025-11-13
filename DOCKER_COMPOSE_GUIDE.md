# Docker Compose Guide

This guide explains how to use the different Docker Compose files for running services independently or together.

## Available Compose Files

### 1. `docker-compose.yml` (Main - All Services)
Runs all services together (default).

```bash
docker-compose up
# or
docker-compose -f docker-compose.yml up
```

**Services:**
- ChromaDB (port 8000)
- RAG Service (port 8001)
- Backend (port 8002)
- Frontend (port 3000)

---

### 2. `docker-compose.chromadb.yml` (ChromaDB Only)
Runs only ChromaDB service.

```bash
docker-compose -f docker-compose.chromadb.yml up
```

**Use Case:** When you only need the database running.

**Services:**
- ChromaDB (port 8000)

---

### 3. `docker-compose.rag-service.yml` (RAG Service + ChromaDB)
Runs RAG service with ChromaDB dependency.

```bash
docker-compose -f docker-compose.rag-service.yml up
```

**Use Case:** When you only need the RAG service for document ingestion/querying.

**Services:**
- ChromaDB (port 8000)
- RAG Service (port 8001)

---

### 4. `docker-compose.backend.yml` (Backend Only)
Runs only the backend service.

```bash
# First, create the network (if not exists)
docker network create voice-assistant-network

# Then run backend
docker-compose -f docker-compose.backend.yml up
```

**Note:** Requires `rag-service` to be running separately and accessible.

**Services:**
- Backend (port 8002)

---

### 5. `docker-compose.frontend.yml` (Frontend Only)
Runs only the frontend service.

```bash
# First, create the network (if not exists)
docker network create voice-assistant-network

# Then run frontend
docker-compose -f docker-compose.frontend.yml up
```

**Note:** Requires `backend` to be running separately and accessible.

**Services:**
- Frontend (port 3000)

---

### 6. `docker-compose.full.yml` (All Services - Explicit)
Same as main compose file, but explicitly named.

```bash
docker-compose -f docker-compose.full.yml up
```

**Use Case:** When you want to be explicit about running the full stack.

**Services:**
- ChromaDB (port 8000)
- RAG Service (port 8001)
- Backend (port 8002)
- Frontend (port 3000)

---

### 7. `docker-compose.dev.yml` (Development Mode)
Runs all services with hot-reload enabled.

```bash
docker-compose -f docker-compose.dev.yml up
```

**Features:**
- Hot-reload for backend (uvicorn --reload)
- Hot-reload for RAG service (uvicorn --reload)
- Hot-reload for frontend (npm run dev)

**Use Case:** Development with automatic code reloading.

**Services:**
- ChromaDB (port 8000)
- RAG Service (port 8001) - with reload
- Backend (port 8002) - with reload
- Frontend (port 3000) - with reload

---

## Common Usage Patterns

### Pattern 1: Run Everything Together
```bash
docker-compose up
```

### Pattern 2: Run Services Individually
```bash
# Terminal 1: Start ChromaDB
docker-compose -f docker-compose.chromadb.yml up

# Terminal 2: Start RAG Service
docker-compose -f docker-compose.rag-service.yml up

# Terminal 3: Start Backend
docker-compose -f docker-compose.backend.yml up

# Terminal 4: Start Frontend
docker-compose -f docker-compose.frontend.yml up
```

### Pattern 3: Development with Hot-Reload
```bash
docker-compose -f docker-compose.dev.yml up
```

### Pattern 4: Run Only Infrastructure
```bash
# Start ChromaDB
docker-compose -f docker-compose.chromadb.yml up -d

# Start RAG Service (includes ChromaDB)
docker-compose -f docker-compose.rag-service.yml up -d
```

### Pattern 5: Run Only Application Services
```bash
# Ensure network exists
docker network create voice-assistant-network 2>/dev/null || true

# Start Backend (requires RAG service running)
docker-compose -f docker-compose.backend.yml up

# Start Frontend (requires Backend running)
docker-compose -f docker-compose.frontend.yml up
```

---

## Network Configuration

All services use the `voice-assistant-network` bridge network.

### Creating Network Manually
```bash
docker network create voice-assistant-network
```

### Checking Network
```bash
docker network ls
docker network inspect voice-assistant-network
```

---

## Volume Management

### ChromaDB Data Volume
The `chroma_data` volume persists ChromaDB data.

**List volumes:**
```bash
docker volume ls
```

**Inspect volume:**
```bash
docker volume inspect voice-assistant_chroma_data
```

**Remove volume (WARNING: Deletes data):**
```bash
docker volume rm voice-assistant_chroma_data
```

---

## Stopping Services

### Stop All Services (Main Compose)
```bash
docker-compose down
```

### Stop Specific Compose File
```bash
docker-compose -f docker-compose.chromadb.yml down
docker-compose -f docker-compose.rag-service.yml down
docker-compose -f docker-compose.backend.yml down
docker-compose -f docker-compose.frontend.yml down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

---

## Building Services

### Build All Services
```bash
docker-compose build
```

### Build Specific Service
```bash
docker-compose build backend
docker-compose build rag-service
docker-compose build frontend
```

### Build with No Cache
```bash
docker-compose build --no-cache
```

---

## Logs

### View All Logs
```bash
docker-compose logs
```

### View Specific Service Logs
```bash
docker-compose logs backend
docker-compose logs rag-service
docker-compose logs frontend
docker-compose logs chromadb
```

### Follow Logs
```bash
docker-compose logs -f
docker-compose logs -f backend
```

---

## Troubleshooting

### Port Conflicts

If you get port conflicts, check what's using the port:

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Network Issues

If services can't communicate:

1. Ensure all services are on the same network:
   ```bash
   docker network inspect voice-assistant-network
   ```

2. Check service names match:
   - Backend connects to `rag-service:8000`
   - RAG service connects to `chromadb:8000`

### Volume Issues

If ChromaDB data is lost:

1. Check volume exists:
   ```bash
   docker volume ls | grep chroma
   ```

2. Ensure volume is mounted:
   ```bash
   docker-compose -f docker-compose.chromadb.yml config
   ```

---

## Best Practices

1. **Development:** Use `docker-compose.dev.yml` for hot-reload
2. **Testing:** Use individual compose files to test services independently
3. **Production:** Use `docker-compose.yml` or `docker-compose.full.yml`
4. **Debugging:** Use individual compose files to isolate issues
5. **CI/CD:** Use specific compose files for targeted testing

---

## Quick Reference

| Compose File | Services | Use Case |
|-------------|----------|----------|
| `docker-compose.yml` | All | Default, production |
| `docker-compose.chromadb.yml` | ChromaDB | Database only |
| `docker-compose.rag-service.yml` | RAG + ChromaDB | RAG testing |
| `docker-compose.backend.yml` | Backend | Backend testing |
| `docker-compose.frontend.yml` | Frontend | Frontend testing |
| `docker-compose.full.yml` | All | Explicit full stack |
| `docker-compose.dev.yml` | All + reload | Development |

