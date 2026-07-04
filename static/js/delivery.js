function placeOrder() {

    const form = document.getElementById("checkoutForm");
    const wrapper = document.querySelector(".dog-wrapper");
    const btn = document.getElementById("placeOrderBtn");

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Start animation
    wrapper.style.display = "block";
    wrapper.classList.add("animate");

    // Button loading
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    btn.disabled = true;

    setTimeout(() => {
        form.submit();
    }, 2500);
}