from tortoise.models import Model
from tortoise import fields

class SessionParticipant(Model):
    id = fields.IntField(pk=True)
    session_id = fields.IntField()  # References session.id
    user_id = fields.IntField()     # References user.id
    role = fields.CharField(max_length=20, default="participant")  # "creator", "participant"
    joined_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    
    class Meta:
        table = "session_participants"
        unique_together = [("session_id", "user_id")]  # Each user can only be in a session once
        ordering = ["joined_at"]
    
    def __str__(self):
        return f"User {self.user_id} in Session {self.session_id} ({self.role})" 