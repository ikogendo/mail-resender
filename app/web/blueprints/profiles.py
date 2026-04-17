from flask import Blueprint, flash, redirect, render_template, url_for

from ...extensions import db
from ...forms import ProfileForm
from ...models import Profile

bp = Blueprint("profiles", __name__, url_prefix="/profiles")


@bp.get("/")
def list_profiles():
    profiles = Profile.query.order_by(Profile.id.desc()).all()
    return render_template("profiles/list.html", profiles=profiles)


@bp.route("/new", methods=["GET", "POST"])
def create_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        profile = Profile(name=form.name.data, is_active=form.is_active.data)
        db.session.add(profile)
        db.session.commit()
        flash("Profile created", "success")
        return redirect(url_for("profiles.list_profiles"))
    return render_template("profiles/form.html", form=form, page_title="Create profile")


@bp.route("/<int:profile_id>/edit", methods=["GET", "POST"])
def edit_profile(profile_id: int):
    profile = Profile.query.get_or_404(profile_id)
    form = ProfileForm(obj=profile)
    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        flash("Profile updated", "success")
        return redirect(url_for("profiles.list_profiles"))
    return render_template("profiles/form.html", form=form, page_title=f"Edit profile #{profile.id}")
