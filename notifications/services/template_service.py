TEMPLATES = {

    # ===============================
    # CONSULTATIONS
    # ===============================

    "consultation_requested": {
        "title": "طلب استشارة جديد",
        "message": lambda obj, actor=None, extra=None: f"لديك طلب استشارة من مشروع {obj.idea.title}",
    },

    "consultation_decided": {
        "title": "تم الرد على طلبك",
        "message": lambda obj, actor=None, extra=None:
            f"تم {'قبول' if extra=='accept' else 'رفض'} طلبك",
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
            f"قام {actor.full_name} بالتسجيل في ورشتك {obj.title}",
    },

    # ===============================
    # TEAM
    # ===============================

    "join_request_sent": {
        "title": "طلب انضمام",
        "message": lambda obj, actor=None, extra=None:
            f"لديك طلب انضمام لفريق مشروع {obj.title}",
    },

    "team_completed": {
    "title": "اكتمل الفريق ",
    "message": lambda idea: f"اكتمل فريق مشروع {idea.title}",
    },

    "team_member_removed": {
    "title": "تم مغادرة عضو",
    "message": lambda idea, member: f"غادر {member.full_name} فريق {idea.title}",
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