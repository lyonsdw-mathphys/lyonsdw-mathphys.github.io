# create calendar items, assignments, and discussions for a canvas course
#  from an plain text input file
#   % python3 gesso.py input_filename

from canvasapi import Canvas
from datetime import datetime
from datetime import timedelta
import os
import sys

# how long before a given class meeting will the discussion board be open?
#  this setting is 5pm, two days before the next meeting
DISCUSSION_OPENING_WINDOW = timedelta(days=-2)+timedelta(hours=17)

# Store your API key in a separate file
with open("access_token.txt") as f:
    API_KEY = f.read().strip()

# read input data for Canvas calendar and assignment entries
in_file = open(sys.argv[1],'r')
#in_file = open('test_canvas_cal_input.txt', 'r') 
Lines = in_file.readlines()
in_file.close()

# course id must appear on first line of input file
COURSE_ID = Lines[0][Lines[0].find('<course_id>')+11:Lines[0].find('</course_id>')]

# Construct course object
API_URL = "https://lvc.instructure.com"
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)
sections = list(course.get_sections())
assignment_groups = list(course.get_assignment_groups())

# construct calendar events, disucssion boards, and assignments
count = 0
entry_count = 0
for line in Lines:
    line_date = ''
    line_title = ''
    line_hw_flag = 0
    line_discussion_flag=0
    first = line.find('<date>')
    last = line.find('</date>')
    if (first > -1 and last > -1):
       line_date = line[first + 6: last]
    first = line.find('<title>')
    last = line.find('</title>')
    if (first > -1 and last > -1):
       line_title = line[first + 7: last]       
    if (line.find('<hw/>') > -1):
        line_hw_flag = 1
    if (line.find('<discuss/>') > -1):
        line_discussion_flag = 1        
    if (line_date !='' and line_title != ''):
        start_date = datetime.strptime(line_date, '%Y-%m-%d')
        calendar_event_dict = {
            'title': line_title,
            'context_code': 'course_12996',
            'start_at': start_date,
            'all_day': True
        }
        canvas.create_calendar_event(calendar_event_dict)
        # put up discussion boards, one for each section
        #  need to remove absolute reference to section numbers below

        title_string = "Class Discussion: " + line_title + " " + line_date
        message_string = 'Post requests for class discussion here. Attach your work. Describe your discussion request using at least one complete sentence.'
        delayed_post_date= start_date + DISCUSSION_OPENING_WINDOW

        if (line_discussion_flag == 1):
            for section in sections:
               new_discussion_topic=course.create_discussion_topic()
               new_discussion_topic.update(title=title_string)
               new_discussion_topic.update(message=message_string)
               new_discussion_topic.update(specific_sections=section.id)
               new_discussion_topic.update(discussion_type='threaded')
               new_discussion_topic.update(delayed_post_at=delayed_post_date )

        # construct and post assignments
            #   restrict allowed file extensions ???
            #      'allowed_extensions': ['pdf'],
        if (line_hw_flag==1):
            assnmt_name = "Homework " + line_title + " " + line_date
            due_date = start_date + timedelta(seconds=-1)
            assignment_dict = {
            'name': assnmt_name,
            'assignment_group_id': assignment_groups[0].id,
            'grading_type': 'points',
            'points_possible': 2,
            'submission_types': ['online_upload'],
            'due_at': due_date,
            'description': "Upload your homework here. Each solution must include at least one complete sentence, using appropriate vocabulary.",
            'published': False,
            }
            course.create_assignment(assignment_dict)
    count += 1

print("All is well\n")

