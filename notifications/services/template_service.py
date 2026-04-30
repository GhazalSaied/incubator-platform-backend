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
        "title": "تم قبولك",
        "message": lambda obj, actor=None, extra=None:
            f"أصبحت الآن عضو في لجنة التقييم",
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
    
    
    "season_published": {
        "title": "فتح موسم جديد",
        "message": lambda season: f"تم فتح موسم {season.name} للتقديم، يمكنك الآن تقديم فكرتك."
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
}



  