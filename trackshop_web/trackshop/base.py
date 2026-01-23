import uuid
from django.db import models 

class BaseSyncModel(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    source = models.CharField(
        max_length=10,
        choices=[('web', 'Web'), ('desktop', 'Desktop')],
        default="web",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True