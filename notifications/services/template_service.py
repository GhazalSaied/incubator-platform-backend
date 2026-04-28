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
        "title": "تم إرسال الورشة",
        "message": lambda obj, actor=None, extra=None: f"تم إرسال ورشتك {obj.title}",
    },

    "workshop_registered": {
        "title": "تسجيل جديد",
        "message": lambda obj, actor=None, extra=None:
            f"تسجيل جديد في ورشتك {obj.title} - العدد الحالي: {extra.get('registrations_count')}"
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

}