// ===== PRODUCT MODAL =====
function openProductModal(modalId) {
    document.getElementById(modalId).classList.add("show");
    document.body.style.overflow = "hidden";
}
function closeProductModal(modalId) {
    document.getElementById(modalId).classList.remove("show");
    document.body.style.overflow = "auto";
}
function changeProductMedia(itemId, mediaUrl, mediaType, clickedThumb) {
    const mainBox = document.getElementById("mainMediaBox" + itemId);
    if (mediaType === "video") {
        mainBox.innerHTML = `<video controls autoplay style="width:100%;height:100%;object-fit:contain;border-radius:20px;"><source src="${mediaUrl}">Your browser does not support video.</video>`;
    } else {
        mainBox.innerHTML = `<img src="${mediaUrl}" alt="Product image">`;
    }
    const thumbs = clickedThumb.parentElement.querySelectorAll(".product-thumb");
    thumbs.forEach(t => t.classList.remove("active"));
    clickedThumb.classList.add("active");
}
function openDetailTab(itemId, tabName, clickedButton) {
    const modal = clickedButton.closest(".product-detail-info");
    modal.querySelectorAll(".detail-tab-content").forEach(c => c.classList.remove("active"));
    modal.querySelectorAll(".detail-tab-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(tabName + itemId).classList.add("active");
    clickedButton.classList.add("active");
}

// ===== CLOSE MODAL ON OUTSIDE CLICK =====
window.addEventListener("click", function(event) {
    document.querySelectorAll(".product-detail-overlay, .modal-overlay").forEach(modal => {
        if (event.target === modal) {
            modal.classList.remove("show");
            document.body.style.overflow = "auto";
        }
    });
});

// ===== PRODUCT SEARCH =====
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById("productSearch");
    const productCards = document.querySelectorAll(".product-card");
    if (searchInput) {
        searchInput.addEventListener("keyup", function() {
            const value = this.value.toLowerCase();
            productCards.forEach(card => {
                const name = card.dataset.name || "";
                const category = card.dataset.category || "";
                card.style.display = (name.includes(value) || category.includes(value)) ? "block" : "none";
            });
        });
    }
});

// ===== MOBILE MENU =====
function toggleMobileMenu() {
    const nav = document.getElementById('mobileNav');
    const btn = document.getElementById('hamburger');
    nav.classList.toggle('open');
    btn.classList.toggle('active');
}

// ===== NEWSLETTER FORM =====
document.addEventListener('DOMContentLoaded', function() {
    const newsletterBtn = document.querySelector('.newsletter-form button');
    const newsletterInput = document.querySelector('.newsletter-form input');
    if (newsletterBtn && newsletterInput) {
        newsletterBtn.addEventListener('click', function() {
            if (newsletterInput.value && newsletterInput.value.includes('@')) {
                newsletterBtn.innerHTML = '<i class="fas fa-check"></i>';
                newsletterBtn.style.background = '#4caf50';
                newsletterInput.value = '';
                setTimeout(() => {
                    newsletterBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                    newsletterBtn.style.background = '';
                }, 3000);
            }
        });
    }
});
