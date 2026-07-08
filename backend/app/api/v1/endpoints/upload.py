from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/upload")
def upload_file() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Upload endpoint not implemented yet",
    )
