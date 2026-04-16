TEMPLATES = {

    # ===============================
    # CONSULTATIONS
    # ===============================

    "consultation_requested": {
        "title": "طلب استشارة جديد",
        "message": lambda c: f"لديك طلب استشارة من مشروع {c.idea.title}",
    },

    "consultation_accepted": {
        "title": "تم قبول طلبك",
        "message": lambda c: f"تم قبول طلبك من {c.volunteer.user.full_name}",
    },

    "consultation_rejected": {
        "title": "تم رفض طلبك",
        "message": lambda c: f"اعتذر {c.volunteer.user.full_name} عن قبول طلبك",
    },

    # ===============================
    # WORKSHOPS
    # ===============================

    "workshop_submitted": {
        "title": "تم إرسال الورشة",
        "message": lambda w: f"تم إرسال ورشتك {w.title} للمراجعة",
    },

    "workshop_registered": {
        "title": "تسجيل جديد",
        "message": lambda w, u: f"قام {u.full_name} بالتسجيل في ورشتك {w.title}",
    },

    # ===============================
    # TEAM
    # ===============================

    "join_request_sent": {
        "title": "طلب انضمام",
        "message": lambda c: f"لديك طلب انضمام لفريق مشروع {c.idea.title}",
    },

    # ===============================
    # EVALUATION
    # ===============================

    "evaluation_invitation_sent": {
        "title": "دعوة لجنة تقييم",
        "message": lambda i: f"تم دعوتك للانضمام إلى لجنة تقييم ({i.season.name})",
    },

    "evaluation_invitation_accepted": {
        "title": "تم قبولك",
        "message": lambda i: "أصبحت الآن عضو في لجنة التقييم",
    },

    # ===============================
    # SYSTEM
    # ===============================

    "message_sent": {
        "title": "رسالة جديدة",
        "message": lambda sender: f"لديك رسالة من {sender.full_name}",
    },

    "account_suspended": {
        "title": "تم تجميد الحساب",
        "message": lambda u: "تم تجميد حسابك مؤقتاً",
    },

}