import sys

def inject_default_settings(name):
    '''
    Inject application default settings into config if not
    already defined.
    '''
    try:
        __import__('%s.settings' % name)

        # Import this app defaults
        app_settings = sys.modules['%s.settings' % name]
        default_settings = sys.modules['django.conf.global_settings']
        settings = sys.modules['django.conf'].settings

        # Get our defaults
        for k in dir(app_settings):
            if k.isupper():
                # Add to Django defaults
                setattr(default_settings, k, getattr(app_settings, k))

                # Add to settings if not defined
                if not hasattr(settings, k):
                    setattr(settings, k, getattr(app_settings, k))

    except ImportError:
        # Skip failures
        pass

inject_default_settings(__name__)
