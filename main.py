import datetime
import google.oauth2.id_token
import random
from flask import Flask, render_template, url_for, request, redirect
from google.cloud import datastore
from google.auth.transport import requests

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserDetail', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

def createUserInfo(claims):
    entity_key = datastore_client.key('UserDetail', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'creation_date': datetime.datetime.now()        
    })

    datastore_client.put(entity)

def createDriverInfo(name, age, totalPoles, totalRaceWins, totalPoints, totalWorldTitles, totalFastestLaps, team):
    id = random.getrandbits(63)

    entity_key = datastore_client.key('DriverInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'age': age,
        'totalPoles': totalPoles,
        'totalRaceWins': totalRaceWins,
        'totalPoints': totalPoints,
        'totalWorldTitles': totalWorldTitles,
        'totalFastestLaps': totalFastestLaps,
        'team': team
    })
    datastore_client.put(entity)
    return entity


def deleteDriverInfo(id):
    driver_info_key = datastore_client.key('DriverInfo', id)
    driver_entity = datastore_client.get(driver_info_key)

    team_entity = getTeamByName(driver_entity['team'])
    teamDriverList = team_entity['driver_list']

    print('geldi 1')
    if driver_entity in teamDriverList:
        teamDriverList.remove(driver_entity)
        print("geldi2")
    team_entity.update({
        'driver_list': teamDriverList
    })
    datastore_client.delete(driver_info_key)
    datastore_client.put(team_entity)

def createTeamInfo(name, yearFounded, teamPolePositions, teamRaceWins, teamTotalTitles, lastYearPosition):
    id = random.getrandbits(63)

    entity_key = datastore_client.key('TeamInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'yearFounded': yearFounded,
        'teamPolePositions': teamPolePositions,
        'teamRaceWins': teamRaceWins,
        'teamTotalTitles': teamTotalTitles,
        'lastYearPosition': lastYearPosition,
        'driver_list': []
    })

    datastore_client.put(entity)

def updateDriverInfo(id, name, age, totalPoles, totalRaceWins, totalPoints, totalWorldTitles, totalFastestLaps, team):
    print(id,name,age,totalPoles,totalRaceWins,totalPoints,totalWorldTitles,totalFastestLaps,team)

    entity_key = datastore_client.key('DriverInfo', id)
    entity = datastore_client.get(entity_key)
    entity.update({
        'name': name,
        'age': age,
        'totalPoles': totalPoles,
        'totalRaceWins': totalRaceWins,
        'totalPoints': totalPoints,
        'totalWorldTitles': totalWorldTitles,
        'totalFastestLaps': totalFastestLaps,
        'team': team
    })
    datastore_client.put(entity)


def updateTeamInfo(id, name, yearFounded, teamPolePositions, teamRaceWins, teamTotalTitles, lastYearPosition):
    entity_key = datastore_client.key('TeamInfo', id)
    entity = datastore_client.get(entity_key)
    entity.update({
        'name': name,
        'yearFounded': yearFounded,
        'teamPolePositions': teamPolePositions,
        'teamRaceWins': teamRaceWins,
        'teamTotalTitles': teamTotalTitles,
        'lastYearPosition': lastYearPosition
    })
    datastore_client.put(entity)

def deleteTeamInfo(id):
    team_info_key = datastore_client.key('TeamInfo', id)
    datastore_client.delete(team_info_key)

def getAllDrivers():
    query = datastore_client.query(kind='DriverInfo')
    result = list(query.fetch())

    return result

def getAllTeams():
    query = datastore_client.query(kind='TeamInfo')
    result = list(query.fetch())

    return result

def getTeamByName(name):
    query = datastore_client.query(kind='TeamInfo')
    query.add_filter('name', '=', name)
    result = list(query.fetch())
    return result[0]

def getTeamIdByName(name):
    query = datastore_client.query(kind='TeamInfo')
    query.add_filter('name', '=', name)
    result = list(query.fetch())[0].id
    return result

def getTeamById(id):
    entity_key = datastore_client.key('TeamInfo', id)
    entity = datastore_client.get(entity_key)
    return entity


def getDriverByName(name):
    query = datastore_client.query(kind='DriverInfo')
    query.add_filter('name', '=', name)
    result = list(query.fetch())
    return result[0]

