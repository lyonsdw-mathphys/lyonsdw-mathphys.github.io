# delete calendar items, assignments, and discussions for a given date range
#  read course id, start and end dates from a file
#  % python3 palimpsest.py input_filename
#   BEWARE! Note 12/8/2020 date checking in calendar events is not working
#    *all* calendar events for the course are being removed right now
#    (date checking is working correctly for discussions and assignments)

from canvasapi import Canvas
import os
import sys
import canvasapi
import dotenv
import datetime
from datetime import datetime
from datetime import timedelta

# Store your API key in a separate file
with open("access_token.txt") as f:
    API_KEY = f.read().strip()
API_URL = "https://lvc.instructure.com"    
canvas_api = canvasapi.Canvas(API_URL, API_KEY)

# read input data for Canvas calendar and assignment entries
in_file = open(sys.argv[1],'r')
Lines = in_file.readlines()
in_file.close()

# course id must appear on first line of input file
COURSE_ID = Lines[0][Lines[0].find('<course_id>')+11:Lines[0].find('</course_id>')]
DELETE_FROM_DATE = Lines[1][Lines[1].find('<delete_from_date>')+18:Lines[1].find('</delete_from_date>')]
DELETE_TO_DATE = Lines[2][Lines[2].find('<delete_to_date>')+16:Lines[2].find('</delete_to_date>')]
delete_from_date = datetime.strptime(DELETE_FROM_DATE, '%Y-%m-%d')
delete_to_date = datetime.strptime(DELETE_TO_DATE, '%Y-%m-%d')

# Construct course object
API_URL = "https://lvc.instructure.com"
canvas = Canvas(API_URL, API_KEY)
user = canvas.get_user('self')
course = canvas.get_course(COURSE_ID)
sections = list(course.get_sections())
assignment_groups = list(course.get_assignment_groups())
discussion_topics = list(course.get_discussion_topics())
assignments = course.get_assignments()

# delete calendar item
#  NOTE 12/7/2020 right now we are just deleting all calendar events, date checking is not working
os.system("rm calendar_got.txt")
get_command_string = 'curl "https://lvc.instructure.com/api/v1/calendar_events?all_events=1&type=event&context_codes[]=course_' + COURSE_ID + '" -X GET  -H "Authorization: Bearer ' + API_KEY + '" >> calendar_got.txt'
os.system(get_command_string)
cal_event_list_file = open('calendar_got.txt', 'r')
calendar_events_raw = cal_event_list_file.readlines()[0]
cal_event_list_file.close()
calendar_events = []

while (calendar_events_raw.find('"id":') > -1):
    start_pos = calendar_events_raw.find('"id":')+5
    end_pos = start_pos + 6
    add_id = calendar_events_raw[start_pos:end_pos]
    start_pos = calendar_events_raw.find('"all_day_date":"')+16
    end_pos = start_pos + 10
    add_date = calendar_events_raw[start_pos:end_pos]
    calendar_events.append([add_id,add_date])
    calendar_events_raw = calendar_events_raw[calendar_events_raw.find('}')+1:]

for calendar_event in calendar_events:
   #    cal_ev_date = datetime.strptime(calendar_event[1], '%Y-%m-%d') 
   #    if (cal_ev_date >= delete_from_date and cal_ev_date <= delete_to_date):
   delete_command_string = 'curl "https://lvc.instructure.com/api/v1/calendar_events/' + str(calendar_event[0]) + '" -X DELETE   -H "Authorization: Bearer ' + API_KEY + '"'
   os.system(delete_command_string)

# delete assignment
for a in assignments:
    assnmt = course.get_assignment(a.id)
    assnmt_date = datetime.strptime(assnmt.name[len(assnmt.name)-10:], '%Y-%m-%d')
    if (assnmt_date >= delete_from_date and assnmt_date <= delete_to_date):
        assnmt.delete()

    

# delete discussion
for d in discussion_topics:
    disc_date = datetime.strptime(d.title[len(d.title)-10:], '%Y-%m-%d')
    if (disc_date >= delete_from_date and disc_date <= delete_to_date):
        d.delete()

# fix annoying cursor position
print("\n")

