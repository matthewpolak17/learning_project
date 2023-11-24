from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import AnswerForm, QuestionForm, QuizSetupForm, RegisterForm, PostFullForm, PostForm, ReplyForm, LoginForm, SemesterForm, SubjectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from decimal import Decimal
from .models import AttemptedAnswer, Grade, Post, File, Question, Attempt, Semester, Subject, User, Quiz
import json
from django.core.serializers import serialize

#this list contains all the users who have logged in
#during a session to display the number of visits the home page
#has gotten
users_viewed = []

###----------------------------------------------------------------------------------###
### Main View

@login_required(login_url="/login")
def home(request):

    cursem = Semester.objects.get(is_current=True)
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

    return render(request, 'main/home.html', {"posts":posts, "files":files, "page_visits": page_visits, "cursem":cursem})



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
    cursem = Semester.objects.get(is_current=True)
    subjects = Subject.objects.filter(semester=cursem)
    quizzes = Quiz.objects.all()
    quizzes_with_attempts = []

    for quiz in quizzes:
        attemptsRem = quiz.max_attempts - Attempt.objects.filter(student=request.user, quiz=quiz).count()

        quizzes_with_attempts.append({
            "quiz":quiz,
            "attemptsRem":attemptsRem
        })
    
    
    return render(request, 'main/quiz/content.html', {"quizzes":quizzes, "quizzes_with_attempts":quizzes_with_attempts, "subjects":subjects, "cursem":cursem})


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
            new_attempt.score = round(score_value, 2)
            new_attempt.save()
            updateGrade(new_attempt, student)
            return redirect('/ind_results/')

    return render(request, 'main/quiz/take_quiz_detail.html', {"quiz":quiz})


def updateGrade(new_attempt, student):
    
    try:
        grade = Grade.objects.get(student=new_attempt.student, subject=new_attempt.quiz.subject)
    except Grade.DoesNotExist:
        grade = None

    quizzes = new_attempt.quiz.subject.quizzes.all()

    if (grade):#if they need to update their grade

        actual = 0
        ideal = 0
        for quiz in quizzes:
            highest = 0

            for attempt in quiz.attempts.all():
                if attempt.score > highest and attempt.student == student:
                    highest = attempt.score

            if quiz.attempts.filter(student=student).count() > 0:
                ideal += quiz.weight

            actual = actual + ((Decimal(highest) / 100) * quiz.weight)
            
            if ideal != 0:
                grade.score = round(actual / ideal * 100, 2)
            else:
                grade.score = 0

        grade.save()
        

    else:#if they haven't been graded for a subject yet

        #set the grade equal to the score of their first quiz
        grade = Grade(student=new_attempt.student, subject=new_attempt.quiz.subject, score=new_attempt.score)
        grade.save()
        print(grade.score)

###----------------------------------------------------------------------------------###
### Results posted from quizzes


#Displays individual student's results
@login_required(login_url="/login")
def ind_results(request):
    cursem = Semester.objects.get(is_current=True)
    search = request.GET.get('search')
    subjects = Subject.objects.filter(semester=cursem)
    student = request.user
    attempts = Attempt.objects.filter(student=student)
    aa = []

    if search:
        subjects = Subject.objects.filter(title__icontains=search, semester=cursem)

    for subject in subjects:
        quizzes = Quiz.objects.filter(subject=subject)
        for quiz in quizzes:
            numOfAttemptsMade = quiz.attempts.filter(student=student).count()
            aa.append({
                "subject":subject,
                "quiz":quiz,
                "numOfAttemptsMade":numOfAttemptsMade
            })

    return render(request, 'main/results/ind_results.html', {"cursem":cursem, "aa":aa, "subjects":subjects, "student":student})

def ind_results_detail(request, quiz_id):
    cursem = Semester.objects.get(is_current=True)
    quiz = Quiz.objects.get(id=quiz_id)
    attempts = Attempt.objects.filter(quiz=quiz)
    attempted_answers = AttemptedAnswer.objects.all()

    return render(request, 'main/results/ind_results_detail.html/', {"cursem":cursem, "quiz":quiz, "attempts":attempts, "attempted_answers":attempted_answers})


#Displays all students' results
@login_required(login_url="/login")
def group_results(request):
    cursem = Semester.objects.get(is_current=True)
    subjects = Subject.objects.filter(semester=cursem)
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

    return render(request, 'main/results/group_results.html', {"quizzes":quizzes, "attempts":attempts, "aa":aa, "cursem":cursem, "subjects":subjects})

@login_required(login_url="/login")
def group_results_detail(request, quiz_id, student_id):
    attempts = Attempt.objects.all()
    quiz = Quiz.objects.get(pk=quiz_id)
    attempted_answers = AttemptedAnswer.objects.all()
    user_attempts = []

    for attempt in attempts:
        if attempt.student.id == student_id and attempt.quiz == quiz:
            user_attempts.append(attempt)
            student = attempt.student

    return render(request, 'main/results/group_results_detail.html', {"user_attempts":user_attempts, "quiz":quiz, "attempted_answers":attempted_answers, "student":student})

###----------------------------------------------------------------------------------###
### Scores posted from results

