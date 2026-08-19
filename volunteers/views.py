from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.events import EventBus
from datetime import datetime, date
from rest_framework.parsers import MultiPartParser, FormParser
from core.permissions import CanManageUsers
from messaging.models import Conversation


from notifications.models import Notification
from messaging.models import Conversation
from datetime import datetime, date

from .models import (
    VolunteerProfile,
    VolunteerAvailability,
    ConsultationRequest, 
    Workshop,
    WorkshopRegistration,
    VolunteerVacation,
    JoinRequest
      
      )
from .serializers import (
    VolunteerProfileSerializer,
    VolunteerAvailabilitySerializer,
    VolunteerAvailabilityCreateUpdateSerializer,
    CreateWorkshopSerializer,
    CreateJoinRequestSerializer,
    JoinRequestSerializer,
    ConsultantListSerializer,
    VolunteerVacationSerializer,
   

    ConsultationRequestSerializer,

    CreateConsultationRequestSerializer,
)
from volunteers.services.volunteer_service import VolunteerService
from ideas.models import TeamMember 
from notifications.services.notification_service import NotificationService
from django.contrib.auth import get_user_model
from django.db import transaction
User = get_user_model()

from core.permissions import(CanManageWorkshop,
                             CanManageVolunteerRequests,
                             CanSendMessage,
                             CanSendJoinRequest,
                             CanManageVolunteerProfile,
                             CanViewConsultants,
                             ) 




#/////////////////////////// VOLUNTEER APPLY ///////////////////////

class VolunteerApplyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, "volunteer_profile"):
            return Response(
                {"detail": "لديك طلب تطوع سابق"},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            profile = VolunteerProfile.objects.create(
                user=request.user,
                primary_skills=request.data["primary_skills"],
                years_of_experience=request.data["years_of_experience"],
                current_company=request.data.get("current_company"),
                specialization=request.data.get("specialization"),
                volunteer_type=request.data["volunteer_type"],
                residence=request.data["residence"],
                motivation=request.data["motivation"],
            )

            # availability
            availability_data = request.data.get("availability", [])

            if not availability_data:
                return Response(
                    {"detail": "يجب إدخال أوقات التوفر"},
                    status=400
                )

            for item in availability_data:
                serializer = VolunteerAvailabilityCreateUpdateSerializer(
                    data=item,
                    context={"request": request}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(volunteer=profile)

        return Response(
            {"detail": "تم إرسال الطلب"},
            status=201
        )


#/////////////////////////// VOLUNTEER PROFILE ///////////////////////

class VolunteerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            VolunteerProfileSerializer(
                request.user.volunteer_profile
            ).data
        )



#/////////////////////////// UPDATE VOLUNTEER PROFILE ///////////////////////

class VolunteerProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerProfile]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=status.HTTP_404_NOT_FOUND
            )

       
        user = request.user
        user.full_name = request.data.get("full_name", user.full_name)
        user.phone = request.data.get("phone", user.phone)
        user.email = request.data.get("email",user.email)
        if request.FILES.get("avatar"):
            user.avatar = request.FILES.get("avatar")
 
        user.save()


       
        profile.residence = request.data.get("residence", profile.residence)
        profile.years_of_experience = request.data.get("years_of_experience", profile.years_of_experience)
        profile.primary_skills = request.data.get("primary_skills", profile.primary_skills)
        profile.additional_skills = request.data.get("additional_skills", profile.additional_skills)
        profile.volunteer_type = request.data.get("volunteer_type", profile.volunteer_type)
        profile.availability_type = request.data.get("availability_type", profile.availability_type)
        profile.projects_count = request.data.get("projects_count",profile.projects_count)
        profile.bio=request.data.get("bio",profile.bio)
        profile.save()

        return Response({
            "detail": "تم التحديث"
        })
    
#/////////////////////////// AVAILABLITY  CREATE ///////////////////////

class VolunteerAvailabilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerProfile]

    def post(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VolunteerAvailabilityCreateUpdateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        availability = serializer.save(volunteer=profile)

        return Response(
            VolunteerAvailabilityCreateUpdateSerializer(availability).data,
            status=status.HTTP_201_CREATED
        )

#////////////////////////////// AVAILABLITY VIEW  //////////////////////////////

class VolunteerAvailabilityListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=404
            )

        data = [
            {
                "id": a.id,
                "day": a.day,
                "from": a.start_time,
                "to": a.end_time,
            }
            for a in profile.availabilities.all().order_by("day", "start_time")
        ]

        return Response(data)

