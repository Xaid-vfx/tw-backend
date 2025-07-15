from tortoise.models import Model
from tortoise import fields
import secrets
import string

class Session(Model):
    id = fields.IntField(pk=True)
    session_code = fields.CharField(max_length=8, unique=True)  # Shareable code
    creator_user_id = fields.IntField()  
    session_mode = fields.CharField(max_length=10, default="couple")  # "solo" or "couple"
    couple_id = fields.IntField(null=True)  # References couple.id (null for solo)
    current_participants = fields.IntField(default=1)  
    status = fields.CharField(max_length=20, default="active")  # "active", "completed", etc.
    max_participants = fields.IntField(default=2)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "sessions"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Session {self.session_code} - {self.session_mode} - Creator: {self.creator_user_id}"
    
    @classmethod
    def generate_session_code(cls) -> str:
        """Generate a unique 8-character session code."""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    async def add_participant(self, user_id: int) -> bool:
        """Add a participant to the session if there's space."""
        # Ensure we don't exceed the maximum allowed participants
        if self.current_participants >= self.max_participants:
            return False
        self.current_participants += 1
        await self.save(update_fields=["current_participants"])
        return True
    
    async def remove_participant(self, user_id: int) -> bool:
        """Remove a participant from the session."""
        if self.current_participants > 0:
            self.current_participants -= 1
            await self.save(update_fields=["current_participants"])
            return True
        return False
