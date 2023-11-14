from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import AnswerForm, QuestionForm, QuizSetupForm, RegisterForm, PostFullForm, PostForm, ReplyForm, LoginForm, SubjectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import AttemptedAnswer, Grade, Post, File, Question, Attempt, Subject, User, Quiz

#this list contains all the users who have logged in
#during a session to display the number of visits the home page
#has gotten
users_viewed = []

###----------------------------------------------------------------------------------###
### Main View

@login_required(login_url="/login")
def home(request):

    files = File.objects.all()
    posts = Post.objects.all()

    if request.user not in users_viewed:
        users_viewed.append(request.user)
    page_visits = len(users_viewed)
    
    #delete form
    if request.method == 'POST':
            post_id = request.POST.get("post-id")
            post = Post.objects.filter(id=post_id).first()
            if post and post.author == request.user:
                post.delete()

    return render(request, 'main/home.html', {"posts":posts, "files":files, "page_visits": page_visits})



###----------------------------------------------------------------------------------###
### How posts are created / viewed


#Register screen
def sign_up(request):

    #registration form
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/login')

    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form":form})


#Login screen
def login(request):
    form = LoginForm(request.POST or None)
    #login form
    if request.method == 'POST':
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
    return render(request, 'registration/sign_up.html', {"form":form})


#Pulls up a detailed view of a post and allows the user to make a reply
@login_required(login_url="/login")
def reply(request, pk):
    post = Post.objects.get(id=pk)
    #reply form
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():

            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.save()

            return redirect('/reply/' + str(pk), {"post":post})
    else:
        form = ReplyForm()
            
    return render(request, 'main/post/reply.html', {"post":post, "form":form})


#Pulls up specific information about a post, including files attached
@login_required(login_url="/login")
def file_view(request, pk):

    post = Post.objects.get(id=pk)
    files = File.objects.all()

    return render(request, 'main/post/file_view.html', {"post":post, "files":files})


#Create post view
@login_required(login_url="/login")
def create_post(request):
    
    if request.method == "POST":
        form = PostFullForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        #create post form
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            for file in files:
                File.objects.create(file=file, post=post)
                
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, 'main/post/create_post.html', {"form":form})



###----------------------------------------------------------------------------------###
### How quizzes are created


#Screen that prompts the user to create a quiz
@login_required(login_url="/login")
def quiz_setup(request, pk):
    subject = Subject.objects.get(id=pk)
    #quiz creation form
    if request.method == 'POST':
        form = QuizSetupForm(request.POST)
        if form.is_valid():
            setup = form.save(commit=False)
            setup.teacher = request.user
            setup.subject = subject
            setup.save()
            return redirect("/question_setup/" + str(setup.id), {"subject":subject })
    else:
        form = QuizSetupForm()
    return render(request, 'main/quiz/quiz_setup.html', {"form":form, "subject":subject })


#Screen that prompts the user to add questions to their quiz
@login_required(login_url="/login")
def question_setup(request, pk):
    quiz = Quiz.objects.get(id=pk)
    questions = quiz.questions.all()
    #question creation form
    if request.method == 'POST' and 'submitform' in request.POST:
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('/answer_setup/' + str(question.id), {"form":form, "quiz":quiz, "questions":questions})
    elif request.method == 'POST' and 'question-id' in request.POST:
        question_id = request.POST.get("question-id")
        Question.objects.filter(id=question_id).delete()
        form = QuestionForm()
    else:
        form = QuestionForm()

    return render(request, 'main/quiz/question_setup.html', {"form":form, "quiz":quiz, "questions":questions})


#Screen that prompts the user to add answers to their question
@login_required(login_url="/login")
def answer_setup(request, pk):
    question = Question.objects.get(id=pk)
    answers = question.answers.all()
    #answer creation form
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('/answer_setup/' + str(pk), {"answers":answers, "form":form, "question":question})
    else:
        form = AnswerForm()
    
    return render(request, 'main/quiz/answer_setup.html', {"answers":answers, "form":form, "question":question})


#Pulls up a list of all quizzes that have been posted
@login_required(login_url="/login")
def view_quizzes(request, pk):
    subject = Subject.objects.get(id=pk)
    quizzes = Quiz.objects.filter(subject=subject)

    return render(request, 'main/quiz/view_quizzes.html', {"quizzes": quizzes, "subject":subject })


#Similar to view_quizzes, but directs exclusively students to a screen that
#allows them to take a quiz
@login_required(login_url="/login")
def content(request):
    quizzes = Quiz.objects.all()
    quizzes_with_attempts = []

    for quiz in quizzes:
        attemptsRem = quiz.max_attempts - Attempt.objects.filter(student=request.user, quiz=quiz).count()

        quizzes_with_attempts.append({
            "quiz":quiz,
            "attemptsRem":attemptsRem
        })
    
    
    return render(request, 'main/quiz/content.html', {"quizzes":quizzes, "quizzes_with_attempts":quizzes_with_attempts})


