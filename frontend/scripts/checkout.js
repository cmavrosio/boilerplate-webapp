document.addEventListener('DOMContentLoaded', async function() {
    // Ensure Stripe is initialized
    const stripe = Stripe('pk_test_51PqdJcFgaG64d7OF0HyA7Kf48qyDyEEzyA8vsEnoBz26jliVx52in1UjSmcrwwGZNOGTQ1cFmfcMEpPKjkiP1r1d00Gd30XE3X');

    if (!stripe) {
        console.error('Stripe failed to initialize');
        return;
    }

    const token = sessionStorage.getItem('token');

    if (token) {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const priceId = urlParams.get('price_id');
            const mode = urlParams.get('mode'); // Pass the mode as a query parameter
            const productId = urlParams.get('product_id');

            if (!priceId || !mode) {
                alert('Price ID or mode not found');
                console.error('Price ID or mode not found in URL.');
                return;
            }

            console.log('Price ID found:', priceId);
            console.log('Mode:', mode);

            const response = await fetch('http://localhost:8000/subscriptions/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ price_id: priceId, mode: mode}) // Send mode with the request
            });

            if (response.ok) {
                const sessionData = await response.json();
                console.log('Checkout session created:', sessionData);

                // Check if session.id exists
                if (sessionData && sessionData.sessionId) {
                    const result = await stripe.redirectToCheckout({ sessionId: sessionData.sessionId });

                    if (result.error) {
                        console.error('Stripe redirect error:', result.error.message);
                        alert('Error: ' + result.error.message);
                    }
                } else {
                    console.error('Session ID not found in the response:', sessionData);
                    alert('Error: Session ID not found. Please try again.');
                }
            } else {
                const errorMessage = await response.text();
                console.error('Failed to create checkout session:', errorMessage);
                alert('Error creating checkout session: ' + errorMessage);
            }
        } catch (error) {
            console.error('Error during fetch:', error);
            alert('An error occurred. Please try again.');
        }
    } else {
        window.location.href = 'login.html';
    }
});
