const backendUrl = 'http://localhost:8000';



document.addEventListener('DOMContentLoaded', async function() {
    if (!sessionStorage.getItem('token')) {
        window.location.href = 'login.html';
    } else {
        const token = sessionStorage.getItem('token');
        try {
            // Fetch user information
            const userResponse = await fetch(`${backendUrl}/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (userResponse.ok) {
                const user = await userResponse.json();
                document.getElementById('welcome-message').textContent = `Welcome, ${user.full_name}!`;
            } else {
                console.error('Failed to fetch user:', await userResponse.text());
            }

            // Check subscription status
            const subscriptionResponse = await fetch(`${backendUrl}/subscriptions/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (subscriptionResponse.ok) {
                const subscriptionData = await subscriptionResponse.json();
                if (subscriptionData.subscription_status) {
                    displaySubscriptionMessage();
                } else {
                    // Fetch and display the products
                    const productsResponse = await fetch(`${backendUrl}/products/`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (productsResponse.ok) {
                        const products = await productsResponse.json();
                        displayProducts(products);
                    } else {
                        console.error('Failed to fetch products:', await productsResponse.text());
                    }
                }
            } else {
                console.error('Failed to fetch subscription status:', await subscriptionResponse.text());
            }

        } catch (error) {
            console.error('Error during fetch:', error);
        }
    }
});
document.addEventListener('DOMContentLoaded', async function() {
    const token = sessionStorage.getItem('token');
    
    if (token) {
        try {
            // Fetch user information
            const userResponse = await fetch(`${backendUrl}/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (userResponse.ok) {
                const user = await userResponse.json();
                document.getElementById('welcome-message').textContent = `Welcome, ${user.full_name}!`;
            } else {
                console.error('Failed to fetch user:', await userResponse.text());
            }

            // Check subscription status
            const subscriptionResponse = await fetch(`${backendUrl}/subscriptions/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (subscriptionResponse.ok) {
                const subscriptionData = await subscriptionResponse.json();
                if (subscriptionData.subscription_status) {
                    displaySubscriptionMessage();
                } else {
                    // Fetch and display the products
                    const productsResponse = await fetch(`${backendUrl}/products/`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (productsResponse.ok) {
                        const products = await productsResponse.json();
                        displayProducts(products);
                    } else {
                        console.error('Failed to fetch products:', await productsResponse.text());
                    }
                }
            } else {
                console.error('Failed to fetch subscription status:', await subscriptionResponse.text());
            }

        } catch (error) {
            console.error('Error during fetch:', error);
        }
    } else {
        // Redirect to the login page if there's no token
        window.location.href = 'login.html';
    }
});

function displaySubscriptionMessage() {
    const container = document.querySelector('.product-cards-container');
    container.innerHTML = ''; // Clear any existing content

    const message = document.createElement('p');
    message.classList.add('subscription-message');
    message.textContent = 'Congrats, you have an active subscription!';
    container.appendChild(message);
}

function displayProducts(products) {
    const container = document.querySelector('.product-cards-container');
    container.innerHTML = ''; // Clear any existing content

    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');

        // Create the product title element
        const title = document.createElement('h2');
        title.classList.add('product-title');
        title.textContent = product.name;
        productCard.appendChild(title);

        // Create the product price element
        const price = document.createElement('p');
        price.classList.add('product-price');
        price.textContent = `${(product.price_info.unit_amount / 100).toFixed(2)} ${product.price_info.currency.toUpperCase()}`;
        productCard.appendChild(price);

        // Create the product description element
        const description = document.createElement('p');
        description.classList.add('product-description');
        productCard.appendChild(description);

        // Create the buy/subscribe button
        const buyButton = document.createElement('a');
        buyButton.classList.add('buy-button');

        if (product.price_info.type === 'one_time') {
            buyButton.textContent = 'Buy Forever';
            buyButton.href = `checkout.html?price_id=${product.price_info.id}&mode=payment&product_id=${product.id}`; // Set mode as payment
        } else if (product.price_info.type === 'recurring') {
            buyButton.textContent = 'Subscribe Monthly';
            buyButton.href = `checkout.html?price_id=${product.price_info.id}&mode=subscription&product_id=${product.id}`; // Set mode as subscription
        }

        productCard.appendChild(buyButton);
        container.appendChild(productCard);
    });
}
