from flask import Flask, Blueprint, render_template, request
from rpc import BitcoinCLI
import os, json

# put your credentials here:
rpc = BitcoinCLI("rpcuser","rpcpassword",port=38443)

app = Flask(__name__, template_folder="templates", static_folder="static")

rand = os.urandom(5).hex()
fallbackaddr = None

def sendtoaddress(address, amount, wallet=None):
    w = wallet
    if w is None:
        w = rpc.wallet("")
    extra_inputs = []
    trusted_balance = w.getbalances()["mine"]["trusted"]
    total_in = 0
    inputs = []
    if trusted_balance < amount:
        txlist = self.cli.listunspent(0,0)
        b = amount-trusted_balance
        for tx in txlist:
            extra_inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
            inputs.append(tx)
            b -= tx["amount"]
            total_in += tx["amount"]
            if b < 0:
                break

    psbt = w.walletcreatefundedpsbt(
        extra_inputs,           # inputs
        [{address: amount}],    # output
        0,                      # locktime
        {},                     # options
        True                    # replaceable
    )["psbt"]
    print(psbt)
    psbt = w.walletprocesspsbt(psbt)["psbt"]
    print(psbt)
    res = w.finalizepsbt(psbt)
    print(res)
    tx = res["hex"]
    w.sendrawtransaction(tx)
    return tx

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
                tx = sendtoaddress(addr, 0.1)
                decoded = w.decoderawtransaction(tx)
                result = {"rawtx": tx, "decoded": decoded}
                kwargs["result"] = json.dumps(result,indent=4)
            elif action == "broadcast":
                rawtx = request.form['rawtx']
                decoded = w.decoderawtransaction(rawtx)
                res = w.sendrawtransaction(rawtx)
                result = {"decoded": decoded}
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
