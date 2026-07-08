from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/records")
def list_records() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Records endpoint not implemented yet",
    )