#///////////////////////// AVAILABLITY DELETE ///////////////////////////


class VolunteerAvailabilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerProfile]

    def delete(self, request, availability_id):
        try:
            availability = VolunteerAvailability.objects.get(
                id=availability_id,
                volunteer=request.user.volunteer_profile
            )
        except (VolunteerAvailability.DoesNotExist, VolunteerProfile.DoesNotExist):
            return Response(
                {"detail": "غير مسموح"},
                status=status.HTTP_404_NOT_FOUND
            )

        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


#/////////////////////////////// VOLUNTEER DASHBOARD VIEW //////////////////////////////////////////////

class VolunteerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            data = VolunteerService.get_dashboard(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response({
            "profile": VolunteerProfileSerializer(data["profile"]).data,
            "availability": VolunteerAvailabilitySerializer(
                data["availability"], many=True
            ).data,
            "consultations": data["consultations"],
            "workshop_stats": data["workshop_stats"],
            "next_workshop": data["next_workshop"],
        })



#///////////////////////// Consultation REQUEST VIEW ///////////////////////////////////

class MyConsultationRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def get(self, request):

        profile = request.user.volunteer_profile

        if not hasattr(request.user, "volunteer_profile"):
             return Response({"detail": "ليس لديك صلاحية"}, status=403)

        request_type = request.query_params.get("type")

        requests = ConsultationRequest.objects.filter(
            volunteer=profile,
            status=ConsultationRequest.PENDING
        )

        if request_type:
            requests = requests.filter(request_type=request_type)

        requests = requests.order_by("-created_at")

        serializer = ConsultationRequestSerializer(requests, many=True)
        return Response(serializer.data)


#///////////////////////// [ACCEPT/REJECT] Consultation ///////////////////////////////////

class ConsultationRequestDecisionAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def post(self, request, request_id):

        action = request.data.get("action")

        if action not in ["accept", "reject"]:
            return Response({"detail": "إجراء غير صالح"}, status=400)

        

        try:
            consultation = VolunteerService.handle_consultation_decision(
                user=request.user,
                request_id=request_id,
                action=action
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        

        return Response(status=status.HTTP_200_OK)
    

    
#//////////////////////////// CREATE CONSULTATION REQUEST /////////////////////////////////////////

class CreateConsultationRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,volunteer_user_id):

        serializer = CreateConsultationRequestSerializer(
            data=request.data,
            context={
                "request": request,
                "volunteer_user_id": volunteer_user_id,
                
                }
        )
        serializer.is_valid(raise_exception=True)

        consultation = serializer.save(
            requester=request.user
        )

        # Notification للمتطوع
        EventBus.emit(
            "consultation_requested", 
            consultation=consultation,
            action="accept",
            actor=request.user,
        )
       

        

        return Response(
            {"detail": "طلبك قيد المراجعة من قبل المتطوع"},
            status=201
        )
 

#/////////////////////////////////// CREATE JOIN REQUEST ////////////////////////

class CreateJoinRequestAPIView(APIView):
    permission_classes = [IsAuthenticated,CanSendJoinRequest]

    def post(self, request,volunteer_user_id):

        serializer = CreateJoinRequestSerializer(
            data=request.data,
            context={
                "request": request,
                "volunteer_user_id": volunteer_user_id,
            }
        )
        serializer.is_valid(raise_exception=True)

        join_request = serializer.save()

        EventBus.emit(
            "join_request_sent",
            join_request=join_request,
            actor=request.user,
        )

        return Response(
            {"detail": "طلبك قيد المراجعة من قبل المتطوع"}, 
            status=201
        )
    
#//////////////////////////////////// JOIN REQUEST (GET LIST) ///////////////////////

class JoinRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def get(self, request):
        profile = request.user.volunteer_profile

        requests = JoinRequest.objects.filter(
            volunteer=profile,
            status=JoinRequest.PENDING
        )

        return Response(JoinRequestSerializer(requests, many=True).data)
    
#////////////////////////////////// JOIN REQUEST DETAILS //////////////////////

class JoinRequestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def get(self, request, request_id):
        jr = get_object_or_404(
            JoinRequest,
            id=request_id,
            volunteer=request.user.volunteer_profile
        )

        idea = jr.idea

        return Response({
            "requester": {
                "name": jr.requester.full_name,
                "email": jr.requester.email,
            },
            "project": {
                "title": idea.title,
                "target_audience":  idea.target_audience,
                "problem": idea.answers.get("problem"),
            },
            "request": {
                "required_skill": jr.required_skill,
                "tasks": jr.tasks,
                "description": jr.description,
            }
        })
    
#/////////////////////////////////// JOIN REQUEST DECISION [ACCEPT | REJECT ] /////////////////////////

class JoinRequestDecisionAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def post(self, request, request_id):
        action = request.data.get("action")

        if action not in ["accept", "reject"]:
            return Response({"detail": "إجراء غير صالح"}, status=400)

        try:
            jr = VolunteerService.handle_join_request_decision(
                user=request.user,
                request_id=request_id,
                action=action
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        return Response(
             status=status.HTTP_200_OK
        )
    
#////////////////////////////////// ALL VOLUNTEER REQUESTS /////////////////////////////

class MyAllRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageVolunteerRequests]

    def get(self, request):
        profile = request.user.volunteer_profile
        request_type = request.query_params.get("type")  # all / consultation / join

        consultations = ConsultationRequest.objects.filter(
            volunteer=profile,
            status=ConsultationRequest.PENDING
        )

        joins = JoinRequest.objects.filter(
            volunteer=profile,
            status=JoinRequest.PENDING
        )

        if request_type == "consultation":
            return Response({
                "consultations": ConsultationRequestSerializer(consultations, many=True).data
            })

        if request_type == "join":
            return Response({
                "join_requests": JoinRequestSerializer(joins, many=True).data
            })

        return Response({
            "consultations": ConsultationRequestSerializer(consultations, many=True).data,
            "join_requests": JoinRequestSerializer(joins, many=True).data
        })
    

#//////////////////////////////////// Assigned Projects APIView  ////////////////////////////////////////

class AssignedProjectsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.volunteer_profile
        if profile.status != "APPROVED":
            return Response({"detail": "الحساب غير مفعل"}, status=403)

        #  الاستشارات المقبولة
        consultations = ConsultationRequest.objects.filter(
            volunteer=profile,
            status=ConsultationRequest.ACCEPTED,
            help_type=ConsultationRequest.ONE_TIME

        ).order_by("-created_at")

        consultations_data = [
            {
                "idea_id": c.idea.id,
                "idea_title": c.idea.title,
                "description": c.description,
                "requester_name": c.requester.full_name if c.requester else None,
                "requester_email": c.requester.email if c.requester else None,
                "required_skill": c.required_skill,
                "help_type": c.help_type,
                "requester_id": c.requester.id if c.requester else None,
            }
            for c in consultations
        ]

        #  المتابعة
        ongoing =  ConsultationRequest.objects.filter(
            volunteer=profile,
            status=ConsultationRequest.ACCEPTED,
            help_type=ConsultationRequest.ONGOING
            
        ).order_by("-created_at")

        ongoing_data = [
        {
            "idea_id": c.idea.id,
            "idea_title": c.idea.title,
            "description": c.description,
            "requester_name": c.requester.full_name if c.requester else None,
            "requester_email": c.requester.email if c.requester else None,
            "required_skill": c.required_skill,
            "help_type": c.help_type,
            "requester_id": c.requester.id if c.requester else None,
        }
        for c in ongoing
    ]

        #  المشاريع المنضم لها
        joined = TeamMember.objects.filter(user=request.user)

        joined_data = [
            {
                "idea_id": j.idea.id,
                "idea_title": j.idea.title,
                "owner_name": j.idea.owner.full_name,
                "owner_email": j.idea.owner.email,
            }
            for j in joined
        ]

        return Response({
            "consultations": consultations_data,
            "ongoing": ongoing_data,
            "joined_projects": joined_data
        })
    
    

#//////////////////////// MY WORKSHOPS > للمتطوع  ///////////////////

class MyWorkshopsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageWorkshop]

    def get(self, request):
        workshops = Workshop.objects.filter(
            created_by=request.user
        )

        data = []

        for w in workshops:
            data.append({
                "id": w.id,
                "title": w.title,
                "start_date": w.start_date,
                "end_date": w.end_date,
                "sessions": w.sessions,
                "days": w.days,
                "time_from": w.time_from,
                "time_to": w.time_to,
                "category": w.category,
                "status": w.status,
            })

        return Response(data)


