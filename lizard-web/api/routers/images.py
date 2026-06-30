import os
from urllib.parse import unquote
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..config import RESULTS_DIR

router = APIRouter(prefix="/images", tags=["images"])

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg"}


@router.get("/{encoded_path:path}")
def serve_image(encoded_path: str):
    relative_path = unquote(encoded_path)

    ext = os.path.splitext(relative_path)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Path inválido")

    results_dir_real = os.path.realpath(RESULTS_DIR)
    full_path = os.path.realpath(os.path.join(RESULTS_DIR, relative_path))

    if not full_path.startswith(results_dir_real + os.sep):
        raise HTTPException(status_code=400, detail="Path inválido")

    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Imagem não disponível")

    return FileResponse(full_path, media_type="image/jpeg")
