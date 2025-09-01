# app/forms/auth.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):

    email = StringField("Email",validators=[DataRequired(),Email(message="Invalid email format"),Length(max=255),],)
    phone = StringField("Phone",
                        validators=[
                            DataRequired(),
                            Length(min=10, max=15, message="Phone number must be between 10 and 15 digits"),
                        ]
                    )
    
    password = PasswordField("Password",validators=[DataRequired(),Length(min=4, message="Password must be at least 4 characters long")],)
    confirm_password = PasswordField("Confirm Password",  # Changed to consistent naming
                                     validators=[
                                         DataRequired(),
                                         EqualTo("password", message="Passwords do not match.")
                                     ],
                                     )
    submit = SubmitField("Register")




class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email(message="Invalid email format")],)
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")




class RequestOtp(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email(message="Invalid email format")],)
    submit = SubmitField("Request OTP")  # Changed to consistent naming




class VerifyOtp(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired()])
    submit = SubmitField("Verify OTP")  # Changed to consistent naming


class ResetPassword(FlaskForm):
    password = PasswordField("Password",
                             validators=[
                                 DataRequired(),
                                 Length(min=8, message="Password must be at least 8 characters long")  # Added length validation
                             ]
                             )
    confirm_password = PasswordField("Confirm Password",  # Changed to consistent naming
                                     validators=[
                                         DataRequired(),
                                         EqualTo("password", message="Passwords do not match")
                                     ],
                                     )
    submit = SubmitField("Reset Password")  # Changed to consistent naming

class UserProfileForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Invalid email format"), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(min=10, max=15, message="Phone number must be between 10 and 15 digits")])
    password = PasswordField("New Password", validators=[Optional(), Length(min=4, message="Password must be at least 4 characters long")])
    confirm_password = PasswordField("Confirm New Password",
                                     validators=[Optional(), EqualTo("password", message="Passwords do not match")])
    submit = SubmitField("Update Profile")