#/////////////////////// MY WORKSHOPS DETAILS ///////////////////


class MyWorkshopDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        CanManageWorkshop
    ]

    def get(self, request, workshop_id):

        user = request.user

        # تحقق هل المستخدم أدمن
        is_admin = (
            user.userrole_set
            .filter(
                role__code="ADMIN",
                is_active=True
            )
            .exists()
        )

        # الأدمن يشوف أي ورشة
        if is_admin:
            workshop = get_object_or_404(
                Workshop,
                id=workshop_id
            )

        # المتطوع يشوف فقط ورشاته
        else:
            workshop = get_object_or_404(
                Workshop,
                id=workshop_id,
                created_by=user
            )

        data = {
            "id": workshop.id,
            "title": workshop.title,
            "description": workshop.description,
            "objectives": workshop.objectives,
            "target_audience": workshop.target_audience,
            "start_date": workshop.start_date.strftime("%Y/%m/%d"),
            "end_date": workshop.end_date.strftime("%Y/%m/%d"),
            "days": workshop.days,
            "time_from": workshop.time_from.strftime("%H:%M"),
            "time_to": workshop.time_to.strftime("%H:%M"),
            "category": workshop.category,
            "sessions": workshop.sessions,
            "status": workshop.status,

            # معلومات المتطوع
            "volunteer_name":
                workshop.created_by.full_name,

            "volunteer_email":
                workshop.created_by.email,
        }

        if workshop.image:
            data["image"] = (
                request.build_absolute_uri(
                    workshop.image.url
                )
            )

        if workshop.status == "ACCEPTED":
            data["registrations"] = [
                {
                    "name": r.name,
                    "email": r.email,
                }
                for r in workshop.registrations.all()
            ]

        elif workshop.status == "REJECTED":
            data["rejection_reason"] = (
                workshop.rejection_reason
            )

        return Response(data)
    

