from django import forms

class CalendarForm(forms.Form):  
	event_name = forms.CharField(
		label='Event name:',
		validators=[],
		widget = forms.TextInput(attrs = {
			"class" : "text",
			"style" : "margin-top: 2%; font-weight: bolder;",
			"name" : "fname",
			"placeholder" : "Fort was here",
		}),
	)

	start_time = forms.TimeField(
		label = "Start time:",
		widget = forms.TimeInput(attrs = {
			'type' : 'time',
		}),
	)

	end_time = forms.TimeField(
		label = "End time:",
		widget = forms.TimeInput(attrs = {
			'type' : 'time',
		}),
	)

	duration = forms.IntegerField(label="Duration:")

	datecount = forms.IntegerField(widget=forms.HiddenInput())

	# https://jacobian.org/2010/feb/28/dynamic-form-generation/
	# https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form
	def __init__(self, *args, **kwargs):
		datecount = kwargs.pop('datecount', 0)
		super(CalendarForm, self).__init__(*args, **kwargs)
		
		if datecount:
			for i in range(int(datecount)):
				self.fields['date_%s' % i] = forms.DateField(input_formats=['%d-%m-%Y'])

	def get_dates(self):
		for name, value in self.cleaned_data.items():
			if name.startswith('date_'):
				yield (value)

class LoginForm(forms.Form):
	name = forms.CharField(max_length=40, label="Your Name:")
	email = forms.CharField(max_length=40)
	password = forms.CharField(max_length=40, widget=forms.PasswordInput(render_value=True))

class ScheduleForm(forms.Form):
	schedulecount = forms.IntegerField(widget=forms.HiddenInput())

	meeting_details = forms.CharField(max_length=255, widget=forms.Textarea())

	# https://jacobian.org/2010/feb/28/dynamic-form-generation/
	# https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form
	def __init__(self, *args, **kwargs):
		schedulecount = kwargs.pop('schedulecount', 0)
		super().__init__(*args, **kwargs)
		
		if schedulecount:
			for i in range(int(schedulecount)):
				self.fields['schedule_%s' % i] = forms.DateTimeField(input_formats=['%B %d %Y %H:%M:%S'])

	def get_schedules(self):
		for name, value in self.cleaned_data.items():
			if name.startswith('schedule_'):
				yield (value)

class BookingForm(forms.Form):
	schedule_id = forms.IntegerField(widget=forms.HiddenInput())
	name = forms.CharField(max_length=40)
	email = forms.CharField(max_length=40)
	message = forms.CharField(max_length=250)
