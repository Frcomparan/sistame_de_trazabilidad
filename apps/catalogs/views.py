from rest_framework import generics
from .models import Field
from rest_framework import serializers


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


class FieldListView(generics.ListAPIView):
    queryset = Field.objects.filter(is_active=True)
    serializer_class = FieldSerializer
