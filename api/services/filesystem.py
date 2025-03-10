# app/services/filesystem.py
"""
Core service handling file system operations and entity management with
singleton pattern ensuring consistent state across the application.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from api.models.entities import Drive, Folder, File, Container, Entity, EntityResponse

logger = logging.getLogger(__name__)


class FileSystemService:
    """
    Singleton service managing file system entities and operations including:
    - Drive/folder/file creation
    - Entity movement/deletion
    - Path resolution
    - Structure serialization
    """
    
    _instance: Optional['FileSystemService'] = None

    def __new__(cls):
        """Ensure singleton instance with lazy initialization."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
            logger.info("Initializing new FileSystemService instance")
        return cls._instance

    def __init__(self):
        """Initialize service state with empty drive registry."""
        if not self.__initialized:
            self.drives: Dict[str, Drive] = {}
            self.__initialized = True
            logger.debug("Service initialization completed")

    def create_drive(self, name: str) -> Drive:
        """
        Create a new top-level drive.

        Args:
            name: Unique name for the new drive

        Returns:
            Created Drive instance

        Raises:
            ValueError: If drive name already exists
        """
        if name in self.drives:
            logger.error("Drive creation failed - duplicate name: %s", name)
            raise ValueError(f"Drive '{name}' already exists")

        try:
            drive = Drive(name)
            self.drives[name] = drive
            logger.info("Created new drive: %s", drive.path())
            return drive
        except ValueError as e:
            logger.error("Drive creation error: %s", str(e))
            raise

    def create_folder(self, name: str, parent: Container) -> Folder:
        """
        Create a new folder within a container.

        Args:
            name: Name for the new folder
            parent: Parent container (Drive or Folder)

        Returns:
            Created Folder instance

        Raises:
            ValueError: For invalid parent or name conflicts
        """
        if not isinstance(parent, Container):
            logger.error("Invalid parent type for folder: %s", type(parent))
            raise ValueError("Parent must be a Drive or Folder")

        try:
            folder = Folder(name)
            parent.add_child(folder)
            logger.info("Created folder at %s", folder.path())
            return folder
        except ValueError as e:
            logger.error("Folder creation failed: %s", str(e))
            raise

    def create_file(self, name: str, parent: Container) -> File:
        """
        Create a new file within a container.

        Args:
            name: Name for the new file
            parent: Parent container (Drive or Folder)

        Returns:
            Created File instance

        Raises:
            ValueError: For invalid parent or name conflicts
        """
        if not isinstance(parent, Container):
            logger.error("Invalid parent type for file: %s", type(parent))
            raise ValueError("Parent must be a Drive or Folder")

        try:
            file = File(name)
            parent.add_child(file)
            logger.info("Created file at %s", file.path())
            return file
        except ValueError as e:
            logger.error("File creation failed: %s", str(e))
            raise

    def delete_entity(self, entity: Entity) -> None:
        """
        Permanently delete an entity from the file system.

        Args:
            entity: Entity to delete

        Raises:
            ValueError: For root entities or invalid operations
        """
        try:
            if isinstance(entity, Drive):
                del self.drives[entity.name]
                logger.warning("Deleted drive: %s", entity.name)
            elif entity.parent:
                # Update parent's modification time before deletion
                entity.parent.modified_at = datetime.now()
                del entity.parent.children[entity.name]
                logger.info("Deleted entity: %s", entity.path())
            else:
                raise ValueError("Cannot delete root entity without parent")
        except KeyError as e:
            logger.error("Deletion failed for %s: %s", entity.path(), str(e))
            raise ValueError(f"Entity not found: {entity.path()}") from e

    def move_entity(
        self,
        entity: Entity,
        new_parent: Container,
        new_name: str
    ) -> None:
        """
        Move/rename an entity within the file system hierarchy.

        Args:
            entity: Entity to move
            new_parent: Target container
            new_name: New name for the entity

        Raises:
            ValueError: For invalid moves or name conflicts
        """
        logger.info(
            "Moving entity %s to %s as %s",
            entity.path(),
            new_parent.path(),
            new_name
        )

        if isinstance(entity, Drive):
            raise ValueError("Cannot move drives")
        if not entity.parent:
            raise ValueError("Root entities cannot be moved")
        if new_name in new_parent.children:
            raise ValueError(f"Name '{new_name}' already exists in target")

        # Validate not moving into own subtree
        current_parent: Optional[Container] = new_parent
        while current_parent:
            if current_parent == entity:
                raise ValueError("Cannot move into own subtree")
            current_parent = current_parent.parent

        try:
            # Update original parent's modification time
            original_parent = entity.parent
            original_parent.modified_at = datetime.now()
            
            # Remove from original location
            del original_parent.children[entity.name]
            
            # Update entity name and parent
            entity.name = new_name
            new_parent.add_child(entity)
            
            logger.info(
                "Successfully moved to %s",
                entity.path()
            )
        except Exception as e:
            logger.critical(
                "Move operation failed: %s. Entity state might be inconsistent!",
                str(e)
            )
            raise

    def get_structure(self) -> List[EntityResponse]:
        """Serialize complete file system structure for API response."""
        logger.debug("Generating full structure response")
        return [self.entity_to_response(drive) for drive in self.drives.values()]

    def entity_to_response(self, entity: Entity) -> EntityResponse:
        """
        Recursively convert entity hierarchy to API response model.

        Args:
            entity: Root entity to convert

        Returns:
            EntityResponse with nested children
        """
        logger.debug("Converting entity to response: %s", entity.path())
        
        response = EntityResponse(
            type=self._get_entity_type(entity),
            name=entity.name,
            path=entity.path(),
            created_at=entity.created_at.isoformat(),
            modified_at=entity.modified_at.isoformat(),
        )

        if isinstance(entity, Container):
            response.children = [
                self.entity_to_response(child)
                for child in entity.children.values()
            ]
        elif isinstance(entity, File):
            response.content = entity.content

        return response

    def resolve_path(self, path: str) -> Entity:
        """
        Resolve full path to filesystem entity.

        Args:
            path: Absolute path to resolve

        Returns:
            Found entity

        Raises:
            ValueError: For invalid paths or missing components
        """
        clean_path = path.strip("/")
        if not clean_path:
            raise ValueError("Cannot resolve root path")

        parts = clean_path.split("/")
        logger.debug("Resolving path segments: %s", parts)

        try:
            # Start from drive
            drive_name = parts[0]
            if drive_name not in self.drives:
                raise ValueError(f"Drive '{drive_name}' not found")

            current: Entity = self.drives[drive_name]

            # Traverse path segments
            for segment in parts[1:]:
                if not isinstance(current, Container):
                    raise ValueError(f"{current.path()} is not a container")

                if segment not in current.children:
                    raise ValueError(f"Path segment '{segment}' not found")

                current = current.children[segment]

            return current
        except (KeyError, ValueError) as e:
            logger.error("Path resolution failed for '%s': %s", path, str(e))
            raise

    def _get_entity_type(self, entity: Entity) -> str:
        """Classify entity type for response model."""
        if isinstance(entity, Drive):
            return "drive"
        if isinstance(entity, Folder):
            return "folder"
        return "file"
    
    # app/services/filesystem.py (add to FileSystemService)
    def update_file_content(self, file: File, content: str) -> File:
        """Update file content with validation"""
        if not isinstance(file, File):
            raise TypeError("Can only update content of File entities")
        file.content = content
        logger.info("Updated content in %s", file.path())
        return file