def getDriverById(id):
    entity_key = datastore_client.key('DriverInfo', id)
    entity = datastore_client.get(entity_key)
    return entity

def addDriverToTeam(team_info, driver_entity):
    driverList = team_info['driver_list']
    driverList.append(driver_entity)
    team_info.update({
        'driver_list': driverList
    })
    datastore_client.put(team_info)


def updateTeamsDriverList(driver_entity, new_team_string):
    oldTeamEntity = getTeamByName(driver_entity['team'])
    oldTeamDriverList = oldTeamEntity['driver_list']
    if driver_entity in oldTeamDriverList:
        oldTeamDriverList.remove(driver_entity)
    oldTeamEntity.update({
        'driver_list': oldTeamDriverList
    })
    datastore_client.put(oldTeamEntity)

    newTeamEntity = getTeamByName(new_team_string)
    newTeamDriverList = newTeamEntity['driver_list']
    newTeamDriverList.append(driver_entity)
    newTeamEntity.update({
        'driver_list': newTeamDriverList
    })
    datastore_client.put(newTeamEntity)

def checkTeamNameInDatastore(team_name):
    teamNameList = []
    teams = getAllTeams()
    for team in teams:
        teamNameList.append(team['name'])

    if team_name in teamNameList:
        return True
    else:
        return False

def checkDriverNameInDatastore(driver_name):
    driverNameList = []
    drivers = getAllDrivers()
    for driver in drivers:
        driverNameList.append(driver['name'])

    if driver_name in driverNameList:
        return True
    else:
        return False

@app.route("/driverList", methods=['GET', 'POST'])
def driverList():
    id_token = request.cookies.get("token")
    error_message = None
    result = None

    if request.method == "POST":
        try:
            if id_token:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            else:
                claims = None
            query = datastore_client.query(kind='DriverInfo')
            if request.form['name']:
                query.add_filter('name', '=', str(request.form['name']))
            if request.form['age']:
                query = query.add_filter('age', '>=', int(request.form['age']))
            if request.form['totalPoles']:
                query = query.add_filter('totalPoles', '>=', int(request.form['totalPoles']))
            if request.form['totalRaceWins']:
                query.add_filter('totalRaceWins', '>=', int(request.form['totalRaceWins']))
            if request.form['totalPoints']:
                query.add_filter('totalPoints', '>=', int(request.form['totalPoints']))
            if request.form['totalWorldTitles']:
                query.add_filter('totalWorldTitles', '>=', int(request.form['totalWorldTitles']))
            if request.form['totalFastestLaps']:
                query.add_filter('totalFastestLaps', '>=', int(request.form['totalFastestLaps']))
            if request.form['team']:
                query.add_filter('team', '=', str(request.form['team']))
            result = list(query.fetch())
            return render_template('driverList.html', user_details=claims, error_message=error_message, drivers=result)
        except ValueError as exc:
            error_message = str(exc)
    else:
        try:
            if id_token:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            else:
                claims = None
            result = getAllDrivers()
        except ValueError as exc:
            error_message = str(exc)
        return render_template("driverList.html", user_details=claims, error_message=error_message, drivers = result)

@app.route("/teamList", methods=['GET', 'POST'])
def teamList():
    id_token = request.cookies.get("token")
    error_message = None
    result = None

    if request.method == "POST":
        try:
            if id_token:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            else:
                claims = None
            query = datastore_client.query(kind='TeamInfo')
            if request.form['name']:
                query.add_filter('name', '=', str(request.form['name']))
            if request.form['yearFounded']:
                query.add_filter('yearFounded', '>=', int(request.form['yearFounded']))
            if request.form['teamPolePositions']:
                query.add_filter('teamPolePositions', '>=', int(request.form['teamPolePositions']))
            if request.form['teamRaceWins']:
                query.add_filter('teamRaceWins', '>=', int(request.form['teamRaceWins']))
            if request.form['teamTotalTitles']:
                query.add_filter('teamTotalTitles', '>=', int(request.form['teamTotalTitles']))
            if request.form['lastYearPosition']:
                query.add_filter('lastYearPosition', '<=', int(request.form['lastYearPosition']))

            result = list(query.fetch())
            return render_template('teamList.html', user_details=claims, error_message=error_message, teams=result)

        except ValueError as exc:
            error_message = str(exc)
    else:
        try:
            if id_token:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            else:
                claims = None
            result = getAllTeams()
        except ValueError as exc:
            error_message = str(exc)
        return render_template('teamList.html', user_details=claims, error_message=error_message, teams = result)


