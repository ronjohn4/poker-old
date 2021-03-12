from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Session, Audit, User, History, load_user
# from app.models import Instance, Key, Keyval, load_user
from app.main.forms import SessionForm, HistoryForm, SessionFormInline
from datetime import datetime


lastpagelist = 0
player_lastpage = 0
history_lastpage = 0


@bp.route('/')
@bp.route('/list/', methods=["GET", "POST"])
# @login_required
def list():
    global lastpagelist

    form = SessionFormInline()
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
        # writeaudit(var.id, None, str(var.to_dict()) )
        db.session.commit()
        lastpagelist = 0  # go back to first page after add, the new row will be on top
        form.name.data = ''
        # redirect(url_for('.list'))  # this will come right back to this route with a fresh form

    page = request.args.get('page', lastpagelist, type=int)
    lastpagelist = page
    datalist = Session.query.order_by(Session.end_date.desc()).paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.list', page=datalist.next_num) if datalist.has_next else None
    prev_url = url_for('.list', page=datalist.prev_num) if datalist.has_prev else None
    return render_template('main/list.html', datalist=datalist.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/addhistory/', methods=["GET", "POST"])
# @login_required
def addhistory():
    form = HistoryForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = History(
            session_id = current_user.session_id,
            story=request.form['story'],
            value=request.form['value']
            )
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        # writeaudit(var.id, None, str(var.to_dict()) )
        db.session.commit()
        # return redirct(url_for('.list'))
        return redirect(request.referrer)
    # return render_template('main/add.html', form=form)
    return redirect(request.referrer)


# /vote/2?vote=3    //userid=2 and vote=3
@bp.route('/vote/<int:id>', methods=["GET", "POST"])
# @login_required
def vote(id):
    vote = request.args.get('vote') 
    if vote in ['0','1', '2', '3', '5', '8', '13', '20', '40', '100', '?', 'ꝏ', 'pass']:
        data_single = User.query.filter_by(id=id).first_or_404()
        # before = str(data_single.to_dict())
        data_single.vote = vote

        # after = str(data_single.to_dict())
        # writeaudit(data_single.id, before, after)
        db.session.commit()

        print('vote={0}', vote)
    else:
        print('invalid vote={0}', vote)
    # return redirect(url_for('.view', id=`id`))
    return redirect(request.referrer)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
# @login_required
def view(id):
    global player_lastpage
    global history_lastpage

    form = HistoryForm()
    data_single = User.query.filter_by(id=current_user.id).first_or_404()
    data_single.current_session_id = id
    db.session.commit()

    playerpage = request.args.get('playerpage', player_lastpage, type=int)
    player_lastpage = playerpage

    historypage = request.args.get('historypage', history_lastpage, type=int)
    history_lastpage = historypage

    data_single = Session.query.filter_by(id=id).first_or_404()

    playerlist = User.query.filter_by(current_session_id=data_single.id).paginate(playerpage,
                    current_app.config['ROWS_PER_PAGE_FILTER'], False)

    player_next_url = url_for('.view', id=id, playerpage=playerlist.next_num,
                                historypage=historypage) if playerlist.has_next else None

    player_prev_url = url_for('.view', id=id, playerpage=playerlist.prev_num,
                                historypage=historypage) if playerlist.has_prev else None

    historylist = History.query.filter_by(session_id=data_single.id).paginate(historypage,
                    current_app.config['ROWS_PER_PAGE_FILTER'], False)

    history_next_url = url_for('.view', id=id, historypage=historylist.next_num,
                           playerpage=playerpage) if historylist.has_next else None

    history_prev_url = url_for('.view', id=id, historypage=historylist.prev_num,
                           playerpage=playerpage) if historylist.has_prev else None

    return render_template('main/view.html', datasingle=data_single, 
        playerlist=playerlist.items, player_next_url=player_next_url, player_prev_url=player_prev_url,
        historylist=historylist.items,  history_next_url=history_next_url,  history_prev_url=history_prev_url,
        form=form)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
# @login_required
def edit(id):
    form = SessionForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Session.query.filter_by(id=id).first_or_404()
        # before = str(data_single.to_dict())
        data_single.name = request.form['name']
        data_single.is_active = 'is_active' in request.form

        # after = str(data_single.to_dict())
        # writeaudit(data_single.id, before, after)
        db.session.commit()
        return redirect(url_for('.view', id=data_single.id))

    if request.method == 'GET':
        data_single = Session.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('main/edit.html', form=form)


@bp.route('/delete/<int:id>', methods=["GET", "POST"])
# @login_required
def delete(id):
    Session.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('.list'))


def writeaudit(parent_id, before, after):
    if before:
        change = "change"
    else:
        change = "add"
    var = Audit(model='session',
                parent_id=parent_id,
                a_datetime=datetime.now(),
                a_user_id=current_user.id,
                a_username=load_user(current_user.id).username,
                action=change,
                before=before,
                after=after
                )

    db.session.add(var)
