from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Regexp, EqualTo


class LoginForm(FlaskForm): 
	login = StringField('Логин', 
		render_kw={"placeholder": "Логин (Не менее 6 символов)"},
		validators=[
		DataRequired(message='Необходимо ввести логин'),
		Regexp('^.{6,}$',message='Не менее 6 символов')
		]) 
	password = PasswordField('Пароль', 
		render_kw={"placeholder": "Пароль"},
		validators=[DataRequired(message='Необходимо ввести пароль')]) 
	remember_me = BooleanField('Запомни меня') 
	submit = SubmitField('Войти') 

class RegForm(FlaskForm): 
	name = StringField(
        'Имя',
		render_kw={"placeholder": "Имя",
			 "title": "Только текст от 2 до 15 символов. Двойные имена пишуться через тире"},
        validators=[
            DataRequired(message='Необходимо ввести имя'),
            Regexp(regex='^^(?:[A-Za-zАА-ЯЁа-яё]{2,15}-)?[A-Za-zАА-ЯЁа-яё]{2,15}$',
                   message='Имя должно содержать только текст от 2 до 15 символов. Двойные имена пишуться через тире')
        ]
    )
	second_name = StringField(
        'Фамилия',
		render_kw={"placeholder": "Фамилия",
			 "title": "Только текст от 2 до 15 символов. Двойные фамилии пишуться через тире"},
        validators=[
            DataRequired(message='Необходимо ввести фамилию'),
            Regexp(regex='^(?:[A-Za-zАА-ЯЁа-яё]{2,15}-)?[A-Za-zАА-ЯЁа-яё]{2,15}$',
                   message='Фмилия должна содержать только текст от 2 до 15 символов. Двойные фамилии пишуться через тире')
        ]
    )
	login = StringField('Логин',
		render_kw={"placeholder": "Логин",
			 "title": "Не менее 6 символов"}, 
		validators=[
		DataRequired(message='Необходимо ввести логин'),
		Regexp('^.{6,}$',message='Не менее 6 символов')
		]) 
	password = PasswordField(
        'Пароль',
		render_kw={"placeholder": "Пароль",
			 "title": "Не менее 8 символов, должны присутствовать прописные и строчные буквы, цифры, символы"},
        validators=[
            DataRequired(message='Необходимо ввести пароль'),
            EqualTo('confirm_password', message='Пароли должны совпадать'),
            Regexp(regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[\\W_]).{8,}$',
                   message='Пароль должен быть не менее 8 символов, должны присутствовать прописные и строчные буквы, цифры, символы')
        ])
	confirm_password = PasswordField('Подтверждение пароля', render_kw={"placeholder": "Подтверждение пароля"},
		validators=[
            DataRequired(message='Необходимо ввести повтор пароль')]) 
	accept_rules = BooleanField(
        'Я принимаю пользовательское соглашением',
        default=False,
        validators=[DataRequired(message='Необходимо согласится с пользовательским соглашением')]
    )
	submit = SubmitField('Зарегистрироваться') 



      