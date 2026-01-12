# # users/signals.py

# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.conf import settings
# from djoser.signals import user_registered

# @receiver(user_registered)
# def send_welcome_email(request, user, **kwargs):
#     subject = "Bienvenue sur DirectAlu ! 🎉"
#     message = f"""
#     Bonjour {user.first_name or user.username},

#     Votre compte DirectAlu a bien été créé avec succès !

#     Email : {user.email}
#     Rôle : {user.get_role_display()}

#     Vous pouvez dès maintenant vous connecter et commencer à utiliser la plateforme.

#     À très vite,
#     L'équipe DirectAlu
#     """

#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [user.email]

#     send_mail(
#         subject=subject,
#         message=message,
#         from_email=from_email,
#         recipient_list=recipient_list,
#         fail_silently=False,
#     )