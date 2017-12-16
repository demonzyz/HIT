from django.db import models

# Create your models here.


class Template(models.Model):
    name = models.CharField(max_length=30, unique=True)
    desc = models.CharField(max_length=50, null=True)
    url = models.URLField(null=False)
    method = models.SmallIntegerField(choices=((0, 'GET'), (1, 'POST')), null=False)
    headers = models.CharField(max_length=500, null=True)
    data = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return self.name


class Case(models.Model):
    name = models.CharField(max_length=30, unique=True)
    desc = models.CharField(max_length=50, null=True)
    status = models.SmallIntegerField(choices=((0, 'run'), (1, 'skip')))

    def __unicode__(self):
        return self.name

class Step(models.Model):
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=50, null=True)
    order = models.IntegerField(null=False, default=1)
    template = models.ForeignKey(Template)
    case = models.ForeignKey(Case)
    check = models.CharField(max_length=500, null=True)
    headers = models.CharField(max_length=500, null=True)
    data = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=30, unique=True)
    desc = models.CharField(max_length=50, null=True)
    case = models.ManyToManyField(Case)
    report = models.CharField(max_length=100, null=True)

    def __unicode__(self):
        return self.name