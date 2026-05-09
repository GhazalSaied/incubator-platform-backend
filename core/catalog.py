EVENTS = {

    # ===============================
    # VOLUNTEER LIFECYCLE
    # ===============================

    "volunteer_approved": {
        "target": "VOLUNTEER",
        "description": "تم قبول المستخدم كمتطوع",
        "payload": ["user"],
        "action_url": "/profile/edit"
    },

    "role_activated": {
        "target": "USER",
        "description": "تم تفعيل دور إضافي (متطوع/مدرب)",
        "payload": ["user", "role"],
        "action_url": "/profile"
    },

    # ===============================
    # WORKSHOPS
    # ===============================

    "workshop_submitted": {
        "target": "ADMIN",
        "payload": ["workshop", "user"]
    },

    "workshop_approved": {
        "target": "VOLUNTEER",
        "payload": ["workshop"],
        "action_url": "/my-workshops/{workshop}"
    },

    "workshop_rejected": {
        "target": "VOLUNTEER",
        "payload": ["workshop", "rejection_reason"],
        "action_url": "/my-workshops/{id}"
    },

    "workshop_published": {
        "target": "ALL_USERS",
        "payload": ["workshop"],
        "action_url": "/workshops/{id}"
    },

    "workshop_registered": {
        "target": "VOLUNTEER",
        "payload": ["workshop", "user"],
        "action_url": "/workshop-details/{workshop}/"
    },

    # ===============================
    # CONSULTATIONS
    # ===============================

    "consultation_requested": {
        "target": "VOLUNTEER",
        "payload": ["consultation"],
        "action_url": "/consultations/{id}"
    },

    "consultation_reminder": {
        "target": "VOLUNTEER",
        "payload": ["consultation"],
        "action_url": "/consultations/{consultation}"
    },

    "consultation_accepted": {
        "target": "IDEA_OWNER",
        "payload": ["consultation", "action"],
        "action_url": "/conversations/{conversation}"
    },

    "consultation_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["consultation"],
        "action_url": "/api/volunteers/consultants/"
    },

    # ===============================
    # TEAM JOIN REQUESTS
    # ===============================

    "join_request_sent": {
        "target": "VOLUNTEER",
        "payload": ["join_request"],
        "action_url": "/join-requests/{join_request}"
    },

    "volunteer_joined_team": {
        "target": "IDEA_OWNER",
        "payload": ["idea", "volunteer"],
        "action_url": "/team-dashboard"
    },


    "join_request_accepted": {
    "target": "IDEA_OWNER",
    "payload": ["join_request"],
    "action_url": "/team-dashboard"
    },

    "join_request_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["join_request"],
        "action_url": "/suggested-volunteers"
    },

    # ===============================
    # EVALUATION (VOLUNTEER AS EVALUATOR)
    # ===============================

    "evaluation_invitation_sent": {
        "target": "VOLUNTEER",
        "payload": ["invitation"],
        "action_url": "/invitations"
    },

    "evaluation_invitation_accepted": {
        "target": "ADMIN",
        "payload": ["invitation", "actor"],
        "action_url": "/admin/evaluation/invitations"
    },

    "evaluation_invitation_rejected": {
        "target": "ADMIN",
        "payload": ["invitation", "actor"],
        "action_url": "/admin/evaluation/invitations"
    },

    "evaluation_joined_committee": {
        "target": "VOLUNTEER",
        "payload": ["invitation"],
        "action_url": "/evaluation-dashboard"
    },

    "evaluation_session_reminder": {
        "target": "VOLUNTEER",
        "payload": ["assignment"],
        "action_url": "/evaluation-dashboard"
    },

    # ===============================
    # IDEA EVENTS
    # ===============================

    "idea_submitted": {
        "target": "USER",
        "payload": ["idea"],
        "action_url": "/ideas/{id}"
    },

    "idea_withdrawn": {
        "target": "USER",
        "payload": ["idea"],
        "action_url": "/my-ideas"
    },

    "idea_accepted": {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": "/incubation"
    },

    "idea_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": "/idea-feedback"
    },

    "idea_status_changed": {},

    # ===============================
    # EVALUATION RESULTS
    # ===============================

    "evaluation_report_published": {
        "target": "IDEA_OWNER",
        "payload": ["idea", "review"],
        "action_url": "/incubation"
    },

    "evaluation_submitted" : {
        "target": "ADMIN",
        "payload": ["evaluation", "idea"],
        "action_url": ""
    },



    # ===============================
    # BOOTCAMP
    # ===============================

    "bootcamp_started": {
        "target": "IDEA_OWNER",
        "payload": ["season"],
        "action_url": "/bootcamp"
    },

    "bootcamp_session_reminder": {
        "target": "IDEA_OWNER",
        "payload": ["session"],
        "action_url": "/bootcamp"
    },

    # ===============================
    # ABSENCE
    # ===============================

    "absence_requested": {
        "target": "ADMIN",
        "payload": ["absence"]
    },

    "absence_approved": {
        "target": "IDEA_OWNER",
        "payload": ["absence"],
        "action_url": "/bootcamp"
    },

    "absence_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["absence"],
        "action_url": "/bootcamp"
    },

    # ===============================
    # EXHIBITION
    # ===============================

    "exhibition_preparation_reminder": {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": "/exhibition"
    },

    "exhibition_approved": {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": "/exhibition"
    },

    # ===============================
    # TEAM BUILDING
    # ===============================

    "team_request_created": {
        "target": "ADMIN",
        "payload": ["team_request"]
    },

    "volunteers_suggested": {
        "target": "IDEA_OWNER",
        "payload": ["idea", "volunteers"],
        "action_url": "/team-dashboard"
    },

    # ===============================
    # CONSULTANT FROM ADMIN
    # ===============================

    "consultant_suggested": {
        "target": "IDEA_OWNER",
        "payload": ["consultant"],
        "action_url": "/consultants"
    },

    # ===============================
    # INVESTOR CONTACT
    # ===============================

    "investor_contact_request": {
        "target": "IDEA_OWNER",
        "payload": ["conversation"],
        "action_url": "/chat/{id}"
    },

    # ===============================
    # SYSTEM
    # ===============================

    "message_sent": {
        "target": "USER",
        "payload": ["message", "conversation"],
        "action_url": "/chat/{id}"
    },

    "account_suspended": {
        "target": "USER",
        "payload": ["user"],
        "action_url": "/contact-admin"
    },

    "admin_reply_sent": {
        "target": "USER",
        "payload": ["message"],
        "action_url": "/support"
    },

    "exhibition_invitation": {
        "target": "ALL_USERS",
        "payload": ["event"],
        "action_url": "/events"
    },


