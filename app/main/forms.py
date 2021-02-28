from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired


class SessionFormInline(FlaskForm):
    id = HiddenField('id:')
    name = StringField('', validators=[DataRequired()])

    def load(self, data):
        self.id.default = data.id
        self.name.default = data.name
        self.is_active.default = data.is_active
        self.process()


class SessionForm(FlaskForm):
    id = HiddenField('id:')
    name = StringField('', validators=[DataRequired()])

    def load(self, data):
        self.id.default = data.id
        self.name.default = data.name
        self.is_active.default = data.is_active
        self.process()


class HistoryForm(FlaskForm):
    id = HiddenField('id:')
    session_id = HiddenField('session_id:')
    story = StringField('story:', validators=[DataRequired()])
    value = StringField('value:', validators=[DataRequired()])

    def load(self, data):
        self.id.default = data.id
        self.session_id = data.session_id
        self.story.default = data.story
        self.value = data.value
        self.process()
