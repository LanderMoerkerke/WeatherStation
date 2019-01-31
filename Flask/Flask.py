print('Script Weatherstationn')
import os, datetime
from flask import Flask, render_template, redirect, request, url_for, session

print(str(datetime.datetime.now()))

from Database.DbClass import DbClass
# from Database.pwdhash import verify_credentials
from RecordData import RecordData

app = Flask(__name__)
app.secret_key = "(Project 1 Howest Kortrijk Moerkerke)String"

# database
database = DbClass()

# session config
@app.before_first_request
def startup():
    session.permanent = False
    app.permanent_session_lifetime = datetime.timedelta(minutes=10)
    session.setdefault('username', None)
    session.setdefault('kleurcode', '2196f3')


@app.context_processor
def geefKleurcodeMee():
    # default kleurcode ingeven
    if 'kleurcode' not in session.keys():
        session['kleurcode'] = '2196f3'
    # kleurcode meegeven
    return dict(kleurcode=session['kleurcode'])

@app.route('/', methods=['GET', 'POST'])
def onboarding():
    if 'username' in session.keys():
        if session['username'] != None:
            return redirect(url_for('homepage'))

    # passwoorden hashen, sha2 op de database
    gebruikers = database.getUsers()

    error = None

    if request.method == 'POST':
        inlogGegevensJuist = False

        # gegevens uit de textbox halen
        gebruikersNaam = request.form['username']
        gebruikersWachtwoord = request.form['password']

        for gebruiker in gebruikers:
            if gebruiker[0] == gebruikersNaam and gebruiker[1] == gebruikersWachtwoord and inlogGegevensJuist == False:
                # session invoegen
                session['username'] = gebruikersNaam
                session['password'] = gebruikersWachtwoord
                session['kleurcode'] = database.getColorByLogin(gebruikersNaam)[0]

                inlogGegevensJuist = True

        if inlogGegevensJuist:
            return redirect(url_for('homepage'))
        else:
            error = 'Gebruikersnaam of wachtword is verkeerd. Gelieve opnieuw te proberen.'
    return render_template('index.html', error=error)


@app.route('/home')
def homepage():
    if checkSessie():
        return redirect(url_for('onboarding'))

    gegevensData = database.gemiddeldeGegevensPerDag()[-1]
    gegevensWeerstation = database.getWeerstations()

    return render_template('homepage.html', username=session['username'], gegevensData=gegevensData,
                           gegevensWeerstation=gegevensWeerstation)


@app.route('/activeerweerstation/<weerstationID>')
def activeerweerstation(weerstationID):
    error = None

    weerstation = database.getWeerstationByID(weerstationID)
    if weerstation == None:
        # error krijgen (internal error)
        pass

    # script starten
    try:
        recordData = RecordData(weerstationID)
        recordData.CapturePeriodically()
    except:
        # wanneer script niet kan starten (try except) geef ID -1 door
        print('script niet kunnen starten')
        error = 'het weerstation kon niet worden gestart'

    if error == None:
        # wijzig database weerstation (datumActief, actief)
        database.updateWeerstationActiveByID(weerstationID)

    return render_template('activeerweerstation.html', weerstation=weerstation, error=error)


@app.route('/deactiveerweerstation/<weerstationID>')
def deactiveerweerstation(weerstationID):
    error = None

    weerstation = database.getWeerstationByID(weerstationID)
    database.updateWeerstationInactiveByID(weerstationID)
    if weerstation == None:
        # error krijgen (internal error)
        pass

    # wijzig database weerstation (datumActief, actief)

    # script starten

    # wanneer script niet kan starten (try except) geef ID -1 door

    return render_template('deactiveerweerstation.html', weerstation=weerstation, error=error)

@app.route('/gegevens')
def gegevens():
    if checkSessie():
        return redirect(url_for('onboarding'))
    gegevens = database.getGegevens()
    return render_template('gegevens.html', gegevens=gegevens, gezocht=False)


@app.route('/gegevens/grafiek/')
def gegevensGrafiek():
    if checkSessie():
        return redirect(url_for('onboarding'))

    gegevens = database.gemiddeldeGegevensPerDag()
    return render_template('grafiek.html', gegevens=gegevens)


