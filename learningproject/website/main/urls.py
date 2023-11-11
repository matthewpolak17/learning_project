from django.urls import path
from . import views

urlpatterns = [
    
    ###general/posts
    path('', views.home, name="home"),
    path('sign_up/', views.sign_up, name="sign_up"),
    path('create_post', views.create_post, name="create_post"),
    path('reply/<int:pk>', views.reply, name="reply"),
    path('file_view/<int:pk>', views.file_view, name="file_view"),

    ###quiz creation
    path('quiz_setup/', views.quiz_setup, name="quiz_setup"),
    path('question_setup/<int:pk>', views.question_setup, name='question_setup'),
    path('answer_setup/<int:pk>', views.answer_setup, name='answer_setup'),

    ###quiz viewing
    path('view_quizzes/', views.view_quizzes, name="view_quizzes"),
    path('content/', views.content, name="content"),

    ###quiz taking
    path('take_quiz_detail/<int:pk>', views.take_quiz_detail, name="take_quiz_detail"),

    ###result viewing
    path('ind_results/', views.ind_results, name="ind_results"),
    path('group_results/', views.group_results, name="group_results"),
    path('group_results_detail/<int:quiz_id>/<int:student_id>', views.group_results_detail, name="group_results_detail"),

    ###score viewing
    path('group_scores/', views.group_scores, name="group_scores"),

    ###subjects
    path('subjects/', views.subjects, name="subjects"),

]