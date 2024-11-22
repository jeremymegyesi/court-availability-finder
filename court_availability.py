from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import re
import date_utils


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# compares a given spot with inputted availability
def spotMatchesAvailability(spot, avail):
    for availWindow in avail:
        if (date_utils.is_day_between(spot['day'], availWindow['dayStart'], availWindow['dayEnd']) and \
            not spot['timeStart'] < availWindow['timeStart'] and \
            not spot['timeEnd'] > availWindow['timeEnd']):
            return True


# prompt user for availability
duration = int(input(color.BOLD + 'Enter duration (mins): ' + color.END))
rawAvail = input(color.BOLD + 'Enter availability...' + color.END + '\n\
(ex. "tue 06-22:30,thu-fri 08:30-12")\n\
("any xx-xx" - any day of week. blank for all availability):\n')

# validate user input

# parse user input
avail = rawAvail.split(',')
for i, window in enumerate(avail):
   window = window.split(' ')
   day = window[0].split('-')
   t = window[1].split('-')
   avail[i] = {
      'dayStart': day[0],
      'dayEnd': day[1] if len(day) == 2 else day[0],
      'timeStart': date_utils.extract_time(t[0]),
      'timeEnd': date_utils.extract_time(t[1])
    }

# load facility data
with open('facility_data.json', 'r') as file:
    facility_data = json.load(file)

# get availability data
session = HTMLSession()
def request_data(session, facility_data):
    gr = session.get(f'{facility_data['baseURL']}/Facility?facilityId={facility_data['facilityId']}')
    f = open("extracted-page.html", "w", encoding="utf-8")
    f.write(gr.content.decode('utf-8'))
    f.close()

    soup = BeautifulSoup(gr.content, "lxml")
    formToken = soup.find('input', attrs={'name': '__RequestVerificationToken'})['value']
    post_data = [
        ('facilityId', facility_data['facilityId']),
        ('daysCount', facility_data['daysCount']),
        ('serviceId', facility_data['serviceId']),
        ('date', datetime.now(timezone.utc).isoformat()),
        ('duration', duration),
        ('__RequestVerificationToken', formToken),
    ]
    for durationId in location_data['durationIds']:
        post_data.append(('durationIds[]', durationId))

    r = session.post(f'{facility_data['baseURL']}/FacilityAvailability', data=post_data)
    # print('Request response: ', r.status_code, r.reason)
    return r

def getMatches(booking_avail, personal_avail, labels):
    avail_days = booking_avail['availabilities']

    matches = []
    for day in avail_days:
        date = day['Date']
        # Timestamp is given in milliseconds
        timestamp_ms = int(re.findall(r'\d+', date)[0])
        # Convert milliseconds to seconds and create a datetime object
        timestamp_sec = timestamp_ms / 1000
        date = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        # Get the day of the week
        day_of_week = date.strftime("%a").lower()
        for bookingGroup in day['BookingGroups']:
            for availableSpot in bookingGroup['AvailableSpots']:
                # calculate end time
                start_time = date_utils.extract_time(f'{availableSpot['Time']['Hours']}:{availableSpot['Time']['Minutes']}')
                datetime_obj = datetime.combine(datetime.today(), start_time)
                new_datetime = datetime_obj + timedelta(minutes=duration)
                # Extract the updated time
                end_time = new_datetime.time()
                formattedSpot = {
                    'location': labels['location'],
                    'facility': labels['facility'],
                    'day': day_of_week,
                    'timeStart': start_time,
                    'timeEnd': end_time
                }
                if (spotMatchesAvailability(formattedSpot, personal_avail)):
                    matches.append(formattedSpot)
    return matches

all_matches = []

# iterate through facilities to check their availabilities
for location in facility_data:
    location_data = facility_data[location]
    for facility in location_data['facilities']:
        refined_data = {
            'baseURL': location_data['baseURL'],
            'daysCount': location_data['daysCount'],
            'serviceId': location_data['serviceId']
        }
        refined_data.update(facility)
        r = request_data(session, refined_data)
        facility_labels = {
            'location': location,
            'facility': facility['name']
        }
        all_matches += getMatches(json.loads(r.content.decode('utf-8')), avail, facility_labels)
        
session.close()

# sort results by time
sorted(all_matches, key = lambda x: (x['day'], x['timeStart'], x['location'], x['facility']))

# print availability matches
if (len(all_matches) < 1):
    print('There are currently no available time slots')
else:
    for match in all_matches:
        print(f'{match['location']} {match['facility']} - {match['day']} {match['timeStart']}-{match['timeEnd']}')
