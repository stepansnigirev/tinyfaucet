from flask import Flask, Blueprint, render_template, request
from rpc import BitcoinCLI
import os, json

# put your credentials here:
rpc = BitcoinCLI("specter","TruckWordTrophySolidVintageFieldGalaxyOrphanSeek",port=18443)

app = Flask(__name__, template_folder="templates", static_folder="static")

rand = os.urandom(5).hex()
fallbackaddr = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global fallbackaddr
    w = rpc.wallet("")
    balance = w.getbalances()
    if fallbackaddr is None:
        fallbackaddr = w.getnewaddress()
    result=None
    kwargs = {
        "balance": balance,
        "rand": rand,
        "result": None,
        "fallbackaddr": fallbackaddr,
    }
    if request.method == 'POST':
        try:
            action = request.form['action']
            if action == "getfunds":
                addr = request.form['btcaddress']
                txid = w.sendtoaddress(addr, 0.1)
                tx = w.getrawtransaction(txid)
                decoded = w.decoderawtransaction(tx)
                result = {"txid": txid, "rawtx": tx, "decoded": decoded}
                kwargs["result"] = json.dumps(result,indent=4)
        except Exception as e:
            error = "%r" % e
            return render_template("index.html", error=error, **kwargs)
    # return json.dumps(balance, indent=4)
    return render_template("index.html", **kwargs)

def main():
    extra_dirs = ['templates']
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    app.run(port=24000, debug=True, extra_files=extra_files)

if __name__ == '__main__':
    main()
