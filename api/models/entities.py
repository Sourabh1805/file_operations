# app/models/entities.py
"""
Data models representing file system entities (drives, folders, files) and their
API response structure.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class Entity(ABC):
    """Abstract base class for all file system entities."""
    
    def __init__(self, name: str):
        """
        Initialize a new file system entity.

        Args:
            name: Unique name for the entity (must be valid filesystem name)
        
        Raises:
            ValueError: If name contains invalid characters
        """
        if '/' in name:
            logger.error("Attempt to create entity with invalid name: %s", name)
            raise ValueError("Entity name cannot contain '/'")
        if not name:
            logger.error("Attempt to create entity with empty name")
            raise ValueError("Entity name cannot be empty")

        self.name = name
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.parent: Optional['Container'] = None

    def path(self) -> str:
        """Get full hierarchical path of the entity."""
        parts = []
        current = self
        while current:
            parts.append(current.name)
            current = current.parent
        return '/' + '/'.join(reversed(parts))

    @abstractmethod
    def is_container(self) -> bool:
        """Check if the entity can contain other entities."""
        pass


class Container(Entity):
    """Base class for entities that can contain other entities (drives/folders)."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.children: Dict[str, Union['Container', 'File']] = {}

    def is_container(self) -> bool:
        return True

    def add_child(self, child: Entity) -> None:
        """
        Add a child entity to this container.

        Args:
            child: Entity to add

        Raises:
            ValueError: If child name already exists
            TypeError: If child is not an Entity instance
        """
        if not isinstance(child, Entity):
            logger.error("Attempt to add non-entity to %s: %s", 
                        self.path(), type(child))
            raise TypeError("Only Entity instances can be added as children")

        if child.name in self.children:
            logger.warning("Duplicate name in %s: %s", self.path(), child.name)
            raise ValueError(f"Name '{child.name}' already exists in this location")

        child.parent = self
        self.children[child.name] = child
        self.modified_at = datetime.now()
        logger.info("Added %s to %s", child.name, self.path())


class Drive(Container):
    """Top-level container representing a drive/volume."""
    
    def path(self) -> str:
        """Get drive path with trailing slash for container indication."""
        return f"/{self.name}/"


class Folder(Container):
    """Container representing a directory/folder."""
    pass


class File(Entity):
    """Entity representing a file with content storage."""
    
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self._content = content

    def is_container(self) -> bool:
        return False

    @property
    def content(self) -> str:
        """Get current file content."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Update file content and modification timestamp."""
        self._content = value
        self.modified_at = datetime.now()
        logger.info("Updated content in %s", self.path())


class EntityResponse(BaseModel):
    """
    API response model representing any file system entity with hierarchy support.
    
    Fields:
        type: Entity type classification
        name: Display name of the entity
        path: Full hierarchical path
        created_at: ISO-8601 creation timestamp
        modified_at: ISO-8601 last modification timestamp
        content: File content (only for file entities)
        children: Contained entities (only for containers)
    """
    type: Literal["drive", "folder", "file"]
    name: str
    path: str
    created_at: str
    modified_at: str
    content: Optional[str] = None
    children: Optional[List['EntityResponse']] = None

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "type": "folder",
                "name": "documents",
                "path": "/main/documents/",
                "created_at": "2023-07-15T10:30:45.000Z",
                "modified_at": "2023-07-15T10:35:12.000Z",
                "children": [
                    {
                        "type": "file",
                        "name": "report.txt",
                        "path": "/main/documents/report.txt",
                        "created_at": "2023-07-15T10:31:00.000Z",
                        "modified_at": "2023-07-15T10:31:00.000Z",
                        "content": "Annual report data"
                    }
                ]
            }
        }

    @field_validator('children')
    @classmethod
    def validate_children(cls, value, values):
        """Ensure children only exist for container types."""
        if values.data['type'] in ('drive', 'folder') and value is None:
            logger.warning("Container entity missing children field")
            return []
        if values.data['type'] == 'file' and value is not None:
            logger.error("File entity with children detected")
            raise ValueError("Files cannot contain children")
        return value