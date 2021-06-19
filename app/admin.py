from re import U
from flask import current_app, Blueprint, render_template, redirect, abort, request, url_for
import os

from flask_login.utils import login_required
from . import db
from json import loads
from .models import Product, Category, Promocode, SubCategory, Product_size, Order

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def admin_root():
    return redirect('/admin/products')

@admin.route('/admin/orders')
@login_required
def admin_orders():
    o = Order.query.all()
    return render_template('admin/orders.html', orders = o)

@admin.route('/admin/order')
@login_required
def admin_order():
    if rid:=request.args.get('id'):
        o = Order.query.get(int(rid))
        items = loads(o.items)
        delivery = loads(o.delivery)
        itemsunpckd = []
        for item in items:
            itemsunpckd.append( {
            'ps' : Product_size.query.get(item.get('product_size')),
            'q' : item.get('q')
            } )
        
        if o.promocode: promo = Promocode.query.get(o.promocode) 
        else: promo = None
        
        return render_template('admin/order.html', items = itemsunpckd, order = o, delivery = delivery, promocode = promo)

    else:
        return redirect('/admin/orders')

@admin.route('/admin/order/delete')
@login_required
def admin_order_del():
    if not request.args.get('id'):
        return redirect('/admin/orders')
    
    o = Order.query.get(int(request.args.get('id')))
    db.session.delete(o)
    db.session.commit()

    return redirect('/admin/orders')

@admin.route('/admin/products')
@login_required
def admin_products():
    p_list = Product.query.all()
    return render_template('admin/products.html', products = p_list)

@admin.route('/admin/product/add')
@login_required
def admin_product_add():
    sc = SubCategory.query.all()
    return render_template('admin/add_product.html', subcats = sc)

@admin.route('/admin/product/add', methods=['POST'])
@login_required
def admin_product_add_post():
    try:
        lastrowid = Product.query.all()[::-1]
        if len(lastrowid)==0:
            lastrowid=1
        else:
            lastrowid=len(lastrowid)+1

        name = request.form['name']
        price = request.form['price']
        desc = request.form['description']
        subcat = request.form['scat']
        try:
            f1 = request.files['file1']
            f1_name = f"{lastrowid}_1.jpg"
            f1.save(os.path.join(current_app.root_path, 'static', 'uploads', f'{f1_name}'))
            
        except Exception as e:
            return abort(400)
        try:
            f2 = request.files['file2']
            f2_name = f"{lastrowid}_2.jpg"
            f2.save(os.path.join(current_app.root_path, 'static', 'uploads', f'{f2_name}'))
        except:
            f2_name = f1_name

        newproduct = Product(
            name=name,
            price=int(price),
            description = desc,
            primary_img = f1_name,
            secondary_img = f2_name,
            subcategory = int(subcat)
        )
        db.session.add(newproduct)
        db.session.commit()
        return redirect(url_for('admin.admin_products'))

    except Exception as e:
        return abort(400)

@admin.route('/admin/product/edit')
@login_required
def admin_product_edit():
    if id:=request.args.get('id'):
        if p:=Product.query.get(int(id)):
            sc = SubCategory.query.all()
            return render_template('admin/product_edit.html', product=p, subcats = sc)
        else:
            return abort(404)
    else:
        return abort(400)

@admin.route('/admin/product/edit', methods=['POST'])
@login_required
def admin_product_edit_post():
    if rid:=request.form['id']:
        p = Product.query.get(int(rid))
        
        p.name = request.form['name']
        p.description = request.form['description']
        p.price = request.form['price']
        p.subcategory = request.form['scat']

        if request.files['file1'] and request.files['file1'].filename != '':
            r = request.files['file1']
            r_name = f"{p.id}_1.jpg"
            r.save(os.path.join(current_app.root_path, 'static', 'uploads', f'{r_name}'))
            p.primary_img = r_name
        
        if request.files['file2'] and request.files['file2'].filename != '':
            r = request.files['file2']
            r_name = f"{p.id}_2.jpg"
            r.save(os.path.join(current_app.root_path, 'static', 'uploads', f'{r_name}'))
            p.secondary_img = r_name
        
        db.session.add(p)
        db.session.commit()

        return redirect(f'/admin/product/edit?id={p.id}')
    
    else:
        return abort(400)

