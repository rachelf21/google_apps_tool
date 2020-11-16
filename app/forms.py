from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField, RadioField
from wtforms.fields.html5 import DateField
import datetime

class SelectDateForm(FlaskForm):

    options = []
    options.append(['application/vnd.google-apps.document','Document'])
    options.append(['application/vnd.google-apps.spreadsheet','Spreadsheet'])

    file_type = SelectField('Select', 
                      choices=options)
       
    date_start = DateField('DatePicker', format='%Y-%m-%d', default=datetime.date.today())
    date_end = DateField('DatePicker', format='%Y-%m-%d', default=datetime.date.today())
    #date = DateField('Date', format="%m-%d-%Y",validators=[DataRequired()])

    owner = RadioField('Owner', choices=[('me', 'Only Me'),('anyone', "Anyone")],default='anyone')
    
    btnSubmit = SubmitField('Submit')

    
