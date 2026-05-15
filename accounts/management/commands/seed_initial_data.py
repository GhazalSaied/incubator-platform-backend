from django.core.management.base import BaseCommand
from accounts.models import Role, Permission, RolePermission
from accounts.constants import SystemRoles


class Command(BaseCommand):
    help = "Seed initial roles, permissions, and mappings"

    def handle(self, *args, **kwargs):
        self.create_roles()
        self.create_permissions()
        self.assign_permissions()

        self.stdout.write(self.style.SUCCESS("✅ Initial data seeded successfully"))

    # ------------------ ROLES ------------------

    def create_roles(self):
        roles = [
            (SystemRoles.ADMIN, "Admin"),
            (SystemRoles.SECRETARY, "Secretary"),
            (SystemRoles.VOLUNTEER, "Volunteer"),
            (SystemRoles.EVALUATOR, "Evaluator"),
            (SystemRoles.IDEA_OWNER, "Idea Owner"),
            (SystemRoles.INCUBATOR, "Incubator"),   
        ]

        for code, name in roles:
            Role.objects.update_or_create(
                code=code,
                defaults={
                    "name_en": name,
                    "name_ar": name,
                    "is_system_role": True
                }
            )

    # ------------------ PERMISSIONS ------------------

    def create_permissions(self):
        permissions = [
            # IDEA

            ("idea.view", "View Idea", "IDEA"),

            # EVALUATION
            ("evaluation.submit", "Submit Evaluation", "EVALUATION"),
            ("evaluation.center.view", "View Evaluation Center", "EVALUATION"),
            ("evaluation.notes.view", "View Evaluation Notes", "EVALUATION"),
            
            # BOOTCAMP

            ("bootcamp.view", "View Bootcamp", "BOOTCAMP"),
            ("bootcamp.absence.submit", "Submit Bootcamp Absence", "BOOTCAMP"),

            # INCUBATION

            ("team.request_completion", "Request Team Completion", "INCUBATION"),
            ("incubation.team_candidates.view", "View Team Candidate Volunteers", "INCUBATION"),
            ("incubation.join_request.send", "Send Join Request", "INCUBATION"),
            ("incubation_reviews.notes.view","View Incubation Reviews Notes","INCUBATION"),


            # ADMIN
            ("user.manage", "Manage Users", "ADMIN"),
            ("season.manage", "Manage Season", "SEASON"),
            ("bootcamp.manage", "Manage Bootcamp", "BOOTCAMP"),
            ("candecidebootcamp.manage", "Manage Candidate Bootcamp", "BOOTCAMP"),
            ("evaluation.manage", "Manage Evaluations", "EVALUATION"),
            ("evaluation_decision.manage", "Manage Evaluation Decisions", "EVALUATION"),
            ("incubtion.manage", "Manage Incubation", "INCUBATION"),
            ("incubtion_decision.manage", "Manage Incubation Decisions", "INCUBATION"),
            ("exhibition.manage", "Manage Exhibition", "EXHIBITION"),
            ("can_decide_exhibition", "Can Decide Exhibition", "EXHIBITION"),
            ("volunteer.manage", "Manage Volunteers", "VOLUNTEER"),
            ("workshop.manage", "Manage Workshops", "WORKSHOP"),
            
            


            #VOLUNTEER

            ("workshop.manage", "Manage Workshop", "WORKSHOP"),
            ("volunteer.requests.manage", "Manage Volunteer Requests", "VOLUNTEER"),
            ("volunteer.assigned_consultations.view", "View Assigned Consultations", "VOLUNTEER"),
            ("volunteer.profile.manage","Manage volunteer profile","VOLUNTEER"),

            ("consultants.view", "View Consultants","VOLUNTEER"),
            

            #EXHIBITION

            ("exhibition.card.create", "Create Exhibition Card", "EXHIBITION"),
            ("exhibition.card.view", "View Exhibition Card", "EXHIBITION"),

             # MESSAGING

             ("message.send", "Send Messages", "MESSAGING"),


        ]

        for code, name, module in permissions:
            Permission.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "module": module,
                    "is_active": True
                }
            )

    # ------------------ ROLE PERMISSIONS ------------------

    def assign_permissions(self):
        role_permissions_map = {

            SystemRoles.ADMIN: [
                "idea.view",
                "evaluation.submit",
                "user.manage",
                "season.manage",
                "bootcamp.manage",
                "candecidebootcamp.manage",
                "evaluation.manage",
                "evaluation_decision.manage",
                "incubtion.manage",
                "incubtion_decision.manage",
                "exhibition.manage",
                "can_decide_exhibition",
                "volunteer.manage",
                "workshop.manage",
            ],

            SystemRoles.SECRETARY: [
                "idea.view",
                
            ],

            SystemRoles.EVALUATOR: [
                "evaluation.submit",
                "evaluation.center.view",
                "evaluation.notes.view",

            ],

            SystemRoles.VOLUNTEER: [
                "idea.view",
                "workshop.manage",
                "volunteer.requests.manage",
                "volunteer.profile.manage",
                 
                
                
            ],

            SystemRoles.IDEA_OWNER: [
                "idea.view",
                "consultants.view",
                "bootcamp.view",
                "bootcamp.absence.submit",
            ],
            SystemRoles.INCUBATOR: [
                "idea.view",
                "consultants.view",
                "team.request_completion",
                "incubation_reviews.notes.view",
            ]
        }

        for role_code, permissions in role_permissions_map.items():
            role = Role.objects.get(code=role_code)

            for perm_code in permissions:
                permission = Permission.objects.get(code=perm_code)

                RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission
                )