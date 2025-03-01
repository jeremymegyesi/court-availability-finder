from requests_html import HTMLSession
from bs4 import BeautifulSoup
import datetime
import json
import re
import asyncio
import aiohttp
import date_utils

class TextEffect:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   ITALICS = '\x1B[3m'
   END = '\033[0m'

DURATION_OPTIONS = [30, 60, 90, 120]

class CourtFinder():
    '''Web scraper to find court availability.'''
    
    def __init__(self, **kwargs):
        # load facility data from file
        try:
            with open('facility_data.json', 'r') as file:
                self._facility_data = json.load(file)
        except FileNotFoundError:
            raise Exception('Error occurred reading the facility configuration file')

    def get_facility_data(self):
        return self._facility_data
    
    def get_facility_locations(self):
        return self.get_facility_data().keys()
    
    # compares a given spot with inputted availability
    def _spot_matches_avail(self, spot, avail):
        for avail_window in avail:
            if (
                (
                    avail_window['start_date'] == 'any' or 
                    date_utils.is_day_between(spot['start_time'].date(), avail_window['start_date'], avail_window['end_date'])
                ) and not spot['start_time'].time() < avail_window['start_time'] and
                not spot['end_time'].time() > avail_window['end_time']
            ):
                return True
        return False

    async def _request_data(self, facility_data, location_data, duration):
        async with aiohttp.ClientSession() as session:
            # need get req to set session cookies and obtain rv token before availability post req
            async with session.get(f'{facility_data['baseUrl']}/Facility?facilityId={facility_data['facilityId']}') as get_req:
                content = await get_req.read()
                soup = BeautifulSoup(content, 'lxml')
                form_token = soup.find('input', attrs={'name': '__RequestVerificationToken'})['value']

                post_data = [
                    ('facilityId', facility_data['facilityId']),
                    ('daysCount', facility_data['daysCount']),
                    ('serviceId', facility_data['serviceId']),
                    ('date', datetime.date.today().isoformat()),
                    ('duration', duration),
                    ('__RequestVerificationToken', form_token),
                ]
                for durationId in location_data['durationIds']:
                    post_data.append(('durationIds[]', durationId))

                r = await session.post(
                    f'{facility_data['baseUrl']}/FacilityAvailability',
                    data=post_data,
                )
                return await r.read()

    def get_matches(self, booking_avail, personal_avail, labels, duration):
        avail_days = booking_avail['availabilities']

        matches = []
        for day in avail_days:
            date = day['Date']
            # Timestamp is given in milliseconds
            timestamp_ms = int(re.findall(r'\d+', date)[0])
            # Convert milliseconds to seconds and create a datetime object
            timestamp_sec = timestamp_ms / 1000
            date = datetime.datetime.fromtimestamp(timestamp_sec, tz=datetime.timezone.utc)
            # Skip non-matching days
            if (not filter(lambda x: x.start_date == 'any' or date_utils.is_day_between(date.strftime('%a').lower(), x.start_date, x.end_date), personal_avail)):
                next
            for bookingGroup in day['BookingGroups']:
                for availableSpot in bookingGroup['AvailableSpots']:
                    # calculate end time
                    start_time = datetime.datetime.combine(
                        date,
                        date_utils.extract_time(f'{availableSpot['Time']['Hours']}:{availableSpot['Time']['Minutes']}')
                    )
                    end_time = start_time + datetime.timedelta(minutes=duration)
                    formattedSpot = {
                        'location': labels['location'],
                        'facility': labels['facility'],
                        'start_time': start_time,
                        'end_time': end_time
                    }
                    if (self._spot_matches_avail(formattedSpot, personal_avail)):
                        matches.append(formattedSpot)
        return matches

    async def _get_facility_matches(self, location, location_data, facility, duration, avail):
        refined_data = {
            'baseUrl': location_data['baseUrl'],
            'daysCount': location_data['daysCount'],
            'serviceId': location_data['serviceId']
        }
        refined_data.update(facility)
        r = await self._request_data(refined_data, location_data, duration)
        facility_labels = {
            'location': location,
            'facility': facility['name']
        }
        return self.get_matches(json.loads(r.decode('utf-8')), avail, facility_labels, duration)
    
    def print_results(self, matches):
        if (len(matches) < 1):
            print('There are currently no available time slots')
        else:
            print(TextEffect.GREEN + TextEffect.BOLD + '\n########## MATCHING AVAILABILITY ##########' + TextEffect.END)
            for match in matches:
                print(f'{match['start_time'].strftime('%a (%b %d)').upper()} - {match['start_time'].strftime('%I:%M%p')}-{match['end_time'].strftime('%I:%M%p')} - ' +
                    f'{match['location']} {match['facility']}')
            print('\n' + TextEffect.END)
    
    async def find_courts(self, user_input):
        duration = user_input['duration']
        avail = user_input['availability']
        location = user_input['location']

        all_matches = []
        tasks = []
        facility_data = self.get_facility_data()
        locations = list(facility_data.keys()) if location.lower() == 'any' else \
            [next(x for x in facility_data.keys() if x.lower() == location)]
        
        # iterate through facilities to check their availabilities
        for location in locations:
            location_data = facility_data[location]
            for facility in location_data['facilities']:
                tasks.append(self._get_facility_matches(location, location_data, facility, duration, avail))
        all_matches = await asyncio.gather(*tasks)
        # have to flatten results: list of lists -> list
        flattened_matches = [item for sublist in all_matches for item in sublist]

        # sort results by time
        sorted_matches = sorted(flattened_matches, key = lambda x: (x['start_time'], x['location'], x['facility']))

        return sorted_matches


