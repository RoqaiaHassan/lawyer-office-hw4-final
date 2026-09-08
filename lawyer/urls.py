from django.urls import path
from . import views

# لتحديد اسم التطبيق عند استخدام {% url 'lawyer:...' %}
app_name = "lawyer"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("<int:lawyer_id>/", views.detail, name="detail"),

    path("lawyers/", views.lawyer_list, name="lawyer_list"),
    path("lawyers/add/", views.lawyer_add, name="lawyer_add"),
    path("lawyers/edit/<int:pk>/", views.lawyer_edit, name="lawyer_edit"),
    path("lawyers/delete/<int:pk>/", views.lawyer_delete, name="lawyer_delete"),
    path("lawyers/office-card/<int:lawyer_id>/", views.office_card_edit, name="office_card_edit"),

    path("cases/", views.case_list, name="case_list"),
    path("cases/new/", views.case_create, name="case_create"),
    path("cases/assign/<int:pk>/", views.case_assign, name="case_assign"),
    path("contacts/", views.contact_messages, name="contact_messages"),
    path("contacts/reply/<int:pk>/", views.reply_message, name="reply_message"),

    # مسارات التكليف الدراسي (QuerySet & Forms & Many-to-Many CRUD)
    path("homework/queryset/", views.homework_queryset_demo, name="queryset_homework"),
    path("homework/forms/", views.homework_forms_demo, name="forms_demo"),
    path("specializations/", views.specialization_list, name="specialization_list"),
    path("specializations/delete/<int:pk>/", views.specialization_delete, name="specialization_delete"),
]