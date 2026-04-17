from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class ProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    is_active = BooleanField("Active")
    submit = SubmitField("Save")


class MailAccountForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email_from = StringField("From email", validators=[DataRequired(), Email(), Length(max=255)])
    smtp_host = StringField("SMTP host", validators=[DataRequired(), Length(max=255)])
    smtp_port = IntegerField("SMTP port", validators=[DataRequired(), NumberRange(min=1, max=65535)])
    username = StringField("Username", validators=[Optional(), Length(max=255)])
    use_tls = BooleanField("Use TLS")
    is_active = BooleanField("Active")
    submit = SubmitField("Save")


class DeliveryChannelForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    kind = SelectField(
        "Type",
        choices=[("email", "Email"), ("telegram", "Telegram"), ("slack", "Slack"), ("webhook", "Webhook")],
        validators=[DataRequired()],
    )
    destination = StringField("Destination", validators=[DataRequired(), Length(max=255)])
    is_active = BooleanField("Active")
    submit = SubmitField("Save")


class TestNotificationForm(FlaskForm):
    profile_id = IntegerField("Profile ID", validators=[Optional(), NumberRange(min=1)])
    channel_id = IntegerField("Delivery channel ID", validators=[Optional(), NumberRange(min=1)])
    recipient = StringField("Recipient", validators=[DataRequired(), Length(max=255)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=255)])
    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Send test")