#This view pulls up a quiz and calculates the student's score
#based on what they submit through a form
@login_required(login_url="/login")
def take_quiz_detail(request, pk):

    quiz = Quiz.objects.get(id=pk)
    student = request.user

    #number of current attempts taken for a quiz
    current_attempts = Attempt.objects.filter(student=student, quiz=quiz).count()

    if (current_attempts >= quiz.max_attempts):
        return redirect('/content/')

    correct = 0
    incorrect = 0
    total = 0
    #take quiz form
    if request.method == 'POST':
        new_attempt = Attempt(student=request.user, quiz=quiz, number=current_attempts+1)
        new_attempt.save()

        questions = quiz.questions.all()
        for question in questions:
            for answer in question.answers.all():
                
                if (str(answer.pk) in request.POST):
                    AttemptedAnswer.objects.create(attempt=new_attempt, answer=answer)

                if request.POST.get(str(answer.id)) == 'True':
                    correct += 1
                elif request.POST.get(str(answer.id)) == 'False':
                    incorrect += 1

        total = correct + incorrect
        if total != 0:
            score_value = (correct / total)*100
            new_attempt.score = score_value
            new_attempt.save()
            updateGrade(new_attempt, student)
            return redirect('/ind_results/')

    return render(request, 'main/quiz/take_quiz_detail.html', {"quiz":quiz})


def updateGrade(new_attempt, student):
    grade = Grade.objects.get(student=student, subject=new_attempt.quiz.subject)

    if (grade):
        return
    else:
        return

###----------------------------------------------------------------------------------###
### Results posted from quizzes


#Displays individual student's results
@login_required(login_url="/login")
def ind_results(request):

    quizzes = Quiz.objects.all()
    attempts = Attempt.objects.all()
    attempted_answers = AttemptedAnswer.objects.all()

    user_attempts = []
    quizzes_taken = []
    none_taken = False

    search = request.GET.get('search')

    for attempt in attempts:
        #allows the template to only display attempts made by the user that's logged in
        if attempt.student == request.user:
            user_attempts.append(attempt)
        #same thing for quizzes
        if attempt.quiz not in quizzes_taken and attempt.student == request.user:
            quizzes_taken.append(attempt.quiz)

    if (search):
        quizzes_taken = Quiz.objects.filter(title__icontains=search)

    if len(quizzes_taken) == 0:
        none_taken = True

    return render(request, 'main/results/ind_results.html', {"user_attempts":user_attempts, "quizzes_taken":quizzes_taken, "none_taken":none_taken, "attempted_answers":attempted_answers})


#Displays all students' results
@login_required(login_url="/login")
def group_results(request):
    quizzes = Quiz.objects.all()
    attempts = Attempt.objects.all()
    students = []
    aa = []

    for quiz in quizzes:
        for attempt in quiz.attempts.all():
                if attempt.student not in students:
                    students.append(attempt.student)
                    numOfAttemptsMade = quiz.attempts.filter(student=attempt.student).count()
                    attemptsMade = quiz.attempts.filter(student=attempt.student)

                    aa.append({
                        "quiz":quiz,
                        "student":attempt.student,
                        "numOfAttemptsMade":numOfAttemptsMade,
                        "attemptsMade":attemptsMade
                    })
        students = []

    return render(request, 'main/results/group_results.html', {"quizzes":quizzes, "attempts":attempts, "aa":aa})

@login_required(login_url="/login")
def group_results_detail(request, quiz_id, student_id):
    attempts = Attempt.objects.all()
    quiz = Quiz.objects.get(pk=quiz_id)
    attempted_answers = AttemptedAnswer.objects.all()
    user_attempts = []

    for attempt in attempts:
        if attempt.student.id == student_id and attempt.quiz == quiz:
            user_attempts.append(attempt)

    return render(request, 'main/results/group_results_detail.html', {"user_attempts":user_attempts, "quiz":quiz, "attempted_answers":attempted_answers})

###----------------------------------------------------------------------------------###
### Scores posted from results

def group_scores(request):
    quizzes = Quiz.objects.all()
    attempts = Attempt.objects.all()
    students = []
    dic = []

    ##generates a list of available students
    for attempt in attempts:
        if attempt.student not in students:
            students.append(attempt.student)

    for quiz in quizzes:
        for student in students:
            highest_score = 0
            for attempt in quiz.attempts.all():
                if attempt.student == student and attempt.quiz == quiz:
                    if attempt.score > highest_score:
                        highest_score = attempt.score

            dic.append({
                "quiz":quiz,
                "student":student,
                "highest_score":highest_score,
            })


    return render(request, 'main/scores/group_scores.html', {"quizzes":quizzes, "students":students, "dic":dic})

###----------------------------------------------------------------------------------###
### Subjects

def subjects(request):

    subjects = Subject.objects.all()

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = request.user
            subject.save()
            return redirect('/subjects/', {"subjects":subjects, "form":form })
    else:
        form = SubjectForm()

    return render(request, 'main/subject/subjects.html', {"subjects":subjects, "form":form })


        







