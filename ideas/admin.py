from django.contrib import admin
from .models import Season,Idea,IdeaForm,FormQuestion,FormQuestionChoice,TeamMember,ExhibitionForm,ExhibitionQuestion,ExhibitionQuestionOption,ExhibitionSubmission        
from .phases import SeasonPhase

admin.site.register(SeasonPhase)
admin.site.register(Season)
admin.site.register(Idea)
admin.site.register(IdeaForm)
admin.site.register(FormQuestion)
admin.site.register(FormQuestionChoice)
admin.site.register(TeamMember)
admin.site.register(ExhibitionForm)     
admin.site.register(ExhibitionQuestion)
admin.site.register(ExhibitionQuestionOption)
admin.site.register(ExhibitionSubmission)



