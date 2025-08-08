from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired(message="請輸入使用者名稱")])
    password = PasswordField('密碼', validators=[DataRequired(message="請輸入密碼")])
    submit = SubmitField('登入')

class RegisterForm(FlaskForm):
    username = StringField('使用者名稱', validators=[
        DataRequired(message="請輸入使用者名稱"),
        Length(min=3, max=20, message="使用者名稱須為 3～20 字元")
    ])
    password = PasswordField('密碼', validators=[DataRequired(message="請輸入密碼")])
    submit = SubmitField('註冊')
