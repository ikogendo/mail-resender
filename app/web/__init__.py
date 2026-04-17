from .blueprints.accounts import bp as accounts_bp
from .blueprints.channels import bp as channels_bp
from .blueprints.events import bp as events_bp
from .blueprints.profiles import bp as profiles_bp
from .blueprints.status import bp as status_bp
from .blueprints.test_send import bp as test_send_bp


BLUEPRINTS = [profiles_bp, accounts_bp, channels_bp, status_bp, events_bp, test_send_bp]
