from . import bp

@bp.route("/")
def index():
    return "CVEScout web UI online"