def group_scores(request):

    order = request.GET.get('order', 'desc')
    cursem = Semester.objects.get(is_current=True)
    subjects = Subject.objects.filter(semester=cursem)
    dic = []
    avg=[]

    for subject in subjects:
        if order == 'asc':
            grades = Grade.objects.filter(subject=subject).order_by('score')
        elif order == 'desc':
            grades = Grade.objects.filter(subject=subject).order_by('-score')
        elif order == 'high':
            high = 0
            high_student = None
            for grade in subject.grades.all():
                if grade.score > high:
                    high = grade.score
                    high_student = grade.student
            grades = Grade.objects.filter(student=high_student, subject=subject)
            print(grades)
        elif order == 'low':
            low = 101
            low_student = None
            for grade in subject.grades.all():
                if grade.score < low:
                    low = grade.score
                    low_student = grade.student
            grades = Grade.objects.filter(student=low_student, subject=subject)
            print(grades)
        elif order == 'average':
            total=0
            numGrades=0
            for grade in subject.grades.all():
                total+=grade.score
                numGrades+=1
            avg.append({
                "subject":subject,
                "average":round(total/numGrades, 2)
            })
            grades=None


        dic.append({
            "subject":subject,
            "grades":grades
        })
        
    grade_percentages = get_percentages(cursem)
    grade_percentages_json = json.dumps(grade_percentages)

    return render(request, 'main/scores/group_scores.html', {"dic":dic, "subjects":subjects, "avg":avg, "grade_percentages_json":grade_percentages_json, "order":order})

##returns a list of letter grades and what percentage they make up compared to all grades
def get_percentages(cursem):

    grades = Grade.objects.filter(subject__semester=cursem)

    percentA = percentB = percentC = percentD = percentF = total = 0  
    for grade in grades:
        total += 1
        if grade.score >= 90:
            percentA += 1
        elif grade.score >= 80:
            percentB += 1
        elif grade.score >= 70:
            percentC += 1
        elif grade.score >= 60:
            percentD += 1
        else:
            percentF += 1

    if total != 0:
        percentA  = round(percentA / total, 2)
        percentB  = round(percentB / total, 2)
        percentC  = round(percentC / total, 2)
        percentD  = round(percentD / total, 2)
        percentF  = round(percentF / total, 2)

    grade_percentages = {
        'A': percentA,
        'B': percentB,
        'C': percentC,
        'D': percentD,
        'F': percentF
    }
    return grade_percentages

def ind_scores(request):

    cursem = Semester.objects.get(is_current=True)
    subjects = Subject.objects.filter(semester=cursem)
    student = request.user
    percentiles = []
    dic = []

    #calculates a student's percentile for a particular subject based on their grade
    for subject in subjects:
        num = Grade.objects.filter(subject=subject).count() #number of grades in a particular subject
        rank = 0
        grades = Grade.objects.filter(subject=subject).order_by('score')
        for grade in grades:
            rank += 1
            if grade.student == request.user:
                percentile = rank / num * 100
                percentiles.append({
                    "student":request.user,
                    "percentile":percentile,
                    "subject":subject,
                })

    grades = Grade.objects.all()

    for subject in subjects:
        for quiz in subject.quizzes.all():
            highest_score = 0
            count = 0
            for attempt in quiz.attempts.all():
                if attempt.student == student:
                    count += 1
                    if attempt.score > highest_score:
                        highest_score = attempt.score
                

            dic.append({
                "subject":subject,
                "quiz":quiz,
                "highest_score":highest_score,
                "count":count
            })

    return render(request, 'main/scores/ind_scores.html', {"dic":dic, "subjects":subjects, "student":student, "grades":grades, "cursem":cursem, "percentiles":percentiles})

def grade_chart(request):
    student = request.user
    semesters = Semester.objects.all()
    cursem = Semester.objects.get(is_current=True)
    selsem = request.GET.get('sem')
    sem = None
    if selsem:
        subjects = Subject.objects.filter(semester=Semester.objects.get(name=selsem))
        sem = Semester.objects.get(name=selsem)
    else:
        subjects = Subject.objects.filter(semester=cursem)
        sem = cursem
    data = {}

    for subject in subjects:
        grade = Grade.objects.get(subject=subject, student=request.user)
        data[subject.title] = grade.score

    json_data = json.dumps(data)

    return render(request, 'main/scores/grade_chart.html', {"semesters":semesters, "sem":sem, "json_data":json_data, "student":student})

###----------------------------------------------------------------------------------###
### Subjects

def subjects(request):

    subjects = Subject.objects.all()
    cursem = Semester.objects.get(is_current=True)

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = request.user
            subject.semester = cursem
            subject.save()
            return redirect('/subjects/', {"subjects":subjects, "form":form })
    else:
        form = SubjectForm()

    return render(request, 'main/subject/subjects.html', {"subjects":subjects, "form":form, "cursem":cursem })

def semes(request):

    semesters = Semester.objects.all()

    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            sem = form.save(commit=False)
            sem.save()
            return redirect('/semes/', {"form":form, "semesters":semesters})
    else:
        form = SemesterForm()
            
    return render(request, 'main/semes.html', {"form":form, "semesters":semesters})

def current_semes(request):
    semesters = Semester.objects.all()

    if request.method == 'POST':
        selected_semester_id = request.POST.get('current_semester')
        Semester.objects.all().update(is_current=False)
        Semester.objects.filter(id=selected_semester_id).update(is_current=True)
        return redirect('/semes/')
    
    return render(request, 'main/current_semes.html', {"semesters":semesters})


        







