from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario_admin import UsuarioAdmin
from app.schemas.auth import LoginRequest, Token
from app.utils.security import verify_password, create_access_token
from datetime import timedelta
from app.config import settings


def authenticate_user(db: Session, login_data: LoginRequest) -> Token:
    user = db.query(UsuarioAdmin).filter(UsuarioAdmin.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "rol": user.rol},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
