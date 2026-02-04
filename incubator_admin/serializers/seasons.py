from rest_framework import serializers
from ideas.models import Season

class SeasonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date', 'is_open']

    def validate(self, data):
        """
        منع وجود أكثر من موسم مفتوح بنفس الوقت
        """
        is_open = data.get('is_open', False)

        if is_open:
            exists_open_season = Season.objects.filter(is_open=True).exists()
            if exists_open_season:
                raise serializers.ValidationError(
                    "يوجد موسم فعّال حالياً، لا يمكن فتح أكثر من موسم بنفس الوقت."
                )

        return data


class SeasonPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id']

    def validate(self, attrs):
        season = self.instance

        # 1️⃣ تأكد في فورم
        if not hasattr(season, 'form'):
            raise serializers.ValidationError(
                "لا يمكن نشر الموسم قبل إنشاء فورم الأسئلة."
            )

        # 2️⃣ تأكد الفورم فيه أسئلة
        if season.form.questions.count() == 0:
            raise serializers.ValidationError(
                "لا يمكن نشر الموسم قبل إضافة أسئلة إلى الفورم."
            )

        # 3️⃣ تأكد ما في موسم مفتوح
        if Season.objects.filter(is_open=True).exclude(id=season.id).exists():
            raise serializers.ValidationError(
                "يوجد موسم منشور حالياً، يجب إغلاقه قبل نشر موسم جديد."
            )

        return attrs

    def save(self, **kwargs):
        season = self.instance
        season.is_open = True
        season.save()
        return season
