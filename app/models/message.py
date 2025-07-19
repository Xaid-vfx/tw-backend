from tortoise.models import Model
from tortoise import fields

class Message(Model):
    id = fields.IntField(pk=True)
    session_id = fields.IntField() 
    user_id = fields.IntField()     # (who is chatting)
    content = fields.TextField()
    sender_type = fields.CharField(max_length=10)  # "human" | "ai"
    message_status = fields.CharField(max_length=20, default="sent")  # "sent", "delivered", "read"
    reply_to_message_id = fields.IntField(null=True)  # For threading, may be if needed
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "messages"
        ordering = ["created_at"]
    
    def __str__(self):
        return f"Message {self.id} - {self.sender_type} to User {self.user_id}"
