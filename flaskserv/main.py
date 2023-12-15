from flask import Flask, render_template, request
from mpmath import *
from waitress import serve
from datetime import datetime, timedelta
from time import strptime
import json

#test comment

def taufromdate(datestr):
    mp.dps = 20
    yearnum = 0
    monthnum = 0
    daynum = 0
    try:
        timeobj = strptime(datestr, "%m/%d/%y")
        yearnum = timeobj.tm_year
        monthnum = timeobj.tm_mon
        daynum = timeobj.tm_mday
    except ValueError:
        return None
    #intervalobj = datetime(yearnum, monthnum, daynum, 16, 30, 0) - datetime.now()
    #16 + 6 is for CST timezone to UTC, since this machine is in UTC
    intervalsec = mpmathify(datetime(yearnum, monthnum, daynum, 16+6, 30, 0).timestamp()) - mpmathify(datetime.now().timestamp())
    #tauyear = mpmathify(intervalobj.total_seconds())/(60*60*24*365)
    tauyear = intervalsec/(60*60*24*365)
    #print("with more accurate year: %s" % nstr(tauyear*(365)/(365.25), n=15))
    #print("Seconds number: %s" % str(intervalobj.total_seconds()))
    print("Seconds interval: %s" % nstr(intervalsec, n=15))
    return tauyear

def costval():
    return

def putval():
    return

def charmcalc_annual(S, tau, K, r, sigma):
    mp.dps = 20
    charmcalc = 0
    variancevar = power(sigma, 2)
    numerfirst = power(S/K, -(r/variancevar) - 1/2)
    numersecond = tau*(2*r + variancevar) - 2*log(S/K)
    expfactor = -(4*power(log(S/K),2)+power(tau*(2*r+variancevar), 2))/(8*variancevar*tau)
    denom = 4*sqrt(2*pi)*sigma*power(tau, 3/2)
    charmcalc = -1*(numerfirst * numersecond * exp(expfactor))/(denom)
    return charmcalc

app = Flask(__name__)

@app.route('/script.py')
def hello():
	return "<html><body><h1>Test!</h1></body></html>"

@app.route('/risk.py')
def riskpage():
    return render_template('riskslider.html')

@app.route('/valuecalc.py')
def valuecalcpage():
    return

@app.route('/script/charmcalc.py')
def charmcalcsimple():
    vinput = request.args
    try:
        expdate = vinput["date"]
        taures = taufromdate(expdate)
        charmval_ann = charmcalc_annual(mpmathify(vinput["S"]), taures, mpmathify(vinput["K"]), mpmathify(vinput["r"])/100, mpmathify(vinput["sigma"])/100)
        #error logging
        for item in vinput:
            print(vinput[item])
        print("Years num: %s\n\n" % nstr(taures, n=15))
        #end of error logging
        return '{"Charm_Annual": %s, "Charm_Daily": %s}' % (nstr(charmval_ann, n=15), nstr(charmval_ann/365, n=15))
    except (KeyError, TypeError) as err:
        return "Parameters entered incorrectly %s" % err.args[0], 400

def InversePhi(x):
    mp.dps = 20
    return sqrt(2) * erfinv(2*x - 1)

def vannavalue(Deltaval, tau, sigma, IsPut):
    mp.dps = 20
    vanna = 0
    d1val = 0
    if IsPut is True:
        d1val = InversePhi(Deltaval + 1)
    elif IsPut is False:
        d1val = InversePhi(Deltaval)
    d2val = d1val - sigma*sqrt(tau)
    vanna = -1*(d2val/sigma)*npdf(d1val)
    return vanna

@app.route('/script/vannacalc.py')
def vannacalcsimple():
    vinput = request.args
    try:
        expdate = vinput["date"]
        taures = taufromdate(expdate)
        thedelta = mpmathify(vinput["Delta"])
        vannaval_perone = vannavalue(mpmathify(vinput["Delta"]), taures, mpmathify(vinput["sigma"])/100)
        #change in delta per unit change in sigma not as a percent ^^
        #error logging
        for item in vinput:
            print(vinput[item])
        print("Years num: %s\n\n" % nstr(taures, n=15))
        #end of error logging
        return '{"Vanna_Per1": %s, "Vanna_PerPercent": %s}' % (nstr(vannaval_perone, n=15), nstr(vannaval_perone/100, n=15))
    except (KeyError, TypeError) as err:
        return "Parameters entered incorrectly %s" % err.args[0], 400

@app.route('/script/ITMrisk.py')
def ITMRiskpage():
    vinput = request.args
    try:
        expdate = vinput["date"]
        taures = taufromdate(expdate)
        thedelta = mpmathify(vinput["Delta"])
        thesigma = mpmathify(vinput["sigma"])/100
        #error logging
        for item in vinput:
            print(vinput[item])
        print("Years num: %s\n\n" % nstr(taures, n=15))
        #end of error logging
        therisk = 0
        d1val = 0
        d2val = 0
        if thedelta > 0:
            #if Call
            d1val = InversePhi(thedelta)
            d2val = d1val - thesigma * sqrt(taures)
            therisk = ncdf(d2val)
        elif thedelta < 0:
            #if Put
            d1val = -InversePhi(-thedelta)
            d2val = d1val - thesigma * sqrt(taures)
            therisk = 1 - ncdf(d2val)
        else:
            return "Delta was 0?", 400
        print("Risk: %s%%" % nstr(therisk*100, n=15))
        retdict = {"ITMRiskPercent": "%s%%" % nstr(therisk*100, n=15)}
        return json.dumps(retdict)

    except (KeyError, TypeError) as err:
        return "Parameters entered incorrectly %s" % err.args[0], 400

@app.route('/script/PLplot')
def PLplot():
    theparams = request.args

if __name__ == '__main__':
	#app.run()
    serve(app, host='127.0.0.1', port=5000)
