import requests
import json
import hmac
import hashlib
import uuid
import datetime
from flask import request, redirect, render_template, session, jsonify

def setup_routes(app):
    @app.route('/')
    def product():
        products_info = [
        {'name': 'Sản phẩm 1', 'price': 100000, 'image': 'https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/d06eb56089c54bf39aec38e21be58b1d_9366/juventus-24-25-away-jersey.jpg'},
        {'name': 'Sản phẩm 2', 'price': 200000, 'image': 'https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/59ad67c97d264bc084937ad2dec4b723_9366/juventus-24-25-home-jersey.jpg'},
        {'name': 'Sản phẩm 3', 'price': 300000, 'image': 'https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/a844307c8ab94de5bc0237e72d798692_9366/juventus-23-24-home-jersey.jpg'}
    ]
        return render_template("pages/product.html", products=products_info)

    @app.route('/momo')
    def momo():
        total = request.args.get('total')
        if not total:
            return "Error: Total amount not provided", 400

        amount = str(int(total))
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        partnerCode = "MOMO"
        accessKey = "F8BBA842ECF85"
        secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        orderInfo = "pay with MoMo"
        redirectUrl = "http://127.0.0.1:5000/statusMomo"
        ipnUrl = "http://127.0.0.1:5000/checkout"
        orderId = str(uuid.uuid4())
        requestId = str(uuid.uuid4())
        requestType = "captureWallet"
        extraData = ""

        rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
        h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
        signature = h.hexdigest()

        data = {
            'partnerCode': partnerCode,
            'partnerName': "Test",
            'storeId': "MomoTestStore",
            'requestId': requestId,
            'amount': amount,
            'orderId': orderId,
            'orderInfo': orderInfo,
            'redirectUrl': redirectUrl,
            'ipnUrl': ipnUrl,
            'lang': "vi",
            'extraData': extraData,
            'requestType': requestType,
            'signature': signature
        }
        data = json.dumps(data)
        clen = len(data)
        response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
        print(response.json())
        momo_url = response.json()['payUrl']
        return redirect(momo_url)

    @app.route('/statusMomo')
    def statusMomo():
        status_code = request.args.get('resultCode')
        amount = request.args.get('amount')
        orderId = request.args.get('orderId')
        partnerCode = request.args.get('partnerCode')
        transId = request.args.get('transId')
        current_time = datetime.datetime.now()
        responseTime = current_time.strftime('%Y-%m-%d, %H:%M:%S')
        if status_code is not None:
            status_code = int(status_code)

        if status_code == 0:
            message = 'success'
        else:
            message = 'failure'

        session['message_momo'] = message
        session['amount_momo'] = amount
        session['orderId_momo'] = orderId
        session['partnerCode_momo'] = partnerCode
        session['transId_momo'] = transId
        session['responseTime_momo'] = responseTime

        return render_template("pages/loading.html", message=message, amount=amount, orderId=orderId, partnerCode=partnerCode, transId=transId, responseTime=responseTime)

    @app.route('/getPaymentStatus', methods=['GET'])
    def getPaymentStatus():
        message = session.get('message_momo')
        amount = session['amount_momo']
        orderId = session['orderId_momo']
        partnerCode = session['partnerCode_momo']
        transId = session['transId_momo']
        responseTime = session['responseTime_momo']
        print("============================", message)
        response_data = {
            'message': message,
            'amount': amount,
            'orderId': orderId,
            'partnerCode': partnerCode,
            'transId': transId,
            'responseTime': responseTime
        }
        return jsonify(response_data)

    @app.route('/clear_message_from_session', methods=['GET'])
    def clear_message_from_session():
        session['message_momo'] = None
        session['amount_momo'] = None
        session['orderId_momo'] = None
        session['partnerCode_momo'] = None
        session['transId_momo'] = None
        session['responseTime_momo'] = None
        response_data = {
            'message': None,
            'amount': None,
            'orderId': None,
            'partnerCode': None,
            'transId': None,
            'responseTime': None
        }
        return jsonify(response_data)

    @app.route('/loading')
    def loading():
        return render_template("pages/loading.html")
