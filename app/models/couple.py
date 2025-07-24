from tortoise.models import Model
from tortoise import fields


class Couple(Model):
    id = fields.IntField(pk=True)
    user1_id = fields.IntField()
    user2_id = fields.IntField()
    relationship_start_date = fields.DateField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)
    
    class Meta:
        table = "couples"
        unique_together = [("user1_id", "user2_id")]
    
    def __str__(self):
        return f"Couple: {self.user1_id} & {self.user2_id}"



"""
TODO - may be we need relationship duration field for each user 
as a field bc if a user has solo joined , may be we need that data point for better context
"""