def parse_availability_input(_avail):
    # parse user input
    avail = _avail.split(',')
    for i, window in enumerate(avail):
        window = window.split(' ')

        day = window[0].split('-')
        time = window[1].split('-') if len(window) == 2 else []
        # time window should have 2 elements (start and end) or not be included
        # if not included, will match any time of day
        if len(time) != 2 and len(time) != 0:
            return None
        
        if len(day) == 1 and day[0].lower() == 'any':
            start_date = 'any'
            end_date = 'any'
        else:
            start_date = date_utils.extract_date(day[0])
            end_date = date_utils.extract_date(day[1]) if len(day) == 2 else start_date

        start_time = date_utils.extract_time(time[0]) if time else datetime.time(0, 0, 0)
        end_time = date_utils.extract_time(time[1]) if time else datetime.time(23, 59, 59, 999999)

        if not (start_date and end_date and start_time and end_time):
            return None
        
        avail[i] = {key: locals()[key] for key in ['start_date', 'end_date', 'start_time', 'end_time']} 
    return avail

def get_user_input(facility_data):
    duration = None
    while duration is None:
        try:
            _duration = int(input(TextEffect.BOLD + TextEffect.BLUE + '\nDuration (mins)?\n' + TextEffect.END +
                                TextEffect.ITALICS + 'Enter one of ' + str(DURATION_OPTIONS) + TextEffect.END + ':\n'))
            if _duration in DURATION_OPTIONS:
                duration = _duration
            else:
                raise ValueError()
            
        except ValueError:
            print(TextEffect.RED + '\nERROR: Invalid duration. Try again.\n' + TextEffect.END)

    avail = None
    while avail is None:
        _avail = input(TextEffect.BOLD + TextEffect.BLUE + '\nDates and times?\n' + TextEffect.END +
            TextEffect.ITALICS + '(ex. "tue 06-22:30,thu-fri,2025/02/12 08:30-12")\n' +
            '("any xx-xx" - any day of week. Leave time window blank for all-day availability):\n' + TextEffect.END)
        avail = parse_availability_input(_avail)
        if avail is None:
            print(TextEffect.RED + '\nERROR: Invalid availability. Try again.\n' + TextEffect.END)

    location = None
    while location is None:
        _location = input(TextEffect.BOLD + TextEffect.BLUE + '\nWhich location?\n' + TextEffect.END +
                        TextEffect.ITALICS + 'Choose one of ' + ", ".join(list(facility_data.keys())) +
                        ' or leave blank for all locations:\n' + TextEffect.END)
        if not _location:
            location = 'any'
            break
        if _location.lower() in (x.lower() for x in list(facility_data.keys())):
            location = _location

        if location is None:
            print(TextEffect.RED + '\nERROR: Invalid location. Try again.\n' + TextEffect.END)

    return {
        'duration': duration,
        'availability': avail,
        'location': location
    }

# TODO: add price estimate
async def main():
    broker = CourtFinder()
    user_input = get_user_input(broker.get_facility_data())
    matches = await broker.find_courts(user_input)
    broker.print_results(matches)

if __name__ == '__main__':
    asyncio.run(main())