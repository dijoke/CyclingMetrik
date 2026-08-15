from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coaching_velo")


def configurer_gestion_erreurs(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def gestion_erreur_inattendue(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Erreur interne inattendue"})
