from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

from tortoise.exceptions import IntegrityError

from app.models.user import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Supabase JWT settings
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-supabase-jwt-secret")  # Change in production
ALGORITHM = "HS256"

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    email = "bigharborr@gmail.com"  # <-- Replace with your test user email
    #email = "muhammedanas5186@gmail.com"

    user = await User.filter(email=email).first()

    # Fetch corresponding user from local DB
    if user is None:
        # Create a local profile from Supabase user data
        user = await User.create(
            email=email,
            username="anas",
            first_name="anas",
            last_name="khan",
            is_verified=True,  # Since they authenticated through Supabase
            password_hash="supabase_auth"  # Placeholder since auth is handled by Supabase
        )

    return user

async def get_current_user_authenticated(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print("Auth header:", credentials.credentials)

    if not credentials or not credentials.credentials:
        raise credentials_exception

    print("secret-len:", len(SUPABASE_JWT_SECRET), " first12:", SUPABASE_JWT_SECRET[:12])

    try:
        payload = jwt.decode(
            credentials.credentials,
            SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            audience="authenticated"
        )

        print("payload:", payload)
        email: str | None = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        print("JWTError -->", e)
        raise credentials_exception

    # Fetch corresponding user from local DB
    user = await User.filter(email=email).first()
    if user is None:
        # Create a local profile from Supabase user data
        try:
            user = await User.create(
                email=email,
                username=payload.get("user_metadata", {}).get("username", email.split("@")[0]),
                first_name=payload.get("user_metadata", {}).get("first_name", ""),
                last_name=payload.get("user_metadata", {}).get("last_name", ""),
                is_verified=True,  # Since they authenticated through Supabase
                password_hash="supabase_auth"  # Placeholder since auth is handled by Supabase
            )
        except Exception as e:
            print(f"Error creating local user: {e}")
            raise credentials_exception

    return user

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    try:
        # Check if user already exists
        existing_user = await User.filter(email=user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = await User.filter(username=user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
        )
        user.set_password(user_data.password)
        await user.save()
        
        return UserResponse.from_orm(user)
    
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        ) 