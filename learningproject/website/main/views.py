from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import AnswerForm, QuestionForm, SubjectSetupForm, RegisterForm, PostFullForm, PostForm, ReplyForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import Post, File, Question, Subject, Score, Attempt

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
### How subjects are created


#Screen that prompts the user to create a subject
@login_required(login_url="/login")
def subject_setup(request):
    #subject creation form
    if request.method == 'POST':
        form = SubjectSetupForm(request.POST)
        if form.is_valid():
            setup = form.save(commit=False)
            setup.teacher = request.user
            setup.save()
            return redirect("/question_setup/" + str(setup.id))
    else:
        form = SubjectSetupForm()
    return render(request, 'main/subject/subject_setup.html', {"form":form})


#Screen that prompts the user to add questions to their subject
@login_required(login_url="/login")
def question_setup(request, pk):
    subject = Subject.objects.get(id=pk)
    questions = subject.questions.all()
    #question creation form
    if request.method == 'POST' and 'submitform' in request.POST:
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.subject = subject
            question.save()
            return redirect('/answer_setup/' + str(question.id), {"form":form, "subject":subject, "questions":questions})
    elif request.method == 'POST' and 'question-id' in request.POST:
        question_id = request.POST.get("question-id")
        Question.objects.filter(id=question_id).delete()
        form = QuestionForm()
    else:
        form = QuestionForm()

    return render(request, 'main/subject/question_setup.html', {"form":form, "subject":subject, "questions":questions})


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
    
    return render(request, 'main/subject/answer_setup.html', {"answers":answers, "form":form, "question":question})


#Pulls up a list of all subjects that have been posted
@login_required(login_url="/login")
def view_subjects(request):
    subjects = Subject.objects.all()
    return render(request, 'main/subject/view_subjects.html', {"subjects": subjects})


#Similar to view_subjects, but directs exclusively students to a screen that
#allows them to take a subject
@login_required(login_url="/login")
def content(request):
    subjects = Subject.objects.all()
    scores = Score.objects.all()
    subjects_with_attempts = []

    for subject in subjects:
        attemptsRem = subject.max_attempts - Attempt.objects.filter(student=request.user, subject=subject).count()

        subjects_with_attempts.append({
            "subject":subject,
            "attemptsRem":attemptsRem
        })
    
    
    return render(request, 'main/subject/content.html', {"subjects":subjects, "scores":scores, "subjects_with_attempts":subjects_with_attempts})


#This view pulls up a subject and calculates the student's score
#based on what they submit through a form
@login_required(login_url="/login")
def take_subject_detail(request, pk):

    subject = Subject.objects.get(id=pk)

    if (Attempt.objects.filter(student=request.user, subject=subject).count() >= subject.max_attempts):
        return redirect('/content/')

    new_attempt = Attempt(student=request.user, subject=subject)
    new_attempt.save()

    correct = 0
    incorrect = 0
    total = 0
    #take subject form
    if request.method == 'POST':
        print(request.POST)
        questions = subject.questions.all()
        for question in questions:
            answers = question.answers.all()
            for answer in answers:
                new_attempt.answers.add(answer)
                if request.POST.get(str(answer.id)) == 'True':
                    correct += 1
                elif request.POST.get(str(answer.id)) == 'False':
                    incorrect += 1
        total = correct + incorrect
        if total != 0:
            score = Score(user=request.user, subject=subject, value=(correct / total)*100)
            new_attempt.score = score
            print(score.value)
            score.save()
            return redirect('/ind_results/')

    return render(request, 'main/subject/take_subject_detail.html', {"subject":subject})



###----------------------------------------------------------------------------------###
### Results posted from subjects


#Displays individual student's scores
@login_required(login_url="/login")
def ind_results(request):
    scores = Score.objects.all()
    counter = 0
    for score in scores:
        if request.user == score.user:
            counter += 1

    return render(request, 'main/results/ind_results.html', {"scores":scores, "counter":counter})


#Displays all students' scores
@login_required(login_url="/login")
def group_results(request):
    subjects = Subject.objects.all()
    scores = Score.objects.all()
    return render(request, 'main/results/group_results.html', {"subjects":subjects, "scores":scores})




