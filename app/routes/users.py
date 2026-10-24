from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database.connection import get_db

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



# Register User
@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    hashed_password = get_password_hash(
        user.password
    )


    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user




@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == form_data.username
    ).first()


    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )


    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )


    return {
        "access_token": token,
        "token_type": "bearer"
    }

    user = db.query(User).filter(
        User.username == username
    ).first()


    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )


    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )


    return {
        "access_token": token,
        "token_type": "bearer"
    }




# Get All Users
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db)
):

    return db.query(User).all()