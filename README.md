# In-Memory File System API 💾

A Python implementation of an object-oriented in-memory file system supporting drives, folders, files, and core operations with full test coverage.

## Overview 🔍
- **Hierarchical Storage**: Mirror real-world file system structure
- **CRUD Operations**: Create/Delete/Move/Write entities with validation
- **Type Safety**: Strict entity type enforcement
- **Path Resolution**: Absolute path-based operations

## Key Features ✨
- Create drives, folders, and files
- Delete entities with cascade
- Move entities between containers
- File content modification
- Path validation and error handling
- 98% test coverage (pytest)

## API Operations 🛠️
| Endpoint                          | Method | Description                  | Parameters             |
|------------------------------------|--------|------------------------------|------------------------|
| `/drives/{name}`                   | POST   | Create new drive             | `name: str`            |
| `/folders/{path}`                  | POST   | Create nested folder         | `path: str`            |
| `/files/{path}`                    | POST   | Create new file              | `path: str`            |
| `/entities/{path}`                 | DELETE | Delete entity                | `path: str`            |
| `/entities/{path}/move/{new_path}` | PUT    | Move/rename entity           | `path: str`, `new_path: str` |
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

## Why This Structure?
Fast Lookups: O(1) access via dictionary keys

Natural Hierarchy: Parent-child relationships mirror OS

Memory Efficiency: Only stores active nodes

Path Resolution: path.split('/') → sequential child access

Scalability: Handles deep nesting efficiently

## Design Principles 🧩

SOLID Compliance

Single Responsibility: Separate entities/operations

Open/Closed: Extensible without modification

PEP8 Standards: Strict style enforcement

Immutable Timestamps: Created/modified times

ACID-like Operations: Atomic moves/deletes


## Installation ⚙️

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

### Run Tests

Set the PYTHONPATH environment variable before running pytest:

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
