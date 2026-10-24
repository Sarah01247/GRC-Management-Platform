from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)



def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    payload = decode_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return payload



def require_role(allowed_roles):

    def role_checker(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"].lower() not in [
    role.lower()
    for role in allowed_roles
]:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user


    return role_checker