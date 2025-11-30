from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_admin import UsuarioAdmin
from app.utils.security import decode_access_token
from app.schemas.auth import TokenData

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UsuarioAdmin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(UsuarioAdmin).filter(UsuarioAdmin.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def get_current_active_superadmin(
    current_user: UsuarioAdmin = Depends(get_current_user)
) -> UsuarioAdmin:
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos suficientes"
        )
    return current_user
