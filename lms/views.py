from django.shortcuts import render,redirect,get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login 

from django.db import transaction

from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
import re
from django.contrib.auth.decorators import login_required

from .models import Enrollment, User,Lesson,Certificate
from .models import Course,CompletedLesson
from django.contrib.auth import logout

from django.utils import timezone
from .models import Quiz, QuizQuestion, QuizOption, QuizResponse,DiscussionForum
from .forms import QuizQuestionForm,QuizForm,QuizOptionForm
from datetime import timedelta

from .forms import UserProfilePicForm,MessageForm,FeedbackForm





def home(request):
    is_teacher = request.user.groups.filter(name='Teacher').exists() if request.user.is_authenticated else False
    print("teacher status: ",is_teacher)
    context = {
        'is_teacher': is_teacher,
        # ... other context variables
    }
    return render(request,'home.html',context)

    
def login_view(request):
    if request.method == 'POST':
        print("Form submitted")  # Check if form is submitted

        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)
        


    
        if not (username and password):
            messages.error(request, 'Please fill all fields.')
            return render(request, 'login.html')

        # Use authenticate to check credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            user.last_login = timezone.now()  # Update last_login
            user.save()
            return redirect(request.GET.get('next', 'home'))  # Redirect to home page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')



def register(request):
    if request.method == "POST":
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        
        
        
       

        
        if not all([first_name,username,password,confirm_password, email, phone_number]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'register.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, 'register.html')

        if not re.match(r'^\d{10}$', phone_number):
            messages.error(request, "Phone number must be 10 digits.")
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

 
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return render(request, 'register.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number is already registered.")
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return render(request, 'register.html')

      
        
        try:
            with transaction.atomic():  
               
                print("Creating user...")
               
                


                user = User.objects.create(
                      
                    phone_number=phone_number,
                    email=email ,
                    username=username,
                    user_type='student',
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password(password)
  

                )
                print(user.password)

                print("student record created successfully")
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('login')  

        except Exception as e:
   
            print("Error occurred during registration:", str(e))
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'register.html')

    return render(request, 'register.html')

        

    
def courses(request):
    
    all_courses = Course.objects.all()
    
    if request.user.is_authenticated:
        enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
        available_courses = [course for course in all_courses if course.course_id not in enrolled_courses]
    else:
      
        available_courses = all_courses
    
    return render(request, 'courses.html', {'courses': available_courses})

@login_required

def profile(request):
     if request.method == 'POST':
        p_form = UserProfilePicForm(request.POST, request.FILES, instance=request.user)
        if p_form.is_valid():
            p_form.save()
            return redirect('profile')
     
     p_form=UserProfilePicForm()
     context={
      
        'p_form': p_form
     }
     return render(request,'profile.html', context)






def course_details(request, course_id,lesson_id=None,quiz_id=None):
    print(course_id)
    print(lesson_id)
    course = Course.objects.get(course_id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('position')
    quiz=Quiz.objects.filter(course=course)
    
    for x in quiz:
        print(x.quiz_title)

    if lesson_id is None and lessons.exists():
        initial_lesson = lessons.first()
    else:
        initial_lesson = get_object_or_404(Lesson, lesson_id=lesson_id)

    
    if request.user.is_authenticated:
        CompletedLesson.objects.get_or_create(user=request.user, lesson=initial_lesson)
    context = {
        'course': course,
        'lessons': lessons,
        'initial_lesson': initial_lesson,
        'quiz':quiz
    }
    return render(request, 'course_details.html', context)


@login_required
def discussion(request, course_id):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user 
            message.course = Course.objects.get(course_id=course_id) 
            message.save()
            return redirect('discussion', course_id=course_id)  
    else:
        form = MessageForm()

    course = Course.objects.filter(course_id=course_id).first()
    all_courses = Course.objects.all()
    enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    context={
        'chat':DiscussionForum.objects.filter(course=course),
        
        'course':course,
       
        'courses':[c for c in all_courses if c.course_id in enrolled_courses]
    }
    return render(request,'discussion.html', context)


@login_required
def discussion_home(request):
    all_courses = Course.objects.all()
    enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    context={
        
        'courses':[c for c in all_courses if c.course_id in enrolled_courses]
    }
    return render(request,'discussion_forum_blank.html', context)





@login_required
def enroll_in_course(request, course_id):
    print(course_id)
    
    course = get_object_or_404(Course, course_id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

    if created:
      
        messages.success(request, "You have successfully enrolled in the course!")
    else:
        
        messages.info(request, "You are already enrolled in this course.")

    return redirect('course_details', course_id=course_id)





def my_courses(request):
   
    enrollments = Enrollment.objects.filter(user=request.user)
    progress_data = []
   

    for enrollment in enrollments:
       
        course = enrollment.course
        
        total_lessons=Lesson.objects.filter(course=course).count()
        total_quiz=Quiz.objects.filter(course=course).count()
      
        completed_lessons = CompletedLesson.objects.filter(user=request.user, lesson__course=course).count()
       
        completed_quizzes = (
        QuizResponse.objects
        .filter(student=request.user, question__quiz__course=course)
        .values('question__quiz')  
        .distinct()  
        .count()
)

        
        print("values are: ")
        print(completed_lessons)
        print(completed_quizzes)
        print(total_lessons)
        print(total_quiz)

        progress_percentage = ((completed_lessons+completed_quizzes) / (total_lessons+total_quiz) * 100) if total_lessons > 0 else 0 if total_quiz > 0 else 0
        enrollment.progress = progress_percentage
        enrollment.save()

        print(progress_percentage)
        progress_data.append({
            'course': course,
            'progress_percentage': progress_percentage,
        })

    return render(request, 'my_courses.html', {'progress_data': progress_data})


@login_required
def certificates(request):
    certificate=Certificate.objects.filter(student=request.user)
    has_certificates=certificate.exists()
    context={
        'certificates':certificate,
        'has_certificates':has_certificates

    }
    return render(request,'certificates.html',context)

@login_required
def certificate_view(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)

    context = {
        'certificate': certificate  
    }
    print("reached here ")

    
    print(certificate)
    
    
    
    return render(request,'index.html',context)

def logout_view(request):
    logout(request)
    return redirect('home') 

def mark_lesson_completed(user, lesson):
    CompletedLesson.objects.get_or_create(user=user, lesson=lesson)


@login_required

def create_quiz(request):
    print(request.user.username)
    if not request.user.groups.filter(name='Teacher').exists():
        messages.error(request, "You do not have permission to access this page.")
        print("not a teacher")
        return redirect('home')  
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.start_time=timezone.now()
            quiz.end_time=quiz.start_time+timedelta(minutes=quiz_form.cleaned_data['duration'])
            quiz.save()
            return redirect('add_quiz_questions', quiz_id=quiz.quiz_id)
    else:
        quiz_form = QuizForm()

    context = {'quiz_form': quiz_form}
    return render(request, 'create_quiz.html', context)


def add_quiz_questions(request, quiz_id):
        if not request.user.groups.filter(name='Teacher').exists():
            messages.error(request, "You do not have permission to access this page.")
            print("not a teacher")
            return redirect('home')
        quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
       

        if request.method == 'POST':
            if 'delete_option' in request.POST:
                question_id = request.POST.get('delete_option')
                print("question id is: ")
                print(question_id)
                QuizQuestion.objects.filter(question_id=question_id).delete()
                return redirect('add_quiz_questions', quiz_id=quiz_id)
            
            question_text = request.POST.get('question_text')
            question_type = request.POST.get('question_type')
            max_marks = request.POST.get('max_marks')

    #      
            question = QuizQuestion(
                quiz=quiz,
                question_text=question_text,
                question_type=question_type,
                max_marks=max_marks
            )
            question.save()  
        print("question saved")
        question_form = QuizQuestionForm(request.POST)
        if question_form.is_valid():


            if request.POST.get('action') == 'finish':
               
                return redirect('view_quiz_questions', quiz_id=quiz_id)
            else:
               
                question_form = QuizQuestionForm()  

        else:
          question_form = QuizQuestionForm()

        questions = QuizQuestion.objects.filter(quiz=quiz)  
        context = {
        'quiz': quiz,
        'question_form': question_form,
        'questions': questions
    }
        return render(request, 'add_quiz_questions.html', context)


def view_quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    questions = QuizQuestion.objects.filter(quiz=quiz)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'view_quiz_questions.html', context)

def feedback(request):
    if request.method=='POST':
        form=FeedbackForm(request.POST)
        if form.is_valid():
            feedback=form.save(commit=False)
            feedback.user=request.user
            feedback.save()
            messages.success(request, "Thank you for your valuable feedback!")
            return redirect('profile')
        else:
            form=FeedbackForm()
    context={
        'form': FeedbackForm()
    }
    return render(request, 'feedback.html', context)



def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    questions = QuizQuestion.objects.filter(quiz=quiz)

    if request.method == 'POST':
        
        QuizResponse.objects.filter(question__quiz=quiz, student=request.user).delete()

        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.question_id}')
            if selected_option_id:
                selected_option = get_object_or_404(QuizOption, option_id=selected_option_id)
             
                QuizResponse.objects.create(
                    student=request.user,
                    question=question,
                    selected_option=selected_option,
                    marks_obtained=selected_option.is_correct * question.max_marks
                )
            
        return redirect('quiz_result', quiz_id=quiz.quiz_id)  

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'take_quiz.html', context)

