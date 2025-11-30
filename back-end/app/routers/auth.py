from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para login de usuarios administradores.
    Retorna un token JWT para autenticación.
    """
    return authenticate_user(db, login_data)
