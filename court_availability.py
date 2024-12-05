from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import re
import asyncio
import aiohttp
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
def spot_matches_avail(spot, avail):
    for availWindow in avail:
        if (date_utils.is_day_between(spot['date'].strftime('%a').lower(), availWindow['dayStart'], availWindow['dayEnd']) and \
            not spot['timeStart'] < availWindow['timeStart'] and \
            not spot['timeEnd'] > availWindow['timeEnd']):
            return True
    return False

def get_user_input():
    # prompt user for availability
    duration = int(input(color.BOLD + 'Enter duration (mins): ' + color.END))
    rawAvail = input(color.BOLD + 'Enter availability...' + color.END + '\n\
    (ex. "tue 06-22:30,thu-fri 08:30-12")\n\
    ("any xx-xx" - any day of week. blank for all availability):\n')

    # TODO: validate user input

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

    return {
        'duration': duration,
        'availability': avail
    }

async def request_data(facility_data, location_data, duration):
    async with aiohttp.ClientSession() as session:
        # need get req to set session cookies and obtain rv token before availability post req
        async with session.get(f'{facility_data['baseURL']}/Facility?facilityId={facility_data['facilityId']}') as get_req:
            content = await get_req.read()
            soup = BeautifulSoup(content, 'lxml')
            form_token = soup.find('input', attrs={'name': '__RequestVerificationToken'})['value']

            post_data = [
                ('facilityId', facility_data['facilityId']),
                ('daysCount', facility_data['daysCount']),
                ('serviceId', facility_data['serviceId']),
                ('date', datetime.now(timezone.utc).isoformat()),
                ('duration', duration),
                ('__RequestVerificationToken', form_token),
            ]
            for durationId in location_data['durationIds']:
                post_data.append(('durationIds[]', durationId))

            r = await session.post(
                f'{facility_data['baseURL']}/FacilityAvailability',
                data=post_data,
            )
            return await r.read()

def get_matches(booking_avail, personal_avail, labels, duration):
    avail_days = booking_avail['availabilities']

    matches = []
    for day in avail_days:
        date = day['Date']
        # Timestamp is given in milliseconds
        timestamp_ms = int(re.findall(r'\d+', date)[0])
        # Convert milliseconds to seconds and create a datetime object
        timestamp_sec = timestamp_ms / 1000
        date = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        # Skip non-matching days
        if (not filter(lambda x: date_utils.is_day_between(date.strftime('%a').lower(), x.dayStart, x.dayEnd), personal_avail)):
            next
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
                    'timeStart': start_time,
                    'timeEnd': end_time,
                    'date': date
                }
                if (spot_matches_avail(formattedSpot, personal_avail)):
                    matches.append(formattedSpot)
    return matches

async def get_facility_matches(location, location_data, facility, duration, avail):
    refined_data = {
        'baseURL': location_data['baseURL'],
        'daysCount': location_data['daysCount'],
        'serviceId': location_data['serviceId']
    }
    refined_data.update(facility)
    r = await request_data(refined_data, location_data, duration)
    facility_labels = {
        'location': location,
        'facility': facility['name']
    }
    return get_matches(json.loads(r.decode('utf-8')), avail, facility_labels, duration)

async def main():
    user_input = get_user_input()
    duration = user_input['duration']
    avail = user_input['availability']

    # load facility data from file
    with open('facility_data.json', 'r') as file:
        facility_data = json.load(file)

    all_matches = []
    tasks = []
    # iterate through facilities to check their availabilities
    for location in facility_data:
        location_data = facility_data[location]
        for facility in location_data['facilities']:
            tasks.append(get_facility_matches(location, location_data, facility, duration, avail))
    all_matches = await asyncio.gather(*tasks)
    # have to flatten results: list of lists -> list
    flattened_matches = [item for sublist in all_matches for item in sublist]

    # sort results by time
    sorted_matches = sorted(flattened_matches, key = lambda x: (x['date'], x['timeStart'].strftime('%p%I%M'), x['location'], x['facility']))

    # print availability matches
    if (len(sorted_matches) < 1):
        print('There are currently no available time slots')
    else:
        print('\n########## MATCHING AVAILABILITY ##########')
        for match in sorted_matches:
            print(f'{match['date'].strftime('%a (%b %d)').upper()} - {match['timeStart'].strftime('%I:%M%p')}-{match['timeEnd'].strftime('%I:%M%p')} - ' +
                  f'{match['location']} {match['facility']}')

if __name__ == '__main__':
    asyncio.run(main())