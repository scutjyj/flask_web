from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ModifyPasswordForm, ForgetPasswordForm, ResetPasswordForm
from .. import db
from ..email import send_email

RESET_PASSWORD_MAGIC = 666

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/modify_password', methods=['GET', 'POST'])
@login_required
def modify_password():
    form = ModifyPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user.verify_password(form.old_password.data):
            if form.old_password.data == form.new_password.data:
                # new password is the same as the old,do nothing.
                flash('New password is the same as the old!Please use another one!')
            else:
                user.password = form.new_password.data
                user.confirmed = False
                flash('You have changed your password successfully!Please confirm your account again!')
                return redirect(url_for('main.index'))
        else:
            # the old password is wrong.
            flash('The old password given is wrong!')
        form.old_password.data = form.new_password.data = form.new_password2.data = ''
        return render_template('auth/modify_password.html', form=form)
    else:
        return render_template('auth/modify_password.html', form=form)


@auth.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        user.reset_password_confirmed = True
        send_email(user.email, 'Reset Password',
                   'auth/email/reset_password_confirm', user=user, user_id=user.id+RESET_PASSWORD_MAGIC, token=token)
        flash("""A password-reset-confirmation email has been sent to you by email.\nBefore logging in,
        you should confirm this email and reset your password.""")
        return redirect(url_for('auth.login'))
    else:
        return render_template('auth/forget_password.html', form=form)


@auth.route('/reset_password/<user_id>/<token>', methods=['GET', 'POST'])
def reset_password(user_id, token):
    user = User.query.filter_by(id=int(user_id)-RESET_PASSWORD_MAGIC).first()
    if user.reset_password_confirmed:
        # this user is under reset_password confirming state.
        if user.reset_password_confirm(token):
            form = ResetPasswordForm()
            if form.validate_on_submit():
                if user.verify_password(form.new_password.data):
                    # the new password is the same as the old one.
                    form.new_password = form.new_password2 = ''
                    flash('The new password is the same as the old one.')
                    return redirect(url_for('auth.reset_password', user_id=user_id, token=token))
                else:
                    user.password = form.new_password.data
                    user.reset_password_confirmed = False
                    user.confirmed = False
                    flash('Reset password successfully.')
                    return redirect(url_for('auth.login'))
            else:
                return render_template('auth/reset_password.html', form=form)
        else:
            flash('Invalid reset password token.')
    else:
        flash('Invalid reset password state.')
    return redirect(url_for('auth.login'))
