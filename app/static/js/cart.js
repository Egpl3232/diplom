const productsBtn = document.querySelectorAll ('.add-cart');
const cartProductsList = document.querySelectorAll ('.product-icon');
const cart = document.querySelectorAll ('.header-cart');
const cart = document.querySelectorAll ('.cart-content');
let price = 0;

const randomId = () => {
	return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

const priceWithoutSpaces = (str) => {
	return str.replace(/\s/g, '');
};

const normalPrice = (str) => {
	return String(str).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
};

const generateCartProduct = (img, name, price, qty, id) => {
	return `
    <div class="cart-img">
    <a href="#">"${img}" alt=""></a>
    </div>
    <div class="cart-content">
    <div class="cart-name"> <a href="#">"${name}" </div>
    <div class="cart-price"> "${price}" </div>
    <div class="cart-qty"> Qty: <span>"${qty}"</span> </div>
    </div>
    <div class="remove"> <a href="#"><i class="zmdi zmdi-close"></i></a> </div>
    </div>
	`;
};

productsBtn.forEach(el => {
	el.closest('.product').setAttribute('data-id', randomId());

	el.addEventListener('click', (e) => {
		let self = e.currentTarget;
		let parent = self.closest('.product');
		let id = parent.dataset.id;
		let img = parent.querySelector('.images/catalog/..').getAttribute('src');
		let name = parent.querySelector('.product_name').textContent;
		let priceString = priceWithoutSpaces(parent.querySelector('.product-price__current').textContent);
		let priceNumber = parseInt(priceWithoutSpaces(parent.querySelector('.product-price').textContent));

		plusFullPrice(priceNumber);

		printFullPrice();

		cartProductsList.querySelector('.simplebar-content').insertAdjacentHTML('afterbegin', generateCartProduct(img, title, priceString, id));
		printQuantity();

		
		self.disabled = true;
	});
});