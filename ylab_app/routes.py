from ylab_app.views import index, login, logout, transfer, signup


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')
    app.router.add_get('/signup', signup, name='signup')
    app.router.add_post('/signup', signup, name='signup')
    app.router.add_get('/transfer', transfer, name='transfer')
    app.router.add_post('/transfer', transfer, name='transfer')
