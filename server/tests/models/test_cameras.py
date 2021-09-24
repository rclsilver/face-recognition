from app.models.cameras import Camera


def test_full_url_without_credentials():
    camera = Camera()
    camera.url = 'http://example.com/live'
    assert camera.full_url == 'http://example.com/live'

def test_full_url_with_username():
    camera = Camera()
    camera.url = 'http://example.com/live'
    camera.username = 'my-username'
    assert camera.full_url == 'http://my-username:@example.com/live'

def test_full_url_with_password():
    camera = Camera()
    camera.url = 'http://example.com/live'
    camera.password = 'my-password'
    assert camera.full_url == 'http://:my-password@example.com/live'

def test_full_url_with_both_username_and_password():
    camera = Camera()
    camera.url = 'http://example.com/live'
    camera.username = 'my-username'
    camera.password = 'my-password'
    assert camera.full_url == 'http://my-username:my-password@example.com/live'
