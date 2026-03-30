from rest_framework import serializers
from bootcamp.models import BootcampSession,BootcampAttendance


class BootcampSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BootcampSession
        fields = '__all__'

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time")
        return data
    
    
    
    



class BootcampAttendanceSerializer(serializers.ModelSerializer):
    idea_name = serializers.CharField(source='idea.title', read_only=True)

    class Meta:
        model = BootcampAttendance
        fields = [
            'id',
            'idea',
            'idea_name',
            'status',
        ]