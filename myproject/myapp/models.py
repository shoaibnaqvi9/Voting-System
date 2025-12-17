from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, default='student')
    has_voted = models.BooleanField(default=False)
    def __str__(self):
        return self.student_id

class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    president = models.CharField(max_length=100)
    vice_president = models.CharField(max_length=100)
    secretary = models.CharField(max_length=100)
    finance_manager = models.CharField(max_length=100)

    def __str__(self):
        return f"Vote by {self.student.student_id}"

class Candidate(models.Model):
    POSITION_CHOICES = [
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('Secretary', 'Secretary'),
        ('Finance Manager', 'Finance Manager'),
    ]
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.position})"

class ElectionSettings(models.Model):
    is_active = models.BooleanField(default=False) # To start/end voting

    def __str__(self):
        return "Election Status"
# Add dynamic candidate management and election status controls for admins.