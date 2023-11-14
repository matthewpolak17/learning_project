from django.urls import path
from . import views

urlpatterns = [
    
    ###general/posts
    path('', views.home, name="home"),
    path('sign_up/', views.sign_up, name="sign_up"),
    path('create_post', views.create_post, name="create_post"),
    path('reply/<int:pk>', views.reply, name="reply"),
    path('file_view/<int:pk>', views.file_view, name="file_view"),

<<<<<<< Updated upstream
    ###subject creation
    path('subject_setup/', views.subject_setup, name="subject_setup"),
    path('question_setup/<int:pk>', views.question_setup, name='question_setup'),
    path('answer_setup/<int:pk>', views.answer_setup, name='answer_setup'),

    ###subject viewing
    path('view_subjects/', views.view_subjects, name="view_subjects"),
=======
    ###quiz creation
    path('quiz_setup/<int:pk>', views.quiz_setup, name="quiz_setup"),
    path('question_setup/<int:pk>', views.question_setup, name='question_setup'),
    path('answer_setup/<int:pk>', views.answer_setup, name='answer_setup'),

    ###quiz viewing
    path('view_quizzes/<int:pk>', views.view_quizzes, name="view_quizzes"),
>>>>>>> Stashed changes
    path('content/', views.content, name="content"),

    ###subject taking
    path('take_subject_detail/<int:pk>', views.take_subject_detail, name="take_subject_detail"),

    ###result viewing
    path('ind_results/', views.ind_results, name="ind_results"),
    path('group_results/', views.group_results, name="group_results"),
    path('group_results_detail/<int:subject_id>/<int:student_id>', views.group_results_detail, name="group_results_detail"),

]