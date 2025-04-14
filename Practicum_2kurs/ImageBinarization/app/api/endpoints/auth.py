from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import create_access_token, verify_token
from app.cruds.user import get_user_by_email, create_user
from app.schemas.user import UserCreate, UserMeResponse, UserLogin, User
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash
from app.core.dependencies import get_current_user

router = APIRouter()

# Настройка OAuth2 схемы для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Функция для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = verify_token(token, credentials_exception)
        user = get_user_by_email(db, email=email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@router.post("/sign-up/", response_model=UserMeResponse)
async def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    
    Параметры:
    - email: валидный email
    - password: пароль (минимум 8 символов)
    
    Возвращает:
    - id: ID пользователя
    - email: email пользователя
    - is_active: статус аккаунта
    - token: JWT токен (опционально)
    """
    # Проверка существующего пользователя
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Создание пользователя
        db_user = create_user(db=db, user=user)
        
        # Генерация токена
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {
            "id": db_user.id,
            "email": db_user.email,
            "is_active": db_user.is_active,
            "token": access_token
        }
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    
@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):  # Используем UserLogin вместо UserCreate
    db_user = get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "token": create_access_token(data={"sub": db_user.email})
    }

@router.get("/users/me/", response_model=UserMeResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    Получение информации о текущем авторизованном пользователе
    
    Требует:
    - Валидный JWT токен в заголовке Authorization
    
    Возвращает:
    - id: идентификатор пользователя
    - email: email пользователя
    - is_active: статус активации
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }