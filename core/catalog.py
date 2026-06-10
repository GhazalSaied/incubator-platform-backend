EVENTS = {



    # ===============================
    # WORKSHOPS
    # ===============================

    "workshop_submitted": {
        "target": "ADMIN",
        "payload": ["workshop", "actor"],
        "action_url": "/api/admin/workshops/"
    },


    "workshop_registered": {
        "target": "VOLUNTEER",
        "payload": ["workshop", "actor"],
        "action_url": "/api/volunteers/workshop-details/{workshop.id}/"
    },

    # ===============================
    # CONSULTATIONS
    # ===============================

    "consultation_requested": {
        "target": "VOLUNTEER",
        "payload": ["consultation", "actor"],
        "action_url": "/volunteers/consultations/"
    },

    "consultation_accepted": {
        "target": "IDEA_OWNER",
        "payload": ["consultation", "actor"],
        "action_url": None
    },

    "consultation_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["consultation", "actor"],
        "action_url": "/api/volunteers/consultants/"
    },

    # ===============================
    # TEAM JOIN REQUESTS
    # ===============================

    "join_request_sent": {
        "target": "VOLUNTEER",
        "payload": ["join_request", "actor"],
        "action_url": "/api/volunteers/join-requests/"
    },

    "volunteer_joined_team": {
        "target": "IDEA_OWNER",
        "payload": ["idea", "volunteer"],
        "action_url": "/api/ideas/team-dashboard/"
    },


    "join_request_accepted": {
    "target": "IDEA_OWNER",
    "payload": ["join_request", "actor"],
    "action_url": "/api/ideas/team-dashboard/"
    },

    "join_request_rejected": {
        "target": "IDEA_OWNER",
        "payload": ["join_request", "actor"],
        "action_url": "/api/ideas/suggested-volunteers/"
    },
    "team_member_added": {
        "target": "INCUBATOR",
        "payload": ["idea", "volunteer"],
        "action_url": "/api/ideas/team-dashboard/"
    },

    # ===============================
    # EVALUATION (VOLUNTEER AS EVALUATOR)
    # ===============================

    "evaluation_invitation_accepted": {
        "target": "ADMIN",
        "payload": ["invitation", "actor"],
        "action_url": None
    },

    "evaluation_invitation_rejected": {
        "target": "ADMIN",
        "payload": ["invitation", "actor"],
        "action_url": None
    },

    "evaluation_joined_committee": {
        "target": "VOLUNTEER",
        "payload": ["invitation"],
        "action_url": None
    },

    
    # ===============================
    # IDEA EVENTS
    # ===============================

    "idea_submitted": {
        "target": "ADMIN",
        "payload": ["idea"],
        "action_url": "/api/admin/ideas/{idea.id}/details/"
    },

    "idea_withdrawn": {
        "target": "USER",
        "payload": ["idea"],
        "action_url": "/my-ideas"
    },


    "idea_status_changed": {},

    # ===============================
    # EVALUATION RESULTS
    # ===============================

    "evaluation_submitted" : {
        "target": "ADMIN",
        "payload": ["evaluation", "idea"],
        "action_url": ""
    },



    # ===============================
    # BOOTCAMP
    # ===============================

    # ===============================
    # ABSENCE
    # ===============================

    "bootcamp_absence_request_submitted": {
    "target": "ADMIN",
    "payload": ["absence_request"],
    "action_url":"/api/admin/bootcamp/absence/"
    },

    # ===============================
    # EXHIBITION
    # ===============================
    "exhibition_submission_created": {
        "target": "ADMIN",
        "payload": ["submission", "actor"],
        "action_url": "/api/admin/exhibition/submissions/"
        },

    # ===============================
    # TEAM BUILDING
    # ===============================

    "team_request_created": { 
        "target": "ADMIN",
        "payload": ["team_request", "actor"],
        "action_url": "/api/admin/volunteers/team-request-owners/" },



    # ===============================
    # CONSULTANT FROM ADMIN
    # ===============================

    
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

   

   
#-------------------------------------------------------------------------------
#-------------------------------ADMIN-------------------------------------------
#-------------------------------------------------------------------------------


# ===============================
#admin_season_events
# ===============================

    "season_published": {
        "target": "USER",
        "payload": ["season"],
        "action_url": "/api/ideas/form/"
    },
# ===============================
#admin_bootcamp_events
# ===============================
    "bootcamp_started": {
        "target": "IDEA_OWNER",
        "payload": ["season"],
        "action_url": None
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
    
    
    "bootcamp_decision_made": {
        "target": "IDEA_OWNER",
        "payload": ["idea", "decision"],
        "action_url": None
    },

    
    "bootcamp_sessions_ended": {
        "target": "IDEA_OWNER", 
        "payload": ["season"], 
        "action_url": None
    },
# ===============================
#admin_evaluations_events
# ===============================    
    
    "evaluation_meeting_scheduled": {
        "target": "EVALUATOR",
        "payload": [
            "idea",
            "assignments",
            "meeting_datetime",
            "actor"
        ],
        "action_url": None
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
# ===============================
#admin_incubations_events
# ===============================        

    "incubation_meeting_scheduled": {
        "target": "INCUBATOR",
        "payload": ["review", "idea", "assignments"],
        "action_url": None
    }, 
    "idea_exhibition_graduated": {
        "target": "INCUBATOR",
        "payload": ["idea"],
        "action_url": None
    },

    "idea_graduated_negative": {
        "target": "INCUBATOR",
        "payload": ["idea"],
        "action_url": None
    },
# ===============================
#admin_exhibition_events
# ===============================       

    "exhibition_scheduled" : {
        "target": "USER",
        "payload": ["season", "exhibition_datetime"],
        "action_url": None  
    },


    "exhibition_form_published" : {
        "target": "INCUBATOR",
        "payload": ["form_id", "season_id"],
        "action_url": "api/ideas/exhibition/dashboard/"
    },
    
    
    "exhibition_submission_decided": {
        "target": "INCUBATOR",
        "payload": [
            "submission",
            "decision",
            "message"
        ],
        "action_url": None
    },
# ===============================
#admin_volunteer_events
# =============================== 
    "volunteer_approved": {
        "target": "VOLUNTEER",
        "payload": ["user"],
        "action_url": "/api/volunteers/me/"
    },
    "volunteer_rejected": {
        "target": "VOLUNTEER",
        "payload": ["user"],
        "action_url": None
    },
    "evaluation_invitation_sent": {
        "target": "VOLUNTEER",
        "payload": ["invitation"],
        "action_url": ""
    },
    
    "volunteers_suggested": {
        "target": "INCUBATOR",
        "payload": ["idea", "volunteers"],
        "action_url": "api/ideas/suggested-volunteers/"
    },
    
# ===============================
#admin_workshops_events
# =============================== 
    
    "workshop_approved": {
        "target": "VOLUNTEER",
        "payload": ["workshop"],
        "action_url": None
    },
    
    "new_workshop_published": {
        "target": "USER",
        "payload": ["workshop"],
        "action_url": "/api/volunteers/public-workshops/"
    },
    

    "workshop_rejected": {
        "target": "VOLUNTEER",
        "payload": [
            "workshop",
            "rejection_reason"
        ],
        "action_url": "api/volunteers/workshop-details/{workshop.id}"
    },
    
# ==============================
# ADMIN BROADCAST
# ==============================   
    "admin_manual_notification": {
        "target": "USER",
        "action_url": "/notifications"
    },

    "ADMIN_BROADCAST_NOTIFICATION": {
        "target": "SYSTEM",
        "action_url": "/notifications"
    },
}
        
          
        
    

    
    
    