def quiz_result(request, quiz_id):
    quiz = Quiz.objects.get(quiz_id=quiz_id)
    responses = QuizResponse.objects.filter(question__quiz=quiz, student=request.user)
    total_marks = sum(response.marks_obtained for response in responses)

    context = {
        'quiz': quiz,
        'responses': responses,
        'total_marks': total_marks,
    }
    return render(request, 'quiz_result.html', context)


def add_quiz_options(request, question_id):

    question = get_object_or_404(QuizQuestion, question_id=question_id)

    if request.method == 'POST':
        if 'delete_option' in request.POST:
            option_id = request.POST.get('delete_option')
            print("option id is: ")
            print(option_id)
            QuizOption.objects.filter(option_id=option_id).delete()
            return redirect('add_quiz_options', question_id=question_id)
      
        option_text = request.POST.get('option_text')
        is_correct = request.POST.get('is_correct') == 'on'  

      
        option = QuizOption(
            question=question,
            option_text=option_text,
            is_correct=is_correct
        )
        option.save()

        
        if request.POST.get('action') == 'finish':
           
            return redirect('view_quiz_questions', quiz_id=question.quiz.quiz_id)
        else:
       
            option_form = QuizOptionForm()  

    else:
        option_form = QuizOptionForm()

   
    options = QuizOption.objects.filter(question=question)
    context = {
        'question': question,
        'option_form': option_form,
        'options': options
    }
    return render(request, 'add_quiz_options.html', context)

