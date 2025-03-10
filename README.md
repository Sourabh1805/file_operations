# In-Memory File System API 💾

A Python implementation of an object-oriented in-memory file system supporting drives, folders, files, and core operations with full test coverage.

## Overview 🔍
- **Hierarchical Storage**: Mirror real-world file system structure
- **CRUD Operations**: Create/Delete/Move/Write entities with validation
- **Type Safety**: Strict entity type enforcement
- **Path Resolution**: Absolute path-based operations
- **Dockerized** image


# Solution 
## Key Focus Areas

### Demonstrated SDLC Lifecycle Events:
       Followed a structured approach to requirements, design, implementation, and testing.
       
### SOLID Principles 
        Single Responsibility Principle (SRP)
        O - Open/Closed Principle (OCP)
        L - Liskov Substitution Principle (LSP)
        I - Interface Segregation Principle (ISP)

### PEP8 Coding standard

  
### Advance Logging
-     Multi-environment support (development/production)
-     Structured JSON logging for file/cloud storage
-     Rich console output for local development
-     Request correlation IDs for traceability
-     Log rotation and size management

### Reliable Solution:
      Prioritized system reliability even with unpredictable BigChat event behavior.

### Scalable Architecture:
      Designed a modular, scalable architecture to accommodate future enhancements.

## API Operations 🛠️
| Endpoint                          | Method | Description                  | Parameters             |
|------------------------------------|--------|------------------------------|------------------------|
| `/drives/{name}`                   | POST   | Create new drive             | `name: str`            |
| `/folders/{path}`                  | POST   | Create nested folder         | `path: str`            |
| `/files/{path}`                    | POST   | Create new file              | `path: str`            |
| `/entities/{path}`                 | DELETE | Delete entity                | `path: str`            |
| `/entities/{path}/move/{new_path}` | PUT    | Move/rename entity           | `path: str`, `new_path: str` |
| `/files/{path}/content` | PUT | Update file content | `path: str`, `content :str` |
| `/structure`                       | GET    | Full system hierarchy        | -                      |

## Data Structure Design 🌳
**Hierarchical Tree with Dictionary Storage**
```python
class Drive(Container):
    def __init__(self, name):
        self.children = {}  # Folders/Files
        self.parent = None

class Folder(Container):
    def __init__(self, name):
        self.children = {}  # Subfolders/Files
        self.parent = None

class File:
    def __init__(self, name):
        self.content = ""
        self.parent = None
```

```
            Entity
              ▲
       _______|_______
      |               |
  Container         File
    ▲
 ___|___
|       |
Drive  Folder
```

## Why This Structure?
- Fast Lookups: O(1) access via dictionary keys
- Natural Hierarchy: Parent-child relationships mirror OS
- Memory Efficiency: Only stores active nodes
- Path Resolution: path.split('/') → sequential child access
- Scalability: Handles deep nesting efficiently



# Installation ⚙️

## Method 1: Local Development
### Clone Repository
```
git clone https://github.com/yourusername/in-memory-filesystem.git
cd in-memory-filesystem
```

### Install Dependencies
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
### env setup

rename ```env.sample ``` to ```.env```

### Run Tests

Set the PYTHONPATH environment variable before running pytest:

```
pip install -r requirements-dev.txt
```

* On Windows:
```
set PYTHONPATH= rootfolder
pytest
```

* On macOS/Linux:

```
export PYTHONPATH=/rootfolder
pytest
```

###  Start Server
```
uvicorn api.main:app --reload
```

### Swagger 
```
http://127.0.0.1:8000/docs
```



## Method 2: Docker Containerization

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/in-memory-filesystem.git
cd in-memory-filesystem

# Build and start containers
docker compose up -d --build

# Follow logs
docker compose logs -f

# Stop containers
docker compose down
```
### Swagger 
```
http://localhost:8000/docs
```



# Assumptions 📋

### 1. Storage Persistence
- In-Memory Only: No persistent storage between application restarts
- Session-Based: Data exists only while the service is running

### 2. Naming Conventions
- Unique Names: No duplicate names within the same container
- Valid Characters: Names must match regex ^[a-zA-Z0-9_-]+$
- Case Sensitivity: "File.txt" ≠ "file.txt"

### 3. Hierarchy Constraints
- Single Parent: Entities cannot exist in multiple locations
- Drive Roots: All paths must start with a drive (e.g., /main/docs)

### 4. Operational Limits
- Path Length: Maximum 255 characters per path segment
- File Size: No explicit size limits (memory-constrained)

### 5. Security Model
- No Authentication: Open access to all operations
- No Encryption: Content stored in plain text
- Local Access: Designed for local network use only

### 6. Environment Setup
- Development Focus: .env.dev loaded by default
- Time Zones: All timestamps in UTC
