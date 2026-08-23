TEMPLATES = {
    #===============================
    # IDEAS
    #===============================
    "idea_submitted": {
        "title": "تم تقديم فكرة جديدة",
        "message": lambda obj, actor=None, extra=None: (
            f"قام المستخدم " f"{actor.full_name if actor else obj.owner.full_name} " f"بتقديم فكرة جديدة بعنوان " f"({obj.title}) " f"ضمن موسم {obj.season.name}" ) },


    "exhibition_submission_created": {
        "title": "تم إرسال بطاقة مشروع جديدة",
        "message": lambda obj, actor=None, extra=None: (
            f"قام المستخدم " f"{actor.full_name if actor else obj.project.owner.full_name} " f"بإكمال تعبئة بطاقة المشروع الخاصة بفكرته " f"({obj.project.title}) " f"وهي الآن بانتظار المراجعة." ) },

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
        "message": lambda obj, actor=None, extra=None: (
            f"وافق المستشار " f"{actor.full_name if actor else obj.volunteer.user.full_name} "
            f"على طلب الاستشارة الخاص بمشروعك " f"({obj.idea.title})" ) },

    "consultation_rejected": {
        "title": "تم رفض طلب الاستشارة",
        "message": lambda obj, actor=None, extra=None: (
            f"اعتذر المستشار " f"{actor.full_name if actor else obj.volunteer.user.full_name} "
            f"عن تقديم الاستشارة لمشروعك " f"({obj.idea.title}). " f"يمكنك اختيار مستشار آخر." ) },

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
            f"تسجيل جديد في ورشتك {obj.title} "
    },

    # ===============================
    # TEAM
    # ===============================
    "team_request_created": {
        "title": "طلب فريق جديد",
        "message": lambda obj, actor=None, extra=None: ( f"قام المستخدم " f"{actor.full_name if actor else obj.idea.owner.full_name} " f"بتقديم طلب تشكيل فريق " f"لفكرته ({obj.idea.title})" ) },
    
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
        "title": "تم قبول طلب الانضمام",
        "message": lambda obj, actor=None, extra=None: (
            f"وافق المتطوع " f"{actor.full_name if actor else obj.volunteer.user.full_name} "
            f"على الانضمام إلى فريق مشروعك " f"({obj.idea.title})" ) },

    "join_request_rejected": {
        "title": "تم رفض طلب الانضمام",
        "message": lambda obj, actor=None, extra=None: (
            f"اعتذر المتطوع " f"{actor.full_name if actor else obj.volunteer.user.full_name} "
            f"عن الانضمام إلى فريق مشروعك " f"({obj.idea.title})" ) },



    # ===============================
    # EVALUATION
    # ===============================
    "evaluation_joined_committee": {
        "title": "مرحباً بك في لجنة التقييم",
        "message": lambda obj, actor=None, extra=None:
            f"شكراً لك على الموافقة لطلب الانضمام "
            f"إلى لجنة تقييم موسم "
            f"{obj.season.name}. "
            f"أنت الآن عضو في لجنة التقييم." },


    "evaluation_invitation_accepted": {
        "title": "تم قبول دعوة لجنة التقييم",

        "message": lambda obj, actor=None, extra=None: (
        f"قام المقيم "
        f"{actor.full_name if actor else obj.user.full_name} "
        f"بقبول دعوة الانضمام إلى لجنة تقييم "
        f"موسم {obj.season.name}"
        )
    },

    "evaluation_invitation_rejected": {
        "title": "تم رفض دعوة لجنة التقييم",

        "message": lambda obj, actor=None, extra=None: (
        f"قام المقيم "
        f"{actor.full_name if actor else obj.user.full_name} "
        f"برفض دعوة الانضمام إلى لجنة تقييم "
        f"موسم {obj.season.name}"
        )
    },

    #==============================
    #BOOTCAMP
    #==============================

    "bootcamp_absence_request_submitted": {
        "title": "طلب غياب جديد",

        "message": lambda obj, actor=None, extra=None: (
            f'المستخدم {actor.full_name if actor else "غير معروف"} '
            f'قدّم طلب غياب عن جلسة: "{obj.session.title}"'
        )
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

    "season_published": {

        "title": "افتتاح موسم جديد للاحتضان",

        "message": lambda season: (
            f"تم إطلاق موسم ({season.name}) "
            f"لاحتضان الأفكار. "
            f"اضغط هنا لتقديم فكرتك."
        )
    },
    
    #----------------bootcamp------------------------------
    
    "bootcamp_started": {
        "title": "انطلاق المعسكر التدريبي",

        "message": lambda season: (
        f"انطلق المعسكر التدريبي لموسم ({season.name}). "
        f"ستقوم الإدارة بإرسال مواعيد الجلسات قريباً."
    )
    },
    
     
    "absence_approved": {
        "title": "طلب الغياب",
        "message": lambda obj: "تم قبول طلب الغياب الخاص بك "
    },
    "absence_warned": {
        "title": "تحذير",
        "message": lambda obj: "تم رفض طلب الغياب  يرجى الالتزام بالحضور"
    },
    
    "bootcamp_session_scheduled": {
        "title": "جلسة جديدة في المعسكر",

        "message": lambda session: (
            f"تمت إضافة جلسة جديدة في المعسكر "
            f"بتاريخ {session.date}"
        )
    },

    "bootcamp_session_assigned": {
        "title": "تم تعيينك كمدرب",

        "message": lambda session: (
            f"تم تعيينك كمدرب لجلسة المعسكر "
            f"بتاريخ {session.date}"
        )
    },
    "idea_bootcamp_approved": {
        "title": "تم قبول فكرتك 🎉",

        "message": lambda idea, actor=None: (
            f"مبروك! تم قبول فكرتك "
            f"({idea.title}) "
            f"والانتقال إلى المرحلة التالية."
        )
    },

    "idea_bootcamp_rejected": {
        "title": "تم رفض الفكرة",

        "message": lambda idea, actor=None: (
            f"نأسف، تم رفض فكرتك "
            f"({idea.title}) "
            f"بسبب عدم الالتزام بحضور المعسكر. "
            f"يمكنك المحاولة مرة أخرى في موسم قادم."
        )
    },
    "bootcamp_sessions_ended": {
        "title": "انتهاء جلسات المعسكر",
        "message": lambda season: f"تم انتهاء جلسات المعسكر لهذا الموسم ، انتظر قرار الادارة  بشأن الانتقال للمرحلة التالية."
    },
    
    
    #===================evaluation==========================
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
        "message": lambda idea, actor=None, extra=None: f"مبروك! تم قبول فكرتك '{idea.title}' اهلا بك في مرحلة الاحتضان "
    },
    
    "idea_rejected": {
        "title": "لم يتم قبول المشروع",
        "message": lambda idea, actor=None, extra=None:
            (
            f"لم يتم قبول مشروعك "
            f"({idea.title}) "
            f"في هذا الموسم. "
            f"يمكنك الاطلاع على ملاحظات اللجنة لتحسين فكرتك."
            )
    },
    
    
    #=====================incubation==============================
    "incubation_meeting_scheduled_owner": {
        "title": "موعد لجنة الاحتضان",

        "message": lambda data: (
            f"تم تحديد موعد لجنة الاحتضان "
            f"لفكرتك ({data['idea_title']}) "
            f"بتاريخ {data['meeting_date']}"
        )
    },

    "incubation_meeting_scheduled_mentor": {
        "title": "جلسة احتضان جديدة",

        "message": lambda data: (
            f"تمت إضافتك إلى جلسة احتضان "
            f"لفكرة ({data['idea_title']}) "
            f"بتاريخ {data['meeting_date']}"
        )
    },
    
    
    "idea_exhibition_graduated": {
        "title": "مبروك التخرج 🎉",

        "message": lambda idea: (
            f"مبروك! تم تخريج فكرتك "
            f"({idea.title}) بنجاح من الحاضنة."
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
    
    #===============exhibition=========================
    "exhibition_scheduled": {
        "title": "موعد معرض المشاريع",
    
        "message": lambda data: (
            f"ندعوكم لحضور معرض المشاريع المتخرجة لهذا العام "
            f"بتاريخ {data['exhibition_datetime'].strftime('%Y-%m-%d %H:%M')} "
            f"في حاضنة تقانة المعلومات والاتصالات."
        )
    },
    
    
    "exhibition_form_published": {

        "title": "بطاقة المعرض النهائي",

        "message": lambda idea: (
            f"حان وقت إعداد بطاقة مشروعك للمعرض النهائي "
            f"لمشروع ({idea.title})، "
            f"يرجى تعبئة بيانات المعرض المطلوبة."
        )
    },
    
    #=====================volunteer=======================================
    "volunteer_approved": {
        "title": "تم قبول طلب التطوع ",

        "message": lambda user: (
            "مرحباً بك كمتطوع في الحاضنة  "
            "يرجى تعديل ملفك الشخصي وإضافة معلوماتك."
        )
    },

    "volunteer_rejected": {
        "title": "تم رفض طلب التطوع",

        "message": lambda user: (
            "نقدر اهتمامك بالتطوع معنا، "
            "ولكن نأسف لإبلاغك بأنه لن يتم قبول طلب التطوع "
            "في الوقت الحالي."
        )
    },
    
    "evaluation_invitation_sent": {
        "title": "دعوة للانضمام إلى لجنة التقييم",

        "message": lambda invitation: (
            f"نود دعوتكم رسمياً للانضمام إلى لجنة تقييم المشاريع "
            f"لموسم {invitation.season.name} "
            f" والمطلوب:"
            f"{invitation.task}."
        )
    },
    
    "volunteers_suggested": {
        "title": "اقتراح متطوعين لفريق المشروع",

        "message": lambda obj: (
            f"تم اقتراح مجموعة من المتطوعين "
            f"لدعم مشروعك ({obj['idea'].title}). "
            f"يمكنك الآن الاطلاع عليهم واختيار "
            f"المناسب للانضمام إلى فريقك."
        )
    },
    
    #------------------admin_workshops-------------
    "workshop_approved": {

        "title": "تم اعتماد ورشة العمل",

        "message": lambda workshop: (
            f"تم اعتماد ورشة عملك بعنوان "
            f"({workshop.title}) "
            f"وتم نشرها ضمن قائمة الفعاليات."
        )
    },
    "new_workshop_published": {

        "title": "ورشة عمل جديدة",

        "message": lambda workshop: (
            f"ورشة عمل جديدة بعنوان "
            f"({workshop.title}). "
            f"سارع بالتسجيل، المقاعد محدودة."
        )
    },
    
    "workshop_rejected": {

        "title": "تم رفض ورشة العمل",

        "message": lambda data: (
            f"تم رفض ورشة عملك بعنوان "
            f"({data.title}). "
            f" سبب الرفض: "
            f"{data.rejection_reason}"
        )
    },
    
    

    "admin_manual_notification": {
        "title": "رسالة من الإدارة",
        "message": lambda data: data.get("message")
    },
    
    
    "ADMIN_BROADCAST_NOTIFICATION": {

        "title": "إشعار إداري",

        "message": lambda data: data.get("message")
    },



    

}

