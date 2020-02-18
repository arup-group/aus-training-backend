from django.db import models

class Course(models.Model):
    ms_uid = models.IntegerField()
    ms_id = models.IntegerField()
    name = models.TextField()
    work = models.TextField(blank=True)
    link = models.TextField(blank=True)
    skill = models.TextField(blank=True)
    media = models.TextField(blank=True)
    children = models.ManyToManyField('self', 
                                    symmetrical=False, 
                                    related_name='parent')
    predecessor = models.ManyToManyField('self', 
                                    symmetrical=False, 
                                    related_name='precedes')
    length = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.name

class SiteVisit(models.Model):
    date = models.DateTimeField()

    def __str__(self):
        return self.date

class LinkClick(models.Model):
    course = models.ForeignKey(Course, 
                            on_delete=models.CASCADE, 
                            related_name='click_dates')
    date = models.DateTimeField()

    def __str__(self):
        return self.name




