import xmltodict
import json
import re
from toposort import toposort_flatten, toposort
from datetime import datetime
from .models import Course

def get_time(time):
    """Converts string in the PT%%H%%M%%S format to %%h%%m"""

    return time.split('PT')[1].split('H')[0] + 'h' + \
            time.split('H')[1].split('M')[0] + 'm'

def top_sort(doc):

    course_dict = {}
    tobe_sorted = {}
    memo = {}
    children = {}
    uid_to_pop = []
    for task in doc['Project']['Tasks']['Task']:

        uid = int(task['UID'])
        if any([keyword in task['Name'].lower() 
                for keyword in ['sint&rde', 'journey start']]):
            uid_to_pop.append(uid)
            continue

        # extract wanted values          
        _id = int(task['ID']) - 1 
        name = task['Name']
        
        work = get_time(task['Work'])
        
        if 'Notes' in task.keys():
            link = task['Notes']
        else:
            link = ''
        
        if 'ExtendedAttribute' in task.keys():
            if type(task['ExtendedAttribute']) == list:
                skill = task['ExtendedAttribute'][1]['Value']
                media = task['ExtendedAttribute'][0]['Value']
            else:
                if task['ExtendedAttribute']['FieldID'] == '188743731':
                    media = task['ExtendedAttribute']['Value']
                    skill = ''
                elif task['ExtendedAttribute']['FieldID'] == '188743734':
                    skill = task['ExtendedAttribute']['Value']
                    media = ''
        else:
            skill = ''
            media = ''
        
        if 'PredecessorLink' in task.keys():
            if type(task['PredecessorLink']) == list:
                predecessor = [int(element['PredecessorUID'])
                                for element in task['PredecessorLink']]
            else:
                predecessor = [int(task['PredecessorLink']['PredecessorUID'])]
        else:
            predecessor = []
        
        predecessor = [n for n in predecessor if n not in uid_to_pop]
        
        length = get_time(task['Duration'])
        start = task['Start'].replace('T', ' ')
        end = task['Finish'].replace('T', ' ')

        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

        # # get level to determine child courses
        current_level = int(task['OutlineLevel'])

        if current_level not in memo.keys():
            memo[current_level] = []

        memo[current_level].append(uid)

        if current_level > 1:
            parent_uid = memo[current_level - 1][-1]
            if parent_uid in children.keys():
                children[parent_uid].append(uid)
            else:
                children[parent_uid] = [uid]

        course_dict[uid] = {
                            '_id': _id,
                            'name': name,
                            'skill': skill,
                            'media': media,
                            'link': link,
                            'work': work,
                            'predecessor': predecessor,
                            'length': length,
                            'start': start,
                            'end': end
        }

        
        if predecessor:
            tobe_sorted[uid] = {x for x in predecessor}

    return toposort_flatten(tobe_sorted), course_dict, children

def save_courses(order, course_dict, children):
    done = []
    
    for uid in order:
        course = Course.objects.update_or_create(
            name = course_dict[uid]['name'],
            ms_uid = uid, 
            defaults = {
            'ms_id': course_dict[uid]['_id'],
            'work': course_dict[uid]['work'],
            'link': course_dict[uid]['link'],
            'skill': course_dict[uid]['skill'],
            'media': course_dict[uid]['media'],
            'length': course_dict[uid]['length'],
            'start': course_dict[uid]['start'],
            'end': course_dict[uid]['end']
            }
        )
        course = course[0]
        course.predecessor.clear()
        for pred_uid in course_dict[uid]['predecessor']:
            predecessor = Course.objects.get(ms_uid=pred_uid)
            course.predecessor.add(predecessor)

        done.append(uid)
    
    for uid, course_dict in course_dict.items():
        course_name = course_dict['name']
        if uid not in done:
            course = Course.objects.update_or_create(
                name = course_name,
                ms_uid = uid,
                defaults = {
                'ms_id': course_dict['_id'],
                'work': course_dict['work'],
                'link': course_dict['link'],
                'skill': course_dict['skill'],
                'media': course_dict['media'],
                'length': course_dict['length'],
                'start': course_dict['start'],
                'end': course_dict['end']
                }
            )
        done.append(uid)
            
    for parent_uid, child_list in children.items():
        parent = Course.objects.get(ms_uid=parent_uid)
        parent.children.clear()
        for child_uid in child_list:
            child = Course.objects.get(ms_uid=child_uid)
            parent.children.add(child)
            
    # delete courses that aren't on the xml file
    Course.objects.exclude(ms_uid__in=done).delete()
    

def parse_xml(file):
    """
    Parses MS Project xml export and upserts in the db. 
    """

    #read file
    doc = xmltodict.parse(file)

    # topological sort
    order, course_dict, children = top_sort(doc)

    # parse and save
    save_courses(order, course_dict, children)

def courses_to_json(course_set):
    out = []

    for course in course_set:

        pred_str = ', '.join([pred.name for pred in course.predecessor.all()])
        
        if course.precedes.all():
            tasks = [
                        {
                            'id': course.ms_id,
                            'name': course.name,
                            'color': '#9FC5F8',
                            'from': course.start.strftime('%Y-%m-%d %H:%M:%S'),
                            'to': course.end.strftime('%Y-%m-%d %H:%M:%S'),
                            'dependencies': [{'to': sucessor.ms_id}]
                        } 

                        for sucessor in course.precedes.all()
                    ]
        else: 
            tasks = [
                        {
                            'id': course.ms_id,
                            'name': course.name,
                            'color': '#9FC5F8',
                            'from': course.start.strftime('%Y-%m-%d %H:%M:%S'),
                            'to': course.end.strftime('%Y-%m-%d %H:%M:%S')
                        } 
                    ]

        course_dict = {
            'id': course.ms_id,
            'name': course.name,
            'skill': course.skill,
            'media': course.media,
            'link': course.link,
            'work': course.work,
            'predecessors': pred_str if pred_str != '' else '',
            'length': course.length,
            'children': [child.name for child in course.children.all().order_by('ms_id')],
            'tasks': tasks
        }
        
        out.append(course_dict)


    return out
