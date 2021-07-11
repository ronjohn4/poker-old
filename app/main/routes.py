from flask import render_template, redirect, url_for, request, current_app, Response
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Session, Audit, User, History, load_user, clear_user_activity, clear_game_votes
from app.main.forms import SessionForm, HistoryForm, AddGameForm
from datetime import datetime


@bp.route('/addgame/<name>', methods=["PUT"])
def addgame(name):
    # form = SessionForm()
    # if form.validate_on_submit():
    var = Session(
        # owner_id=current_user.id,
        name=name,
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_active=True
        )
    db.session.add(var)
    db.session.flush()  # flush() so the id is populated after add
    db.session.commit()
    # form.name.data = ''

    status_code = Response(status=200)
    
    return status_code


@bp.route('/')
@bp.route('/list/', methods=["GET", "POST"])
def list():
    if current_user.is_authenticated:
        clear_user_activity(current_user.id)
    form = SessionForm()
    addgameform = AddGameForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Session(
            # owner_id=current_user.id,
            name=request.form['name'],
            start_date=datetime.now(),
            end_date=datetime.now(),
            is_active=True
            )
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        db.session.commit()
        form.name.data = ''
    datalist = Session.query.order_by(Session.end_date.desc()).limit(100).all()
    row_count = Session.query.count()
    return render_template('main/list.html', datalist=datalist, form=form, max_exceeded=(row_count > 100), addgameform=addgameform)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
# @login_required
def view(id):
    form = HistoryForm()
    data_single = User.query.filter_by(id=current_user.id).first_or_404()
    # if data_single.current_session_id is None:
    data_single.current_session_id = id
    data_single.vote = None
    db.session.commit()

    data_single = Session.query.filter_by(id=id).first_or_404()
    playerlist = User.query.filter_by(current_session_id=data_single.id).order_by(User.username.asc())
    historylist = History.query.filter_by(session_id=data_single.id).order_by(History.a_datetime.desc())
    return render_template('main/view.html', datasingle=data_single, playerlist=playerlist, 
                                            historylist=historylist, form=form)


@bp.route('/delete/<int:id>', methods=["GET", "POST"])
# @login_required
def delete(id):
    # TODO - trigger refresh if deleted session was valid
    Session.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('.list'))


@bp.route('/addhistory/', methods=["GET", "POST"])
# @login_required
def addhistory():
    # TODO - trigger game refresh
    form = HistoryForm()
    clear_game_votes(current_user.current_session_id)
    if request.method == 'POST' and form.validate_on_submit():
        var = History(
            session_id = current_user.current_session_id,
            a_datetime=datetime.now(),
            story=request.form['story'],
            value=request.form['value']
            )
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        db.session.commit()
    return redirect(request.referrer)


# /vote/2?vote=3    //userid=2 and vote=3
@bp.route('/vote/<int:id>', methods=["GET", "POST"])
# @login_required
def vote(id):
    # TODO - trigger refresh for this game
    vote = request.args.get('vote') 
    if vote in ['0','1', '2', '3', '5', '8', '13', '20', '40', '100', '?', 'ꝏ', 'pass']:
        data_single = User.query.filter_by(id=id).first_or_404()
        data_single.vote = vote
        db.session.commit()
    return redirect(request.referrer)