#//////////////////////// CREATE WORKSHOP ///////////////////
from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)

class CreateWorkshopAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        CanManageWorkshop
    ]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def post(self, request):

        print("FILES ===>", request.FILES)
        print("DATA ===>", request.data)

        serializer = CreateWorkshopSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        workshop = serializer.save(
            created_by=request.user
        )

        print("IMAGE SAVED ===>", workshop.image)
        EventBus.emit(
            "workshop_submitted",
            workshop=workshop,
            
            actor=request.user
        )

        return Response({
            "detail": "تم إنشاء الورشة"
        })
#///////////////////// WORKSHOPS FOR PUBLIC //////////////
class PublicWorkshopsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filter_type = request.GET.get("filter")

        workshops = Workshop.objects.filter(status="ACCEPTED")

        today = timezone.now().date()

        if filter_type == "upcoming":
            workshops = workshops.filter(start_date__gt=today)

        elif filter_type == "ongoing":
            workshops = workshops.filter(
                start_date__lte=today,
                end_date__gte=today
            )

        elif filter_type == "finished":
            workshops = workshops.filter(end_date__lt=today)

        data = []

        for w in workshops:

            image_url = None

            if w.image:
                image_url = request.build_absolute_uri(
                    w.image.url
                )

            data.append({
                "id": w.id,
                "title": w.title,
                "description": w.description,
                "image": image_url,
                "capacity": w.capacity,
                "trainer_name": w.created_by.full_name,
                "status": (
                    "لم تبدأ بعد"
                    if w.start_date > today
                    else "منتهية"
                    if w.end_date < today
                    else "بدأت حديثاً"
                )
            })

        return Response(data)
#///////////////////// WORKSHOPS DETAILS FOR PUBLIC //////////////

class WorkshopDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workshop_id):
        w = get_object_or_404(
            Workshop,
            id=workshop_id,
            status="ACCEPTED"
        )

        image_url = None

        if w.image:
            image_url = request.build_absolute_uri(
                w.image.url
            )

        return Response({
            "title": w.title,
            "description": w.description,
            "start_date": w.start_date,
            "days": w.days,
            "time_from": w.time_from,
            "time_to": w.time_to,
            "target_audience": w.target_audience,
            "image": image_url,
        })

#/////////// WORKSHOP REGISTER > PUBLIC  اليوزرات اللي بدن يسجلوا بالورشات ////////



class RegisterWorkshopAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workshop_id):
        workshop = get_object_or_404(
            Workshop,
            id=workshop_id,
            status="ACCEPTED"
        )

        today = timezone.now().date()
        if workshop.end_date < today:
            return Response({"detail": "انتهت الورشة"}, status=400)

        #   منع التسجيل المكرر
        exists = WorkshopRegistration.objects.filter(
            user=request.user,
            workshop=workshop
        ).exists()

        if exists:
            return Response({"detail": "أنت مسجل مسبقاً"}, status=400)

        if workshop.registrations.count() >= workshop.capacity:
            return Response({"detail": "الورشة ممتلئة"}, status=400)

        WorkshopRegistration.objects.create(
            user=request.user,
            workshop=workshop,
            name=request.user.full_name,
            email=request.user.email
        )
        count = workshop.registrations.count()
        EventBus.emit(
            "workshop_registered",
            workshop=workshop,
            user=request.user,
            registrations_count=count,
            actor=request.user
        )

        return Response({"detail": "تم التسجيل"})