@app.route("/add_driver", methods=['GET', 'POST'])
def add_driver():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    driver_entity = None
    team_entity = None

    if request.method == "POST" and id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            if request.form['name']:
                isNameExist = checkDriverNameInDatastore(request.form['name'])
                if isNameExist:
                    raise Exception("Sorry, the driver name is already exist!")
                else:
                    if request.form['team'] != "":
                        team_entity = getTeamByName(request.form['team'])
                        driver_entity = createDriverInfo(request.form['name'], int(request.form['age']), int(request.form['totalPoles']), int(request.form['totalRaceWins']), int(request.form['totalPoints']), int(request.form['totalWorldTitles']), int(request.form['totalFastestLaps']), request.form['team'])
                        addDriverToTeam(team_entity, driver_entity)
                    else:
                        driver_entity = createDriverInfo(request.form['name'], int(request.form['age']), int(request.form['totalPoles']), int(request.form['totalRaceWins']), int(request.form['totalPoints']), int(request.form['totalWorldTitles']), int(request.form['totalFastestLaps']), "")
        except ValueError as exc:
            error_message = str(exc)
        return redirect(url_for('driverList'))

    else:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            teams = getAllTeams()
        except ValueError as exc:
            error_message = str(exc)
        return render_template("add_driver.html", user_details=claims, error_message=error_message, teams = teams)

@app.route("/add_team", methods=['GET', 'POST'])
def add_team():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    driver_info = None
    team_info = None

    if request.method == "POST" and id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            if request.form['name']:
                isNameExist = checkTeamNameInDatastore(request.form['name'])
                if isNameExist:
                    raise Exception("Sorry, the team name is already exist!")
                else:
                    createTeamInfo(request.form['name'], int(request.form['yearFounded']), int(request.form['teamPolePositions']), int(request.form['teamRaceWins']), int(request.form['teamTotalTitles']), int(request.form['lastYearPosition']))

        except ValueError as exc:
            error_message = str(exc)
        return redirect(url_for('teamList'))

    else:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

        return render_template("add_team.html", user_details=claims, error_message=error_message)


