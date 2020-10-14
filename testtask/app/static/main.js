let stripe;
// Get Stripe publishable key
var cart = []
fetch("/config/")
    .then((result) => {
        return result.json();
    })
    .then((data) => {
        // Initialize Stripe.js
        stripe = Stripe(data.publicKey);
    });

function buy(id, itemCount) {

    var url = new URL(window.location.protocol + window.location.host + "/buy/" + id),
        params = {itemCount}
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

    fetch(url)
        .then((result) => {
            return result.json();
        })
        .then((data) => {
            // Redirect to Stripe Checkout
            return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
            console.log(res);
        });
}

function addToCart(id, ItemCount) {
    let isIdInCart = false;
    cart.forEach(elem => {
        if (elem.item_id === id) {
            isIdInCart = true;
            elem.quantity = ItemCount;
        }
    })

    if (isIdInCart === false) {
        cart.push({
            'item_id': id,
            'quantity': ItemCount,
        })
        
    }
    alert('added')
}

function checkout() {

    if (typeof cart != "undefined" && cart != null && cart.length != null && cart.length > 0) {
        var url = new URL(window.location.protocol + window.location.host + "/checkout/")
        fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({cart: cart})
    })
        .then((result) => {
            return result.json();
        })
        .then((data) => {
            return stripe.redirectToCheckout({sessionId: data.sessionId})
        });
    }
    else {
        alert('cart is empty')
    }

}
    