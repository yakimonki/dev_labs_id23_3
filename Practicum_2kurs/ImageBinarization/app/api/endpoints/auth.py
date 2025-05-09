from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import create_access_token, verify_token
from app.cruds.user import get_user_by_email, create_user
from app.schemas.user import UserCreate, User
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

@router.post("/sign-up/", response_model=User)
async def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового пользователя.

    Параметры:
    - user: Данные нового пользователя (email и пароль).
    - db: Сессия базы данных (автоматически внедряется через Depends).

    Возвращает:
    - Данные зарегистрированного пользователя (схема User).

    Ошибки:
    - 400: Если пользователь с таким email уже зарегистрирован.
    """
    # Проверяем, существует ли пользователь с таким email
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #hashed_password = get_password_hash(user.password)
    # Передаем параметры напрямую, а не словарь
    new_user = create_user(
        db=db,
        user=UserCreate(email=user.email, password=user.password)  # Мы передаем не хешированный пароль, а обычный
    )

    # Генерируем токен для нового пользователя
    access_token = create_access_token(data={"sub": new_user.email})

    # Возвращаем данные нового пользователя и токен
    return {
        "id": new_user.id,
        "email": new_user.email,
        "token": access_token,
    }

@router.post("/login/")
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Проверяет существование пользователя с указанным email.
    Проверяет правильность введенного пароля.
    Если все верно, генерирует новый токен для пользователя.
    Возвращает данные пользователя с новым токеном.
    """
    # Получаем пользователя по email
    db_user = get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Генерируем токен
    access_token = create_access_token(data={"sub": db_user.email})

    # Возвращаем данные пользователя и токен
    return {
        "id": db_user.id,
        "email": db_user.email,
        "token": access_token,
    }

@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Возвращает данные текущего авторизованного пользователя.

    Параметры:
    - current_user: Данные текущего пользователя (автоматически извлекаются через Depends).

    Возвращает:
    - Данные текущего пользователя (схема User).

    Ошибки:
    - 401: Если пользователь не авторизован.
    """
    return current_user