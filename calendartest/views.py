from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.crypto import get_random_string

from .forms import CalendarForm, LoginForm, ScheduleForm, BookingForm

import string

import datetime

from datetime import timedelta

from event.models import Event, DateRange, Inviter, Schedule, Invitee

def home(request):
	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = CalendarForm(data=request.POST, datecount=request.POST.get('datecount'))

		# Check if the form is valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			event_name = form.cleaned_data['event_name']

			start_time = form.cleaned_data['start_time'] 
			end_time = form.cleaned_data['end_time'] 

			duration = form.cleaned_data['duration'] 

			event_id = get_random_string(14, string.ascii_letters + string.digits)
			share_id = get_random_string(14, string.ascii_letters + string.digits)

			event = Event(event_id=event_id, share_id=share_id, name=event_name, start_time=start_time, end_time=end_time, duration=duration)

			event.save()

			dates = [date for date in form.get_dates()]

			date_ranges = []
			start_date = dates[0]

			if len(dates) == 1:
				date_ranges.append([start_date, start_date])
			else:
				for index in range(1, len(dates)):
					if (dates[index] - dates[index-1] > datetime.timedelta(days=1)):
						end_date = dates[index-1]
						date_ranges.append((start_date, end_date))
						start_date = dates[index]

				end_date = dates[index]
				date_ranges.append((start_date, end_date))


			for date_range in date_ranges:
				date_range = DateRange(event=event, start_date=date_range[0], end_date=date_range[1])
				date_range.save()

			

			# redirect to a new URL:
			return redirect(reverse('signin', args=[event_id]))

	# If this is a GET (or any other method) create the default form.
	else:
		form = CalendarForm(initial={
				'event_name': 'serge', 
				'duration': '60', 
				'start_time': '08:00', 
				'end_time': '20:00',
			})
	
	
	context = {
		'form' : form,
		'month' : datetime.date.strftime(datetime.date.today(), "%B"),
		'year' : datetime.date.strftime(datetime.date.today(), "%Y"),
		'days' : [(datetime.date.today() + datetime.timedelta(days=i+1)).day for i in range(-1, 34)],
	}
	
	return render(request, "index.html", context)

def signin(request, event_id):
	event = get_object_or_404(Event, event_id=event_id)

	if request.method == 'POST':
		form = LoginForm(data=request.POST)

		if form.is_valid():
			name = form.cleaned_data['name']
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			try:
				existing_inviter = event.inviter_set.get(name=name)
			except:
				existing_inviter = None
			
			if existing_inviter and existing_inviter.password == password:
				request.session['user'] = existing_inviter.inviter_id
				return redirect(reverse('inviter', args=[event_id]))
			elif existing_inviter and existing_inviter.password != password:
				messages.error(request, "Wrong password")
			else:
				inviter_id = get_random_string(14, string.ascii_letters + string.digits)
				inviter = Inviter(event=event, inviter_id=inviter_id, name=name, email=email, password=password)
				inviter.save()
				request.session['user'] = inviter.inviter_id
				return redirect(reverse('inviter', args=[event_id]))

	else:
		form = LoginForm(initial={
			'name' : 'serge', 
			'email' : 'sergealecrivera@gmail.com', 
			'password' : 'secret'
			})
		
	context = {
		'form' : form
	}

	return render(request, "login.html", context=context)

def inviter(request, event_id):
	success = 0
	if 'user' in request.session:
		inviter = get_object_or_404(Inviter, inviter_id=request.session['user'])
		existing_schedules = inviter.schedule_set.all()
		meeting_details = inviter.meeting_details
		inviter_name = inviter.name
	else:
		return redirect(reverse('signin', args=[event_id]))

	form = ScheduleForm(initial={
		"meeting_details" : meeting_details,
	})
		
	event = get_object_or_404(Event, event_id=event_id)
	share_link = f"{request.get_host()}/{event.share_id}/invitee/"

	date_ranges = event.daterange_set.all()

	available_dates = ""
	for date_range in date_ranges:
		start_date = date_range.start_date
		end_date = date_range.end_date

		delta = end_date - start_date
		
		for i in range(delta.days + 1):
			date = (start_date + datetime.timedelta(days=i))

			if date >= datetime.date.today():
				available_dates += date.isoformat() + ","

	start_time = event.start_time
	end_time = event.end_time

	print(start_time.hour)
	print(start_time.minute)

	print(end_time.hour)
	print(end_time.minute)

	start_time_delta =  datetime.timedelta(hours=start_time.hour, minutes=start_time.minute) 
	end_time_delta = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute)

	duration = event.duration

	delta = end_time_delta - start_time_delta

	print(delta.seconds)
	print(duration)

	available_times = ""

	for i in range(0, delta.seconds//60 + 1, duration):
		time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=i)).strftime("%H:%M")
		available_times += time + ","

	available_dates = available_dates[:-1]
	available_times = available_times[:-1]

	if request.method == 'POST':
		# Create a form instance and populate it with data from the request (binding):
		form = ScheduleForm(data=request.POST, schedulecount=request.POST.get('schedulecount'))

		if form.is_valid():
			schedules = [schedule for schedule in form.get_schedules()]
			meeting_details = form.cleaned_data["meeting_details"]

			inviter.meeting_details = meeting_details
			inviter.save()

			existing_schedules.delete()

			for schedule in schedules:
				schedule = Schedule(inviter=inviter, start_datetime=schedule, end_datetime=schedule + datetime.timedelta(minutes=duration), is_booked=False)
				schedule.save()
			success = 1

	existing_schedules = ",".join([sched.start_datetime.isoformat() for sched in existing_schedules])

	context = {
		'month' : datetime.date.strftime(datetime.date.today(), "%B"),
		'year' : datetime.date.strftime(datetime.date.today(), "%Y"),
		'days' : [(datetime.date.today() + datetime.timedelta(days=i+1)).day for i in range(-1, 34)],
		'available_dates' : available_dates,
		'available_times' : available_times,
		'inviter_name' : inviter_name,
		'existing_schedules' : existing_schedules,
		'form' : form,
		'success' : success,
		'share_link' : share_link,
	}

	print("hello")
	print(existing_schedules)

	return render(request, "inviter.html", context)