# ===============================
#admin_season_events
# ===============================

    "season_published": {
        "target" : "USER",
        "payload" : ["season"],
        "action_url" : "/form"
    },

    "submission_closed": {
        "target" : "USER",
        "payload" : ["season"],
        "action_url" : "/season-status"
    },

    
    "idea_status_changed": {
        "target" : "USER",
        "payload" : ["idea","old_status","new_status"],
        "action_url" : "/ideas/{id} "
    }, 
    
    
    "absence_decision_made": {
        "target": "IDEA_OWNER",
        "payload": ["absence", "decision"],
        "action_url": None
    },
    

    "bootcamp_session_created": {
        "target": "USER", 
        "payload": ["session"], 
        "action_url": None
        },
    
    
    "bootcamp_decision_made" : {
        "target": "IDEA_OWNER",
        "payload": ["idea", "decision"],
        "action_url": "/idea/{id}"
    },

    
    "bootcamp_sessions_ended": {
        "target": "IDEA_OWNER", 
        "payload": ["season"], 
        "action_url": None
    },
    
    "evaluation_meeting_scheduled": {
        "target": "EVALUATOR",
        "payload": ["idea", "meeting_datetime"],
        "action_url": ""
    },

    "idea_accepted" : {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": ""
    },
    
    
    "idea_rejected" : {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": ""},
    "season_phase_changed" : {
        "target": "USER",
        "payload": ["season", "new_phase"],
        "action_url": ""  
    },
    
    "incubation_meeting_scheduled": {
        "target": "incubation",
        "payload": ["review", "idea", "assignments"],
        "action_url": ""
}, 
    "idea_EXhibition_graduated" : {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": " "
    },
    
    "idea_graduated_negative" : {
        "target": "IDEA_OWNER",
        "payload": ["idea"],
        "action_url": " "},
    "exhibition_scheduled" : {
        "target": "USER",
        "payload": ["season", "exhibition_datetime"],
        "action_url": " "   
    },


    "exhibition_form_published" : {
        "target": "IDEA_OWNER",
        "payload": ["form_id", "season_id"],
        "action_url": " "
    },
    
    
    "exhibition_submission_decided": {
    "target": "IDEA_OWNER",
    "payload": [
        "submission",
        "decision",
        "message"
    ],
    "action_url": ""
},
    "volunteer_approved": {
    "target": "USER",
    "description": "تم قبول طلب التطوع الخاص بك",
    "payload": ["user"],
    "action_url": "api/volunteers/me/update/"
},
    "volunteer_rejected": {
    "target": "USER",
    "description": "تم رفض طلب التطوع",
    "payload": ["user"],
    "action_url": " "
},
    "evaluation_invitation_sent": {
    "target": "VOLUNTEER",
    "payload": ["invitation"],
    "action_url": ""
},
    
    "evaluator_role_removed": {
    "target": "USER",
    "payload": ["user"],
    "action_url": " "
},
    
    "volunteers_suggested": {
    "target": "IDEA_OWNER",
    "payload": ["idea", "volunteers"],
    "action_url": ""
}

}
        
          
        
    

    
    
    
