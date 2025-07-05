from tortoise.models import Model
from tortoise import fields
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=50, unique=True)
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)
    password_hash = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, null=True)
    date_of_birth = fields.DateField(null=True)
    gender = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login = fields.DatetimeField(null=True)
    partner_id = fields.IntField(null=True) 
    
    class Meta:
        table = "users"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def set_password(self, password: str):
        """Set and hash the user's password."""
        self.password_hash = self.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password."""
        return self.verify_password(password, self.password_hash)
    
    async def update_last_login(self):
        """Update the user's last login timestamp."""
        self.last_login = datetime.utcnow()
        await self.save(update_fields=["last_login"])
