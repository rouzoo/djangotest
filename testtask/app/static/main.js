console.log("Sanity check!");
let stripe;
// Get Stripe publishable key
fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  stripe = Stripe(data.publicKey);  
});

function buy(id, itemCount) {

  var url = new URL(window.location.protocol+window.location.host+"/buy/"+id),
  params = {itemCount}
Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))


  fetch(url)
    
  .then((result) => {return result.json(); })
  .then((data) => {
    // Redirect to Stripe Checkout
    return stripe.redirectToCheckout({sessionId: data.sessionId})
  })
  .then((res) => {
    console.log(res);
  });
}