@app.route('/zoeken', methods=['GET', 'POST'])
def zoeken():
    if checkSessie():
        return redirect(url_for('onboarding'))

    minMax = database.getMinMaxDatumZoekGegevens()
    return render_template('zoeken.html', minMax=minMax)


@app.route('/zoeken/gegevens/')
def zoekenGegevens():
    if checkSessie():
        return redirect(url_for('onboarding'))

    maxDate = database.getMinMaxDatumZoekGegevens()[1]

    # gegevens uit de url halen
    bar = request.args.to_dict()

    # wanneer de gebruiker geen einddatum heeft ingesteld dan w
    if bar['eind'] == '':
        bar['eind'] = maxDate

    gegevens = database.getGegevensBetweenDates(bar['start'], bar['eind'])
    return render_template('gegevens.html', gegevens=gegevens, gezocht=True, bar=bar)


@app.route('/zoeken/grafiek/<begin><eind>')
def zoekenGrafiek(begin, eind):
    if checkSessie():
        return redirect(url_for('onboarding'))

    gegevens = database.gemiddeldeGegevensPerDag()
    return render_template('grafiek.html', gegevens=gegevens)


@app.route('/instellingen', methods=['GET', 'POST'])
def instellingen():
    if checkSessie():
        return redirect(url_for('onboarding'))

    kleuren = database.getColors()

    informatieWachtwoord = None
    informatieKleuren = None

    if request.method == 'POST':
        # WACHTWOORD wijzigen
        oud = request.form.get('oudwachtwoord')
        nieuw = request.form.get('nieuwwachtwoord')
        bevestig = request.form.get('bevestigwachtwoord')

        # check of de de sectie wachtwoorden zijn ingevuld
        if oud != "" and nieuw != "" and bevestig != "":
            # oud = bestaand
            if session['password'] == oud:
                # bevestig == nieuw --> update wachtwoord
                if bevestig == nieuw:
                    database.changePasswordByName(session['username'], nieuw)
                    # update session
                    session['password'] = nieuw
                    informatieWachtwoord = "Succes, het wachtwoord is gewijzigd"
                else:
                    informatieWachtwoord = "ERROR: Gelieve hetzelfde wachtwoord correct te herhalen in het bevestingsvak."
            else:
                informatieWachtwoord = "ERROR: Gelieve het oud wachtwoord juist in te geven"

        # KLEUR accent wijzigen
        kleurCode = request.form.get('kleuren')
        # check of de de sectie kleuren zijn ingevuld
        if kleurCode != None:
            # update instellingen
            database.updateSettingsColor(kleurCode, session['username'])
            session['kleurcode'] = kleurCode
            informatieKleuren = "Succes, het accentkleur is gewijzigd"

            # if session['password'] == oud:
            #     # update wachtwoord
            #     pass
            #     return redirect(url_for('homepage'))
            # else:
            #     error = 'Wachtwoord klopt niet.'

    return render_template('instellingen.html', kleuren=kleuren, informatieWachtwoord=informatieWachtwoord,
                           informatieKleuren=informatieKleuren)


@app.route('/instellingen/melding')
def melding():
    if checkSessie():
        return redirect(url_for('onboarding'))

    return render_template('melding.html')


@app.route('/checkingelogd')
def checkingelogd():
    if 'username' in session.keys():
        if session['username'] != None:
            username = session['username']
            return 'Ingelogd als ' + username + '<br>' + \
                   "<b><a href = '/logout'>klik hier om uit te loggen</a></b>"
    return "Je bent niet ingelogd <br><a href = '/'></b>" + \
           "klik hier om in te loggen.</b></a>"


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session['username'] = None
    session['kleurcode'] = '2196f3'
    return redirect(url_for('onboarding'))

# errorhandlers
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error/404.html', error=error)


@app.errorhandler(500)
def internalError(error):
    return render_template('error/505.html', error=error)

def checkSessie():
    if 'username' in session.keys():
        if session['username'] == None:
            return True
        return False
    return True

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True)