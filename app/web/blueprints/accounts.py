from flask import Blueprint, flash, redirect, render_template, url_for

from ...extensions import db
from ...forms import MailAccountForm
from ...models import MailAccount

bp = Blueprint("accounts", __name__, url_prefix="/accounts")


@bp.get("/")
def list_accounts():
    accounts = MailAccount.query.order_by(MailAccount.id.desc()).all()
    return render_template("accounts/list.html", accounts=accounts)


@bp.route("/new", methods=["GET", "POST"])
def create_account():
    form = MailAccountForm()
    if form.validate_on_submit():
        account = MailAccount()
        form.populate_obj(account)
        db.session.add(account)
        db.session.commit()
        flash("Mail account created", "success")
        return redirect(url_for("accounts.list_accounts"))
    return render_template("accounts/form.html", form=form, page_title="Create mail account")


@bp.route("/<int:account_id>/edit", methods=["GET", "POST"])
def edit_account(account_id: int):
    account = MailAccount.query.get_or_404(account_id)
    form = MailAccountForm(obj=account)
    if form.validate_on_submit():
        form.populate_obj(account)
        db.session.commit()
        flash("Mail account updated", "success")
        return redirect(url_for("accounts.list_accounts"))
    return render_template("accounts/form.html", form=form, page_title=f"Edit account #{account.id}")