import json

def invitee(request, share_id):
	success = 0
	form = BookingForm()

	event = get_object_or_404(Event, share_id=share_id)

	inviter = event.inviter_set.all()[0]
	schedules = inviter.schedule_set.filter(is_booked=False)
	print(schedules)

	if (request.method == "POST"):
		form = BookingForm(data=request.POST)

		if form.is_valid():
			schedule_id = form.cleaned_data["schedule_id"]
			name = form.cleaned_data["name"]
			invitee_email = form.cleaned_data["email"]
			message = form.cleaned_data["message"]

			schedule = Schedule.objects.get(schedule_id=schedule_id)
            
			schedule.is_booked = True 
			schedule.save()

			invitee = Invitee(schedule=schedule, name=name, email=invitee_email, message=message)
			invitee.save()

			print(schedule.start_datetime.isoformat())
			send_invites(event.name, invitee_email, inviter, schedule.start_datetime.isoformat(), schedule.end_datetime.isoformat())
			success = 1

	temp = ""
	for schedule in schedules:
		schedule_object = {}
		schedule_object["start"] = schedule.start_datetime.isoformat()
		schedule_object["end"] = schedule.end_datetime.isoformat()
		schedule_object["id"] = schedule.schedule_id

		temp += "." + json.dumps(schedule_object)

	schedules = temp[1:]
	
	context = {
		'month' : datetime.date.strftime(datetime.date.today(), "%B"),
		'year' : datetime.date.strftime(datetime.date.today(), "%Y"),
		'days' : [(datetime.date.today() + datetime.timedelta(days=i+1)).day for i in range(-1, 34)],
		'schedules' : schedules,
		'form' : form,
		'success' : success
	}

	return render(request, "invitee.html", context)

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import google.oauth2.credentials

scopes = ["https://www.googleapis.com/auth/calendar.events"]

from event.models import OauthCredentials

# view used to request from spreadsheet 
def send_invites(event_name, invitee_email, inviter, start_datetime, end_datetime):
	creds = OauthCredentials.objects.all()[0]

	creds = {
		'token': creds.token,
		'refresh_token': creds.refresh_token,
		'token_uri': creds.token_uri,
		'client_id': creds.client_id,
		'client_secret': creds.client_secret,
	}

	credentials = google.oauth2.credentials.Credentials(**creds)

	# access Google Sheets API with API key
	service = build('calendar', 'v3', credentials=credentials)

	inviter_email = inviter.email
	print(inviter_email)

	meeting_details = inviter.meeting_details

	event = {
		'summary': event_name,
		'description': meeting_details,
		'start': {
			'dateTime': start_datetime,
			'timeZone': 'Asia/Shanghai',
		},
		'end': {
			'dateTime': end_datetime,
			'timeZone': 'Asia/Shanghai',
		},
		'attendees': [
			{'email': inviter_email},
			{'email': invitee_email},
		],
		'reminders': {
			'useDefault': False,
			'overrides': [
			{'method': 'email', 'minutes': 24 * 60},
			{'method': 'popup', 'minutes': 10},
			],
		},

		"guestsCanSeeOtherGuests" : False,
	}

	event = service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()

	print('Event created: %s' % (event.get('htmlLink')))


from googleapiclient.discovery import build

from django.shortcuts import render, redirect
from django.urls import reverse
import google_auth_oauthlib.flow

# permissions set for the Google App to be accessed currently it is set to view and download only
# more permissions here https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# home view
def generate_token(request):

	# create flow from client credentials downloaded from Google cloud
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('creds.json', scopes=SCOPES)

	# URI where the oauth2's response will be redirected this must match with one of the authorized URIs configured in Google Cloud
	flow.redirect_uri = 'http://localhost:8000/oauthcallback/'

	# configuring the authorization url which will be used to request from oauth2
	authorization_url, state = flow.authorization_url(include_granted_scopes='true', access_type='offline')

	# store the state in the session
	request.session['state'] = state
	
	# redirect to the authorization url which will redirect back to the callback view
	return redirect(authorization_url)

# callback used to extract the credentials. this will have a URL with query parameters set to the necessary arguments to extract the credentials e.g. http://localhost/oauthcallback/?state=K15TtnzoBKKepgg0Z3Ph86nEgGiubM&code=4%2F0AWgavdeDqFt44lGsb24OidcJrpSeLUja1OZkhfHNgNsacb00BrKgyeA-6pY7Uw08lt7s9g&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets
def callback(request):
	# get URL of the callback
	response = request.get_full_path()

	# extract the state stored from the home view
	state = request.session['state']

	# create a new flow note that scopes were not defined because it gets appended to the previous scopes
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
	 'creds.json', scopes=None, state=state)

	# same redirect uri as before
	flow.redirect_uri = 'http://localhost:8000/oauthcallback/'

	# function call to get the credentials
	flow.fetch_token(authorization_response=response)

	# store the fetched credentials
	credentials = flow.credentials

	creds = OauthCredentials(token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret)

	creds.save()

	# go back to the home page
	return redirect(reverse('home'))