@app.route('/driver_info<int:id>')
def driver_info_page(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    teams = getAllTeams()

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    entity_key = datastore_client.key('DriverInfo', id)
    result = datastore_client.get(entity_key)
    return render_template('driver_info.html', user_details=claims, driver=result, teams = teams, id=id)

@app.route('/edit_driver_info/<int:id>', methods=['POST'])
def editDriverInfo(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    driver_entity = getDriverById(id)
    oldTeamName = driver_entity['team']

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            if request.form['name_update']:
                isNameExist = checkDriverNameInDatastore(request.form['name_update'])
                if isNameExist:
                    raise Exception("Sorry, the driver name is already exist!")
                else:
                    new_driverName = request.form['name_update']
            else:
                new_driverName = driver_entity['name']

            if request.form['age_update']:
                new_age = int(request.form['age_update'])
            else:
                new_age = driver_entity['age']

            if request.form['totalPolePositions_update']:
                new_totalPolePositions = int(request.form['totalPolePositions_update'])
            else:
                new_totalPolePositions = driver_entity['totalPoles']

            if request.form['totalRaceWins_update']:
                new_totalRaceWins = int(request.form['totalRaceWins_update'])
            else:
                new_totalRaceWins = driver_entity['totalRaceWins']

            if request.form['totalPoints_update']:
                new_totalPoints = int(request.form['totalPoints_update'])
            else:
                new_totalPoints = driver_entity['totalPoints']

            if request.form['totalWorldTitles_update']:
                new_totalWorldTitles = int(request.form['totalWorldTitles_update'])
            else:
                new_totalWorldTitles = driver_entity['totalWorldTitles']

            if request.form['totalFastestLaps_update']:
                new_totalFastestLaps = int(request.form['totalFastestLaps_update'])
            else:
                new_totalFastestLaps = driver_entity['totalFastestLaps']

            if request.form.get('team_update') != oldTeamName:
                new_driverTeam = request.form.get('team_update')
                updateTeamsDriverList(driver_entity, new_driverTeam)
            else:
                new_driverTeam = driver_entity['team']

            updateDriverInfo(id, new_driverName, new_age, new_totalPolePositions, new_totalRaceWins, new_totalPoints, new_totalWorldTitles, new_totalFastestLaps, new_driverTeam)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('driverList'))


@app.route('/edit_team_info/<int:id>', methods=['POST'])
def editTeamInfo(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    team_entity = getTeamById(id)

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            if request.form['name_update']:
                isNameExist = checkTeamNameInDatastore(request.form['name_update'])
                if isNameExist:
                    raise Exception("Sorry, the team name is already exist!")
                else:
                    new_teamName = request.form['name_update']
            else:
                new_teamName = team_entity['name']

            if request.form['yearFounded_update']:
                new_yearFounded = int(request.form['yearFounded_update'])
            else:
                new_yearFounded = team_entity['yearFounded']

            if request.form['teamPolePositions_update']:
                new_teamPolePositions = int(request.form['teamPolePositions_update'])
            else:
                new_teamPolePositions = team_entity['teamPolePositions']

            if request.form['teamRaceWins_update']:
                new_teamRaceWins = int(request.form['teamRaceWins_update'])
            else:
                new_teamRaceWins = team_entity['teamRaceWins']

            if request.form['teamTotalTitles_update']:
                new_totalConstructorsTitles = int(request.form['teamTotalTitles_update'])
            else:
                new_totalConstructorsTitles = team_entity['teamTotalTitles']

            if request.form['lastYearPosition_update']:
                new_lastYearPositions = int(request.form['lastYearPosition_update'])
            else:
                new_lastYearPositions = team_entity['lastYearPosition']

            updateTeamInfo(id, new_teamName, new_yearFounded, new_teamPolePositions, new_teamRaceWins, new_totalConstructorsTitles, new_lastYearPositions)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('teamList'))


@app.route('/team_info<int:id>')
def team_info_page(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    entity_key = datastore_client.key('TeamInfo', id)
    result = datastore_client.get(entity_key)

    return render_template('team_info.html', user_details=claims, team=result, id=id)



@app.route('/delete_team_info/<int:id>', methods=['POST'])
def delete_team_info(id):
    id_token = request.cookies.get("token")
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            deleteTeamInfo(id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/teamList')

@app.route('/delete_driver_info/<int:id>', methods=['POST'])
def delete_driver_info(id):
    id_token = request.cookies.get("token")
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            deleteDriverInfo(id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/driverList')

@app.route("/compare", methods=['GET'])
def compare():
    id_token = request.cookies.get("token")
    error_message = None
    teams = getAllTeams()
    drivers = getAllDrivers()

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('compare.html', user_details=claims, error_message=error_message, drivers = drivers, teams = teams)

@app.route("/compare_teams", methods=['POST'])
def compare_teams():
    id_token = request.cookies.get("token")
    error_message = None
    team1 = getTeamByName(request.form['team1'])
    team2 = getTeamByName(request.form['team2'])

    if id_token and (team1 != team2):
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
        return render_template('compare_teams.html', user_details=claims, error_message=error_message, first_team = team1, second_team = team2)
    else:
        raise ValueError("Please Choose Different Teams!")
        return redirect(url_for('compare'))

@app.route("/compare_drivers", methods=['POST'])
def compare_drivers():
    id_token = request.cookies.get("token")
    error_message = None
    driver1 = getDriverByName(request.form['driver1'])
    driver2 = getDriverByName(request.form['driver2'])

    if id_token and (driver1 != driver2):
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
        return render_template('compare_drivers.html', user_details=claims, error_message=error_message, first_driver = driver1, second_driver = driver2)
    else:
        raise ValueError("Please Choose Different Drivers!")
        return redirect(url_for('compare'))

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_details = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('index.html', user_details=claims, error_message=error_message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
