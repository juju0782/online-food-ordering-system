function changeToPlaced(productId) {
    // Get the icon element based on product ID
    var iconElement = document.getElementById("icon-" + productId);

    // Change the color and innerHTML to reflect the state of being placed
    if (iconElement) {
        iconElement.style.color = "green";  // Change the color to green
        iconElement.innerHTML = `<span style="font-size:0.45em;"> Placed </span>`;  // Change the text to "Placed"
    }
    }



document.querySelectorAll('.update-quantity-btn').forEach(button => {
    button.addEventListener('click', event => {
        event.preventDefault();

        const productId = button.dataset.productId;
        const action = button.dataset.action;

        fetch("{{ url_for('cart.shopping_cart') }}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ product_id: productId, action: action })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the cart item details
                document.getElementById(`quantity-${productId}`).textContent = data.updated_quantity;
                document.getElementById(`item-total-${productId}`).textContent = `KSh ${data.updated_item_total.toFixed(2)}`;
                document.getElementById('total-price').textContent = `KSh ${data.new_total_price.toFixed(2)}`;
                
                // Remove the item row if quantity becomes 0
                if (data.updated_quantity === 0) {
                    document.getElementById(`cart-item-${productId}`).remove();
                }

                // Show empty cart message if cart becomes empty
                if (data.cart_empty) {
                    document.querySelector('.container').innerHTML = `
                        <p>Your cart is empty.</p>
                        <a href="{{ url_for('main.home') }}" class="btn btn-primary">Start Shopping</a>
                    `;
                }
            } else {
                alert(data.message || "An error occurred.");
            }
        })
        .catch(error => console.error("Error:", error));
    });
});