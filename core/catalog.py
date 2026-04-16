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
    "action_url": "/my-workshops/{id}/registrations"
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
    "action_url": "/consultations/{id}"
},

"consultation_decided": {
    "target": "IDEA_OWNER",
    "payload": ["consultation", "action"],
    "action_url": "/consultations/{id}"
},

# ===============================
# TEAM JOIN REQUESTS
# ===============================

"join_request_sent": {
    "target": "VOLUNTEER",
    "payload": ["consultation"],
    "action_url": "/consultations/{id}"
},

"volunteer_joined_team": {
    "target": "IDEA_OWNER",
    "payload": ["idea", "volunteer"],
    "action_url": "/team-dashboard"
},

"join_request_rejected": {
    "target": "IDEA_OWNER",
    "payload": ["consultation"],
    "action_url": "/consultations"
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
    "target": "VOLUNTEER",
    "payload": ["invitation"],
    "action_url": "/evaluation-dashboard"
},

"evaluation_invitation_rejected": {
    "target": "ADMIN",
    "payload": ["invitation"]
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

# ===============================
# EVALUATION RESULTS
# ===============================

"evaluation_report_published": {
    "target": "IDEA_OWNER",
    "payload": ["idea", "review"],
    "action_url": "/incubation"
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

}