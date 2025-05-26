from flask import Blueprint, render_template, request, redirect, url_for
from helloSecurity import db
from helloSecurity.models import Restaurant, Tag, RestaurantTag, TagCategory
from sqlalchemy import func, distinct
from datetime import time

# ✅ Blueprint 한 번만 선언
bp = Blueprint("restaurants", __name__, url_prefix="/")

# ✅ 메인 페이지: 태그 필터링 및 맛집 리스트 출력
@bp.route("/", methods=["GET"])
def index():
    MIN_RATING = 4

    high_rated = (Restaurant.query
                    .filter(Restaurant.rating >= MIN_RATING)
                    .order_by(Restaurant.id.desc())
                    .all())

    tag_ids = request.args.getlist("tags", type=int)
    search_q = Restaurant.query

    if tag_ids:
        search_q = (search_q.join(RestaurantTag)
                             .filter(RestaurantTag.tag_id.in_(tag_ids))
                             .group_by(Restaurant.id)
                             .having(func.count(distinct(RestaurantTag.tag_id)) == len(tag_ids))
                   )

    restaurants = search_q.order_by(Restaurant.id.desc()).all()
    categories = TagCategory.query.order_by(TagCategory.id).all()

    return render_template("restaurants/main.html",
                           restaurants=restaurants,
                           categories=categories,
                           filtered=high_rated,
                           selected=set(tag_ids))

# ✅ 상세 페이지
@bp.route("/<int:r_id>")
def detail(r_id):
    r = Restaurant.query.get_or_404(r_id)
    return render_template("restaurants/detail.html", restaurant=r)

# ✅ 생성 페이지
@bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        start_time = time.fromisoformat(request.form["start_hour"])
        end_time   = time.fromisoformat(request.form["end_hour"])

        r = Restaurant(
            name = request.form["name"],
            address=request.form["address"],
            description=request.form["description"],
            rating=int(request.form["rating"]),
            start_hour=start_time,
            end_hour=end_time,
            break_time=request.form["breaktime"]
        )

        db.session.add(r)     
        db.session.flush()

        tag_ids = map(int, request.form.getlist("tags"))
        db.session.add_all(
            [RestaurantTag(restaurant_id=r.id, tag_id=tid) for tid in tag_ids]
        )                      

        db.session.commit()
        return redirect(url_for("restaurants.index"))

    categories = TagCategory.query.order_by(TagCategory.id).all()
    return render_template("restaurants/create.html",
                           tags=[],
                           categories=categories)

# ✅ 수정 페이지
@bp.route("/<int:r_id>/edit", methods=["GET", "POST"])
def edit(r_id):
    r = Restaurant.query.get_or_404(r_id)

    if request.method == "POST":
        start_time = time.fromisoformat(request.form["start_hour"])
        end_time   = time.fromisoformat(request.form["end_hour"])

        r.name = request.form["name"]
        r.address = request.form["address"]
        r.description = request.form["description"]
        r.rating = request.form['rating']
        r.start_hour = start_time
        r.end_hour = end_time
        r.break_time = request.form['breaktime']

        RestaurantTag.query.filter_by(restaurant_id=r.id).delete()
        for tag_id in request.form.getlist("tags"):
            db.session.add(RestaurantTag(
                restaurant_id=r.id,
                tag_id=int(tag_id)
            ))

        db.session.commit()
        return redirect(url_for("restaurants.index"))

    categories = TagCategory.query.order_by(TagCategory.id).all()
    attached = {rel.tag_id for rel in r.tags}
    return render_template("restaurants/create.html",
                           restaurant=r,
                           categories=categories,
                           attached=attached)

# ✅ 삭제 기능
@bp.route("/<int:r_id>/delete", methods=["POST"])
def delete(r_id):
    r = Restaurant.query.get_or_404(r_id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for("restaurants.index"))
