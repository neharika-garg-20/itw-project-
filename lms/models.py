# from django.db import models


from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

# Step 1: Create a custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# Step 2: Update your custom User model
class User(AbstractBaseUser, PermissionsMixin):  # Inherit from AbstractBaseUser and PermissionsMixin
    USER_TYPES = [('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')]

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Important fields for admin and authentication
    is_active = models.BooleanField(default=True)  # Required by Django's authentication
    is_staff = models.BooleanField(default=False)  # Required for access to the admin panel
    is_superuser = models.BooleanField(default=False)  # Required to grant all permissions

    profile_picture = models.URLField(max_length=255, null=True, blank=True)

    objects = CustomUserManager()  # Use your custom user manager

    USERNAME_FIELD = 'username'  # Login will use the username
    REQUIRED_FIELDS = ['email']  # Other required fields for creating a user

    def __str__(self):
        return self.username
# from django.contrib.auth.models import AbstractUser

# class User(AbstractUser):
#     USER_TYPES = [('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')]
#     phone_number = models.CharField(max_length=12, unique=True)
#     user_type = models.CharField(max_length=10, choices=USER_TYPES)
#     profile_picture = models.URLField(max_length=255, null=True, blank=True)

#     def __str__(self):
#         return self.username

# class User(models.Model):
#     USER_TYPES = [('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')]

#     user_id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=100, unique=True)
#     email = models.EmailField(max_length=100, unique=True)
#     phone_number = models.CharField(max_length=12, unique=True)
#     password = models.CharField(max_length=255)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100, null=True, blank=True)
#     user_type = models.CharField(max_length=10, choices=USER_TYPES)
#     date_joined = models.DateField(auto_now_add=True)
#     last_login = models.DateTimeField(null=True, blank=True)
#     profile_picture = models.URLField(max_length=255, null=True, blank=True)

#     def _str_(self):
#         return self.username

class Course(models.Model):
    course_id=models.AutoField(primary_key=True,default=1)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=200, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100)

    def _str_(self):
        return self.course_name

class Lesson(models.Model):
    lesson_title = models.CharField(max_length=100)
    lesson_description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    video_url = models.URLField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(default=0)

    def _str_(self):
        return self.lesson_title

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    date_enrolled = models.DateField(auto_now_add=True)
    progress = models.FloatField(default=0)
    COMPLETION_STATUS = [('In Progress', 'In Progress'), ('Completed', 'Completed')]
    completion_status = models.CharField(max_length=20, choices=COMPLETION_STATUS, default='In Progress')

    def _str_(self):
        return f'{self.user} - {self.course}'

class Quiz(models.Model):
    quiz_id=models.AutoField(primary_key=True,default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    quiz_title = models.CharField(max_length=100)
    max_marks = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def _str_(self):
        return self.quiz_title
class QuizQuestion(models.Model):
    question_id=models.AutoField(primary_key=True,default=1)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,null=True,blank=True)
    question_text = models.TextField()
    QUESTION_TYPE = [('Multiple Choice', 'Multiple Choice'), ('T/F', 'True/False')]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE)
    max_marks = models.IntegerField()

    def _str_(self):
        return self.question_text

class QuizOption(models.Model):
    option_id=models.AutoField(primary_key=True,default=1)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE,null=True,blank=True)
    option_no = models.IntegerField(default=0)
    option_text = models.TextField(default=0)
    is_correct = models.BooleanField(default=False)

    def _str_(self):
        return self.option_text

class QuizResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE,null=True,blank=True)
    selected_option = models.ForeignKey(QuizOption, on_delete=models.CASCADE,null=True,blank=True)
    marks_obtained = models.IntegerField(default=0)

    def _str_(self):
        return f'{self.student} - {self.question}'

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    date_issued = models.DateField()
    certificate_url = models.URLField(max_length=255)

    def _str_(self):
        return f'{self.student} - {self.course}'

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateField(auto_now_add=True)

    def _str_(self):
        return self.title
class DiscussionForum(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    content = models.TextField()
    date_posted = models.DateField(auto_now_add=True)
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def _str_(self):
        return f'Post by {self.user} on {self.course}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    content = models.TextField()
    date_sent = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)

    def _str_(self):
        return f'Notification for {self.user}'



class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    content = models.TextField()
    feedback_date = models.DateField(auto_now_add=True)

    def _str_(self):
        return f'Feedback from {self.user}'    
    


# class UserProfile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
#     bio = models.TextField(blank=True, null=True)
#     completed_courses = models.ManyToManyField('Course', blank=True, related_name="completed_users")
#     ongoing_courses = models.ManyToManyField('Course', blank=True, related_name="ongoing_users")
#     registration_date = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.user.username