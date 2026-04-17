from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class TestMessageForm(FlaskForm):
    channel = StringField("Channel", validators=[DataRequired(), Length(max=40)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=5000)])