@admin.route('/admin/product/delete')
@login_required
def admin_product_delete():
    if r:= request.args.get('id'):
        p = Product.query.get(int(r))
        
        db.session.delete(p)
        db.session.commit()
        
        return redirect(url_for('admin.admin_products'))
    else:
        return redirect(url_for('admin.admin_products'))

@admin.route('/admin/product/sizes')
@login_required
def admin_product_sizes_get():
    if pid:= request.args.get('id'):
        p = Product_size.query.filter_by(product=int(pid)).all()
        return render_template('admin/sizes.html', sizes=p, p=int(pid))

@admin.route('/admin/product/sizes/add', methods=['POST'])
@login_required
def admin_product_sizes_add():
    pid = request.form['pid']
    size = request.form['size']
    ost = request.form['ost']

    n = Product_size(size = size, ost = ost, product = int(pid))
    db.session.add(n)
    db.session.commit()
    return redirect(f'/admin/product/sizes?id={pid}')

@admin.route('/admin/product/sizes/edit', methods=['POST'])
@login_required
def admin_product_sizes_edit():
    sid = request.form['id']
    size = Product_size.query.get(int(sid))
    size.ost = int(request.form['ost'])
    db.session.add(size)
    db.session.commit()
    return redirect(f'/admin/product/sizes?id={size.product}')

@admin.route('/admin/categories')
@login_required
def admin_categories_get():
    categories = Category.query.all()
    scats = SubCategory.query.all()
    return render_template('admin/categories.html', categories=categories, scats = scats)

@admin.route('/admin/categories/add_cat', methods=['POST'])
@login_required
def admin_categories_addcat():
    try:
        catname = request.form['name']

        newcat = Category(name=catname)
        db.session.add(newcat)
        db.session.commit()

        return redirect(url_for('admin.admin_categories_get'))

    except:
        return abort(400)

@admin.route('/admin/categories/add_subcat', methods=['POST'])
@login_required
def admin_categories_addsubcat():
    try:
        catid = request.form['cat']
        subcatname = request.form['name']

        newsubcat = SubCategory(name=subcatname, category_ref=int(catid) )
        db.session.add(newsubcat)
        db.session.commit()

        return redirect(url_for('admin.admin_categories_get'))

    except:
        return abort(400)

@admin.route('/admin/categories/delete_cat', methods = ['POST'])
def delete_cat():
    cat = request.form['cat']
    c = Category.query.get(int(cat))
    for scat in c.subcategorys:
        for item in scat.product_ref:
            db.session.delete(item)
            db.session.commit()
        
        db.session.delete(scat)
        db.session.commit()
    
    db.session.delete(c)
    db.session.commit()
    return redirect('/admin/categories')

@admin.route('/admin/categories/delete_subcat', methods = ['POST'])
def delete_subcat():
    scat = request.form['scat']
    scat = SubCategory.query.get(int(scat))
    for item in scat.product_ref:
        db.session.delete(item)
        db.session.commit()

    db.session.delete(scat)
    db.session.commit()
    return redirect('/admin/categories')

@admin.route('/admin/promo')
@login_required
def admin_promo_view():
    promos = Promocode.query.filter(Promocode.count>0).all()
    return render_template('admin/promo.html', promos=promos)

@admin.route('/admin/promo/add', methods=['POST'])
@login_required
def admin_promo_add():
    key = request.form['code']
    disc = request.form['disc']
    ost = request.form['ost']

    n = Promocode(key=key, discount=disc, count=ost)
    db.session.add(n)
    db.session.commit()
    return redirect(url_for('admin.admin_promo_view'))

@admin.route('/admin/promo/del')
@login_required
def admin_promo_del():
    if rid:=request.args.get('id'):
        p = Promocode.query.get(int(rid))
        db.session.delete(p)
        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)
