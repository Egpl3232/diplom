from flask import Blueprint, render_template, redirect, request, session, current_app, abort, jsonify
from flask.helpers import url_for
from . import db
from .models import *
from json import dumps
from .models import Product, Category, Basket, Product_size

main = Blueprint('main', __name__)

@main.before_app_first_request
def newCustomer():
    if 'customer' not in session:
        customer = Customer()
        db.session.add(customer)
        db.session.commit()
        session['customer'] = str(customer.id)
        session.permanent = True 
        current_app.logger.info("New user id : {}".format(customer.id))

@main.before_request
def fixCustomer():
    if 'customer' in session:
        session['customer'] = session['customer']
    else:
        newCustomer()


def calculatebasketprice(cart):
    price = 0
    for item in cart: 
        price += item.amount * item.product.product_size.price
    return price


@main.route('/')
def main_root():
    new = Product.query.order_by(Product.date.desc()).limit(5)
    popular = Product.query.order_by(Product.sales.desc()).limit(5)
    cart = Basket.query.filter_by(cust_id=int(session['customer'])).all()
    cartprice = calculatebasketprice(cart)
    return render_template('index.html', popular=popular, newprod=new, cart = cart, cartprice = cartprice)


@main.route('/tracking')
def tracking_page():
    return render_template('track.html')

@main.route('/shipping')
def shipping_page():
    return render_template('shipping.html')

@main.route('/aboutus')
def about_page():
    return render_template('aboutus.html')

@main.route('/warranty')
def warranty_page():
    return render_template('warranty.html')

@main.route('/policy')
def policy_page():
    return render_template('policy.html')

@main.route('/toe')
def toe_page():
    return render_template('toe.html')

@main.route('/sizetable')
def sizepage():
    return render_template('size.html')

@main.route('/product')
def product():
    cp = calculatebasketprice(Basket.query.filter_by(cust_id = session['customer']).all())
    cart = Basket.query.filter_by(cust_id=int(session['customer'])).all()
    if rid:=request.args.get('id'):
        p = Product.query.get(rid)
        return render_template('product.html', product=p, cart = cart, cartprice = cp)
    else:
        return redirect(url_for(request.referrer))
        
@main.route('/shop')
def products():
    cp = calculatebasketprice(Basket.query.filter_by(cust_id = session['customer']).all())
    plist = Product.query.all()
    cats = Category.query.all()
    if r:=request.args.get('sc'):
        p = Product.query.filter(Product.subcategory==int(r)).all()
        return render_template('products.html', plist=p, cats=cats, cartprice = cp)
    else: 
        return render_template('products.html', plist=plist, cats=cats, cartprice = cp)


@main.route('/cart')
def cart_get():
    promocode = None
    discountvalue = None
    cart = Basket.query.filter_by(cust_id = session['customer']).all()
    cp = calculatebasketprice(Basket.query.filter_by(cust_id = session['customer']).all())
    
    if promo:=request.args.get('promocode'):
        promo = Promocode.query.filter_by(key=promo).first()
        if promo.count>0: promocode = promo
    
    if promocode: 
        discountvalue = (cp + 300) / 100 * promocode.discount
        total =  (cp + 300) - ((cp + 300) / 100 * promocode.discount)

    else: total = cp + 300

    return render_template('cart.html', cart=cart,
     promocode = promocode,
      cartprice = cp,
       total=total,
        discountvalue=discountvalue,
        bp = cp
        )

@main.route('/basket/add', methods=['POST'])
def basket_add():
    if 'size' in request.form:
        size = request.form['size']
    else:
        return redirect(request.referrer)
    qty = request.form['qtybutton']

    ps = Product_size.query.get(int(size))

    if ps.ost < int(qty):
        return redirect(url_for('main.products'))
    
    nb = Basket(amount=int(qty), cust_id=int(session['customer']) ,item_size=int(size))
    db.session.add(nb)
    db.session.commit()
    return redirect(request.referrer)
    
@main.route('/basket/del')
def basket_del():
    if bid:=request.args.get('id'):
        b = Basket.query.get(int(bid))
        if b.cust_id == int(session['customer']):
            db.session.delete(b)
            db.session.commit()
            return redirect(request.referrer)
        else:
            return abort(403)
    else:
        return abort(404)

@main.route('/order', methods=['POST'])
def createorder():
    f = request.form
    try:

        delinfo = {}
        delinfo["name"] = f['name']
        delinfo["surname"] = f['surname']
        delinfo["email"] = f['email']
        delinfo['phone'] = f['phone']
        delinfo["city"] = f['phone']
        delinfo["street"] = f['phone'] 
        delinfo["build"] = f['building']
        delinfo["flat"] = f['flat']
        delinfo["zipcode"] = f['zipcode']
        paytype = int(f['pay'])

    except:
        return redirect(request.referrer)
    
    cart = Basket.query.filter_by(cust_id = session['customer']).all()
    total = round(calculatebasketprice(Basket.query.filter_by(cust_id = session['customer']).all()))+300

    jsonarr = []

    for item in cart:
        i = {}
        i['product_size'] = item.product.id
        item.product.product_size.sales+=1
        item.product.ost-= item.amount
        db.session.add(item)
        db.session.commit()
        i['q'] = item.amount
        jsonarr.append(i)

    jsonarr = dumps(jsonarr)

    try: 
        promo =  Promocode.query.filter_by(key=f['promocode']).first()
        if promo and promo.count>0:
            promocode = promo.id
            promo.count -= 1
            total = round(total - ((total/100) * promo.discount))
            db.session.add(promo)
            db.session.commit()
        else:
            promocode = None
    except:
        promocode = None
    
    nr = Order(cust_id = int(session['customer']), items=jsonarr, delivery=dumps(delinfo), pay_type = paytype, promocode = promocode, total=total)
    db.session.add(nr)
    db.session.commit()

    for item in cart:
        db.session.delete(item)
        db.session.commit()

    return redirect(f'/order/success?id={nr.id}')

@main.route('/order/success')
def order_succ():
    if o:=request.args.get('id'):
        return render_template('successorder.html', id = o)
    else:
        return redirect('/')