from django.db import models
import uuid


class Field(models.Model):
    """Ejemplo de modelo para `fields` (parcelas/lotes)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    surface_ha = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fields'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"
