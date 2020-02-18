from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Course
from .utils import *

@api_view(['GET', 'POST'])
def courses(request):
    if request.method == 'GET':
        
        course_set = Course.objects.all().order_by('ms_id')
        courses_list = courses_to_json(course_set)

        return Response({
            'courses': courses_list
        })
    
    if request.method == 'POST':
        # try:
        
        parse_xml(request.FILES['file'])
        return Response({'message': 'Database updated successfully.'}) 
        # except Exception as e:
        #     return Response({
        #         'message': 'Something went wrong. \n {}'.format(e)
        #         }, status=status.HTTP_400_BAD_REQUEST) 

        