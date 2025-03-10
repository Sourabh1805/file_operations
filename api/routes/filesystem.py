# app/api/routes/filesystem.py
"""
API endpoints for file system operations including drives, folders, files management,
and entity operations with full CRUD capabilities.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
import logging

from api.models.entities import EntityResponse, Container
from api.services.filesystem import FileSystemService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_filesystem_service() -> FileSystemService:
    """Dependency provider for FileSystemService instance."""
    return FileSystemService()


@router.post(
    "/drives/{drive_name}",
    summary="Create a new drive",
    response_description="Path and creation timestamp of the new drive"
)
def create_drive(
    drive_name: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """
    Creates a new top-level drive with the specified name.

    - **drive_name**: Unique name for the new drive (must be valid filesystem name)
    - **Example Input**: Drive1
    """
    try:
        drive = service.create_drive(drive_name)
        logger.info("Drive '%s' created successfully at %s", drive_name, drive.path())
        return {
            "path": drive.path(),
            "created_at": drive.created_at.isoformat()
        }
    except ValueError as e:
        logger.warning("Drive creation failed for '%s': %s", drive_name, str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/folders/{path:path}",
    summary="Create a new folder",
    response_description="Path and creation timestamp of the new folder"
)
def create_folder(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """
    Creates a new folder at the specified path.

    - **path**: Full path including parent directories and new folder name
    - **Example Input**: Drive1/folder1 , Drive1/folder2

    """
    clean_path = path.strip('/')
    if not clean_path:
        logger.error("Empty path provided for folder creation")
        raise HTTPException(status_code=400, detail="Path cannot be empty")

    parts = clean_path.split('/')
    folder_name = parts[-1]
    parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''

    if not parent_path:
        logger.warning("Attempted root-level folder creation at %s", clean_path)
        raise HTTPException(
            status_code=400,
            detail="Use /drives endpoint for root-level creation"
        )

    try:
        parent = service.resolve_path(parent_path)
        if not isinstance(parent, Container):
            logger.error("Parent %s is not a container", parent_path)
            raise ValueError("Parent must be a drive or folder")

        folder = service.create_folder(folder_name, parent)
        logger.info("Folder created at %s", folder.path())
        return {
            "path": folder.path(),
            "created_at": folder.created_at.isoformat()
        }
    except ValueError as e:
        logger.error("Folder creation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except KeyError as e:
        logger.error("Parent path not found: %s", parent_path)
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/files/{path:path}",
    summary="Create a new file",
    response_description="Path, content, and creation timestamp of the new file"
)
def create_file(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """
    Creates a new file at the specified path.

    - **path**: Full path including parent directories and new file name
    - **Example Input**: Drive1/folder1/file1.txt , Drive1/folder2/file1.jpg
    """
    clean_path = path.strip('/')
    if not clean_path:
        logger.error("Empty path provided for file creation")
        raise HTTPException(status_code=400, detail="Path cannot be empty")

    parts = clean_path.split('/')
    if len(parts) < 2:
        logger.error("Invalid file path depth: %s", clean_path)
        raise HTTPException(
            status_code=400,
            detail="File must be created within a drive or folder"
        )

    filename = parts[-1]
    parent_path = '/'.join(parts[:-1])

    try:
        parent = service.resolve_path(parent_path)
        if not isinstance(parent, Container):
            logger.error("Parent %s is not a container", parent_path)
            raise ValueError("Parent must be a drive or folder")

        file = service.create_file(filename, parent)
        logger.info("File created at %s", file.path())
        return {
            "path": file.path(),
            "created_at": file.created_at.isoformat(),
            "content": file.content
        }
    except ValueError as e:
        logger.error("File creation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except KeyError as e:
        logger.error("Parent path not found: %s", parent_path)
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/structure",
    response_model=List[EntityResponse],
    summary="Get full filesystem structure",
    response_description="Retrieves complete hierarchy of drives, folders and files"
)
def get_full_structure(
    service: FileSystemService = Depends(get_filesystem_service)
):
    """Retrieves complete filesystem structure with nested relationships."""
    logger.debug("Retrieving full filesystem structure")
    return service.get_structure()


@router.get(
    "/entity/{path:path}",
    response_model=EntityResponse,
    summary="Get entity details",
    response_description="Retrieve metadata and content for a specific entity"
)
def get_entity(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """Retrieves details for a specific entity by its full path.

        - **Example Input**: Drive1/folder1 , Drive1/, Drive1/folder1/file1.txt
    """
    clean_path = path.strip('/')
    logger.info("Fetching entity at path: %s", clean_path)
    
    try:
        entity = service.resolve_path(clean_path)
        return service.entity_to_response(entity)
    except (ValueError, KeyError) as e:
        logger.error("Entity not found at %s: %s", clean_path, str(e))
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put(
    "/entities/{old_path:path}/move/{new_path:path}",
    summary="Move/rename an entity",
    response_description="New path and move timestamp"
)
def move_entity(
    old_path: str,
    new_path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """
    Moves or renames an entity to a new location.

    - **old_path**: Current full path of the entity
    - **new_path**: Target path including new parent and name
    - **Example Input**: Drive1/folder1/file1.txt   to  Drive1/folder2/file1.txt 
    """
    logger.info("Moving entity from %s to %s", old_path, new_path)
    
    try:
        entity = service.resolve_path(old_path.strip('/'))
        clean_new_path = new_path.strip('/')
        
        if not clean_new_path:
            raise ValueError("New path cannot be empty")

        new_parts = clean_new_path.split('/')
        if len(new_parts) < 2:
            raise ValueError("New path must include parent directory")

        parent_path = '/'.join(new_parts[:-1])
        new_name = new_parts[-1]

        new_parent = service.resolve_path(parent_path)
        if not isinstance(new_parent, Container):
            logger.error("Target parent %s is not a container", parent_path)
            raise ValueError("Target must be a drive or folder")

        service.move_entity(entity, new_parent, new_name)
        logger.info("Entity moved successfully to %s", entity.path())
        
        return {
            "status": "success",
            "new_path": entity.path(),
            "moved_at": datetime.now().isoformat()
        }
        
    except (ValueError, KeyError) as e:
        logger.error("Move operation failed: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.critical("Unexpected error during move: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.delete(
    "/entities/{path:path}",
    summary="Delete an entity",
    response_description ="Permanently deletes a file, folder, or drive"
)
def delete_entity(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """Deletes an entity and all its contents (if a container).
        - **Example Input**: Drive1/folder1/file1.txt   
    """
    clean_path = path.strip('/')
    logger.warning("Attempting deletion of entity at %s", clean_path)
    
    try:
        entity = service.resolve_path(clean_path)
        service.delete_entity(entity)
        logger.info("Entity deleted successfully: %s", clean_path)
        return {"status": "success"}
    except (ValueError, KeyError) as e:
        logger.error("Deletion failed: %s", str(e))
        raise HTTPException(status_code=404, detail=str(e)) from e