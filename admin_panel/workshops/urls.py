# workshops/urls.py

from django.urls import path

from .views import (
    ApproveWorkshopAPIView,
    RejectWorkshopAPIView,
    WorkshopDetailsAPIView,
    WorkshopListAPIView
)

urlpatterns = [
   #\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض الورشات \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("",WorkshopListAPIView.as_view(),name="admin-workshops-list"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الورشة\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:workshop_id>/",WorkshopDetailsAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول ورشة\\\\\\\\\\\\\\\\\\\\\
    path("<int:workshop_id>/approve/",ApproveWorkshopAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض ورشة\\\\\\\\\\\\\\\\\\\\\
    path("<int:workshop_id>/reject/",RejectWorkshopAPIView.as_view()),
]