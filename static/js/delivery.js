function placeOrder() {
    const form    = document.getElementById("checkoutForm");
    const wrapper = document.getElementById("dogWrapper");
    const btn     = document.getElementById("placeOrderBtn");

    // Validate form first
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Bug fix: reset animation state before re-triggering.
    // Without this, if the user somehow clicks twice the classList
    // already has 'animate' and the keyframe won't restart.
    wrapper.classList.remove("animate");
    wrapper.style.display = "block";

    // Force reflow so the browser registers the class removal
    // before we add it back (otherwise the animation won't restart).
    void wrapper.offsetWidth;

    wrapper.classList.add("animate");

    // Disable button & show spinner
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    btn.disabled  = true;

    // Submit after animation completes (2.5 s)
    setTimeout(() => {
        form.submit();
    }, 2500);
}
