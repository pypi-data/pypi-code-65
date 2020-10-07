from flask_login_dictabase_blueprint import GetUser, admins

menu = []


def GetMenu(active=None):
    m = menu.copy()

    for item in m:
        item['active'] = item['title'] == active

    user = GetUser()
    if user:
        m.append(dict(title='Logout', url='/logout', active=False))
    else:
        m.append(dict(title='Login', url='/login', active=False))
        m.append(dict(title='Sign Up', url='/register', active=False))

    # remove admin menu options if user is not admin
    if user is None or user['email'] not in admins:
        for item in m.copy():
            if item.get('adminOnly', False):
                m.remove(item)

    return m


def AddMenuOption(title, url, adminOnly=False):
    global menu
    item = dict(title=title, url=url, active=False, adminOnly=adminOnly)
    menu.append(item)
    menu = sorted(menu, key=lambda i: i['title'].upper())


def Setup(app):
    pass
