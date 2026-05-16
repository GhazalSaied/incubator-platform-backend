TEMPLATES = {

    # ===============================
    # CONSULTATIONS
    # ===============================

    "consultation_requested": {
        "title": "طلب استشارة جديد",
        "message": lambda obj, actor=None, extra=None: 
            f"لديك طلب استشارة جديد في مشروع {obj.idea.title} في مجال {obj.idea.sector}",
    },

    "consultation_decided": {
        "title": "تم الرد على طلبك",
        "message": lambda obj, actor=None, extra=None:
            f"تم {'قبول' if extra=='accept' else 'رفض'} طلبك",
    },

    "consultation_accepted": {
    "title": "تم قبول طلب الاستشارة",
    "message": lambda obj, actor=None, extra=None:
        f"تم قبول طلب الاستشارة من المستشار {actor.full_name}",
    },

    "consultation_rejected": {
        "title": "تم رفض طلب الاستشارة",
        "message": lambda obj, actor=None, extra=None:
            f"اعتذر المستشار {actor.full_name} عن قبول طلبك. يمكنك اختيار مستشار اخر",
    },

    # ===============================
    # WORKSHOPS
    # ===============================

    "workshop_submitted": {
        "title": "ورشة جديدة",
        "message": lambda obj, actor=None, extra=None:
            f"تمت إضافة ورشة جديدة بعنوان {obj.title} من قبل {actor.full_name}",
    },

    "workshop_registered": {
        "title": "تسجيل جديد",
        "message": lambda obj, actor=None, extra=None:
            f"تسجيل جديد في ورشتك {obj.title} - العدد الحالي: {(extra or {}).get('registrations_count')}"
    },

    # ===============================
    # TEAM
    # ===============================

    "join_request_sent": {
        "title": "طلب انضمام",
        "message": lambda obj, actor=None, extra=None:
            f"لديك طلب تطوع جديد من مشروع {obj.title} في مجال {obj.sector}",
    },

    "team_completed": {
    "title": "اكتمل الفريق ",
    "message": lambda idea: f"اكتمل فريق مشروع {idea.title}",
    },



    "join_request_accepted": {
    "title": "تم انضمام متطوع",
    "message": lambda obj, actor=None, extra=None:
        f"تم انضمام {actor.full_name} إلى فريق مشروعك",
    },

    "join_request_rejected": {
        "title": "تم رفض الطلب",
        "message": lambda obj, actor=None, extra=None:
            f"رفض المتطوع {actor.full_name} الانضمام إلى فريقك",
    },



    # ===============================
    # EVALUATION
    # ===============================

    "evaluation_invitation_sent": {
        "title": "دعوة لجنة تقييم",
        "message":lambda obj, actor=None, extra=None: 
            f"تم دعوتك للانضمام إلى لجنة تقييم ({obj.season.name})",
    },

    "evaluation_invitation_accepted": {
        "title": "قبول دعوة لجنة التقييم",
        "message": lambda obj, actor=None, extra=None:
            f"تم قبول طلب الانضمام إلى لجنة التقييم لموسم {obj.season.name} من قبل المقيم {actor.full_name if actor else obj.user.full_name}"
    },

    "evaluation_invitation_rejected": {
        "title": "رفض دعوة لجنة التقييم",
        "message": lambda obj, actor=None, extra=None:
            f"رفض المقيم {actor.full_name if actor else obj.user.full_name} الانضمام إلى لجنة التقييم لموسم {obj.season.name}"
    },

    
    # ===============================
    # SYSTEM
    # ===============================

    "message_sent": {
        "title": "رسالة جديدة",
        "message": lambda obj, actor=None, extra=None:
            f"لديك رسالة من {actor.full_name}",
    },

    "account_suspended": {
        "title": "تم تجميد الحساب",
        "message": lambda obj, actor=None, extra=None:
            f"تم تجميد حسابك مؤقتاً",
    },

    "idea_status_changed": {
        "title": "تحديث حالة الفكرة",
        "message": lambda obj, actor=None, extra=None:
            f"تم تغيير حالة فكرتك إلى {extra}",
    },
    
      
      
      
      
      
      
      
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\     
#----------------------ADMIN------------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
    #-----------------season------------------------------
    
    
    # notifications/services/template_service.py

    "season_published": {

        "title": "افتتاح موسم جديد للاحتضان",

        "message": lambda season: (
            f"تم إطلاق موسم ({season.name}) "
            f"لاحتضان الأفكار. "
            f"اضغط هنا لتقديم فكرتك."
        )
    },
    
    "submission_closed": {
        "title": "تم إغلاق التقديم",
        "message": lambda season: f"تم إغلاق التقديم لموسم {season.name}، سيتم الانتقال إلى المرحلة التالية."
    },
    
    
    "absence_approved": {
        "title": "طلب الغياب",
        "message": lambda obj: "تم قبول طلب الغياب الخاص بك ✅"
    },
    "absence_warned": {
        "title": "تحذير",
        "message": lambda obj: "تم رفض طلب الغياب ⚠️ يرجى الالتزام بالحضور"
    },
    
    "bootcamp_session_scheduled": {
        "title": "جلسة جديدة في المعسكر",
        "message": lambda session, extra=None: f"تم جدولة جلسة جديدة في المعسكر بتاريخ {session.date}"
    },
    "bootcamp_session_assigned": {
        "title": "تم تعيينك كمدرب",
        "message": lambda session, extra=None: f"تم تعيينك كمدرب للجلسة بتاريخ {session.date}"
    },
    "idea_approved": {
        "title": "تم قبول فكرتك 🎉",
    "message": lambda idea, actor: f"مبروك! تم قبول فكرتك '{idea.title}' والانتقال للمرحلة التالية 🚀"

},

    "idea_rejected": {
        "title": "تم رفض الفكرة",
    "message": lambda idea, actor: f"نأسف! تم رفض فكرتك لعدم التزامك بحضور المعسكر يمكنك المحاولة مرة اخرى'{idea.title}'"
},
    "bootcamp_sessions_ended": {
    "title": "انتهاء جلسات المعسكر",
    "message": lambda season: f"تم انتهاء جلسات المعسكر لهذا الموسم ، انتظر قرار الادارة  بشأن الانتقال للمرحلة التالية."
},
    
    "evaluation_meeting_scheduled_owner": {
        "title": "تم تحديد موعد اللجنة",
        "message": lambda data: (
            f"تم تحديد موعد لجنة التقييم لفكرتك "
            f"({data['idea'].title}) "
            f"بتاريخ "
            f"{data['meeting_datetime'].strftime('%Y-%m-%d %H:%M')}"
        )
    },
    
    "evaluation_meeting_scheduled_evaluator": {
        "title": "جلسة تقييم جديدة",
        "message": lambda data: (
            f"لديك جلسة تقييم لفكرة "
            f"({data['idea'].title}) "
            f"بتاريخ "
            f"{data['meeting_datetime'].strftime('%Y-%m-%d %H:%M')}"
        )
    },
    "idea_accepted": {
        "title": "تم قبول فكرتك 🎉",
        "message": lambda idea, actor=None, extra=None: f"مبروك! تم قبول فكرتك '{idea.title}' اهلا بك في مرحلة الاحتضان 🚀"
    },
    "idea_rejected": {
        "title": "تم رفض الفكرة",
        "message": lambda idea, actor=None, extra=None: f"نأسف! تم رفض فكرتك....لا تيأس يمكنك المحاولة في موسم أخر"
    },
    
    "incubation_meeting_scheduled_owner": {
    "title": "موعد لجنة الاحتضان",

    "message": lambda data: (
        f"تم تحديد موعد لجنة الاحتضان "
        f"لفكرتك بتاريخ "
        f"{data['meeting_date']}"
    )
},
    "incubation_meeting_scheduled_mentor": {
    "title": "جلسة احتضان جديدة",

    "message": lambda data: (
        f"تمت إضافتك إلى جلسة احتضان "
        f"بتاريخ {data['meeting_date']}"
    )
},
    "idea_Exhibition_graduated": {
    "title": "مبروك التخرج 🎉",

    "message": lambda idea: (
        f"مبروك! تم تخريج فكرتك "
        f"({idea.title}) بنجاح من الحاضنة， "
        f"يرجى البدء بتجهيز بطاقة المعرض الخاصة بمشروعك."
    )
},
    "idea_graduated_negative": {
    "title": "إشعار تخريج",

    "message": lambda idea: (
        f"مع الأسف تم تخريج فكرتك "
        f"({idea.title}) من الحاضنة بشكل سلبي "
        f"نظراً لعدم الالتزام بمتطلبات البرنامج."
    )
},
    "exhibition_scheduled": {
    "title": "تم تحديد موعد المعرض",
    "message": lambda data: (
        f"تم تحديد موعد معرض الموسم {data['season_id']} "
        f"بتاريخ {data['exhibition_datetime']}"
    )
    },
    
    
    "exhibition_form_published": {

    "title": "تم نشر فورم المعرض 🎉",

    "message": lambda idea: (
        f"تم نشر فورم المعرض الخاص بمشروعك "
        f"({idea.title})، "
        f"يرجى تعبئة بيانات بطاقة المعرض."
    )
},
     "volunteer_approved": {
        "title": "تم قبول طلب التطوع 🎉",
        "message": "مبروك! تم قبول طلبك كمتطوع عدل ملفك الشخصي واضف معلوماتك."
    },
    "volunteer_rejected": {
        "title": "تم رفض طلب التطوع",
        "message": lambda user : ( "نعتذر، تم رفض طلب التطوع الخاص بك. يمكنك المحاولة مرة أخرى لاحقاً.")
    },
    
    "evaluation_invitation_sent": {
        "title": "دعوة تقييم جديدة",

        "message": lambda invitation: (
            f"تمت دعوتك كمقيم.\n"
            f"المهمة: {invitation.task}\n"
            f"المدة: {invitation.expected_duration} دقيقة"
        )
    },
    
    "evaluator_role_removed": {
        "title": "إزالة دور المقيم",
        "message": lambda user: (
            "تمت إزالة دورك كمقيم من النظام.\n"
            "لم تعد قادراً على تقييم المشاريع حالياً."
        )
    },
    
    
    "volunteers_suggested": {
        "title": "تم اقتراح متطوعين ",
        "message": lambda obj: (
        f"تم اقتراح متطوعين من قبل الإدارة لفكرتك \"{obj['idea'].title}\". "
        f"يمكنك الآن الاطلاع عليهم واختيار المناسب."
    )
},
    
    
    #------------------admin_workshops-------------
    "workshop_approved": {

    "title": "تم قبول الورشة",

    "message": lambda workshop:
        f"تم قبول ورشة العمل ({workshop.title}) بنجاح"
},
    
    "workshop_rejected": {

    "title": "تم رفض الورشة",

    "message": lambda data:
        f"تم رفض ورشة ({data['workshop'].title}) بسبب: {data['rejection_reason']}"
<<<<<<< Updated upstream
}
=======
},
    
    "admin_manual_notification": {
        "title": "رسالة من الإدارة",
        "message": lambda data: data.get("message")
    },
    
    
    "ADMIN_BROADCAST_NOTIFICATION": {

        "title": "إشعار إداري",

        "message": lambda data: data.get("message")
    },

>>>>>>> Stashed changes


    

}



  