#//////////////////////// NEAREST WORKSHOP /////////////////////////////

class NearestWorkshopAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageWorkshop]

    def get(self, request):
        today = timezone.now().date()

        workshop = Workshop.objects.filter(
            status="ACCEPTED",
            start_date__gte=today
        ).order_by("start_date").first()

        if not workshop:
            return Response({"detail": "لا يوجد ورشات قادمة"})

        return Response({
            "title": workshop.title,
            "date": workshop.start_date.strftime("%A %Y-%m-%d"),
            "time": f"{workshop.time_from.strftime('%I').lstrip('0')}-{workshop.time_to.strftime('%I %p')}"
        })      


#/////////////////// CANCEL WORKSHOP REGISTRATION /////////////

class CancelWorkshopRegistrationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workshop_id):
        WorkshopRegistration.objects.filter(
            user=request.user,
            workshop_id=workshop_id
        ).delete()

        return Response({"detail": "تم إلغاء التسجيل"})


#/////////// MY REGISTERED WORKSHOPS > كل ورشات العمل اللي مسجل فيها اليوز //////

class MyRegisteredWorkshopsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        registrations = WorkshopRegistration.objects.filter(
            user=request.user
        ).select_related("workshop")

        data = []

        for r in registrations:
            w = r.workshop

            data.append({
                "id": w.id,
                "title": w.title,
                "start_date": w.start_date,
                "status": w.status
            })

        return Response(data)
    
#////////////////////// PUBLIC VIEW عرض كما يظهر للاخرين /////////////

class PublicVolunteerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        try:
            profile = user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response({"detail": "ليس متطوع"}, status=404)

        availability = profile.availabilities.all()

        total_hours = 0
        availability_data = []

        for a in availability:
            hours = (
                datetime.combine(date.min, a.end_time) -
                datetime.combine(date.min, a.start_time)
            ).seconds / 3600

            total_hours += hours

            availability_data.append({
                "day": a.day,
                "from": a.start_time,
                "to": a.end_time,
            })

        

        return Response({
            "user_id": user.id,
            "name": user.full_name,
            "email": user.email,
            "residence": profile.residence,
            "avatar": user.avatar.url if user.avatar else None,
            "availability": availability_data,
            "bio": profile.bio,
            "additional_skills": profile.additional_skills,
            "years_of_experience": profile.years_of_experience,
            "primary_skills": profile.primary_skills,
            "projects_count": profile.projects_count,
            "availability_type": profile.availability_type,
            "volunteer_type": profile.volunteer_type,
            "specialization":profile.specialization,
        })
    
#///////////////////// VOLUNTEER VACATION VIEW (ADD + VIEW)  //////////////////////



class VolunteerVacationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vacations = request.user.volunteer_profile.vacations.all()

        data = [
            {
                "id": vacation.id,
                "start_day": vacation.start_day,
                "end_day": vacation.end_day,
            }
            for vacation in vacations
        ]

        return Response(data)

    def post(self, request):

        profile = request.user.volunteer_profile

        serializer = VolunteerVacationSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        vacation = serializer.save(
            volunteer=profile
        )

        return Response(
            VolunteerVacationSerializer(vacation).data,
            status=status.HTTP_201_CREATED
        )


#////////////////////// DELETE VACATION //////////////////////


class DeleteVolunteerVacationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, vacation_id):
        VolunteerVacation.objects.filter(
            id=vacation_id,
            volunteer=request.user.volunteer_profile
        ).delete()

        return Response({"detail": "تم الحذف"})
    
#/////////////////////// CONSULTANTS LIST عرض المستشارين /////////////////////////

class ConsultantByPrimarySkillAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewConsultants]

    def get(self, request, primary_skill):
        consultants = VolunteerService.get_consultants_by_primary_skill(
            primary_skill=primary_skill
        )

        if not consultants.exists():
            return Response(
                {
                    "message": "No consultants found for this primary skill."
                },
                status=status.HTTP_200_OK
            )

        serializer = ConsultantListSerializer(
            consultants,
            many=True
        )

        return Response(
            {
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )