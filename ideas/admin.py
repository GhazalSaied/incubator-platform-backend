from django.contrib import admin
from .models import Season,Idea,IdeaForm,FormQuestion,FormQuestionChoice,TeamMember
from .phases import SeasonPhase

@admin.register(SeasonPhase)
class SeasonPhaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'season', 'phase', 'start_date', 'end_date']
admin.site.register(Season)
admin.site.register(Idea)
admin.site.register(IdeaForm)
admin.site.register(FormQuestion)
admin.site.register(FormQuestionChoice)
admin.site.register(TeamMember)


