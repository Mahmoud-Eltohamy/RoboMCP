// Custom JavaScript for MCP Appium

// Initialize tooltips
document.addEventListener("DOMContentLoaded", function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll("[data-bs-toggle=\"tooltip\"]"));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll("[data-bs-toggle=\"popover\"]"));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Animated scroll to top
    var scrollToTopBtn = document.getElementById("scrollToTop");
    if (scrollToTopBtn) {
        window.addEventListener("scroll", function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                scrollToTopBtn.style.display = "block";
            } else {
                scrollToTopBtn.style.display = "none";
            }
        });

        scrollToTopBtn.addEventListener("click", function() {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });
    }

    // Add copy-to-clipboard functionality for code blocks
    var codeBlocks = document.querySelectorAll("pre code");
    codeBlocks.forEach(function(codeBlock) {
        var copyButton = document.createElement("button");
        copyButton.className = "btn btn-sm btn-outline-primary copy-button";
        copyButton.innerHTML = "<i class=\"bi bi-clipboard\"></i>";
        copyButton.title = "Copy to clipboard";
        copyButton.style.position = "absolute";
        copyButton.style.top = "0.5rem";
        copyButton.style.right = "0.5rem";
        
        // Set the parent pre to position relative for absolute positioning
        codeBlock.parentNode.style.position = "relative";
        
        codeBlock.parentNode.appendChild(copyButton);
        
        copyButton.addEventListener("click", function() {
            navigator.clipboard.writeText(codeBlock.textContent).then(function() {
                copyButton.innerHTML = "<i class=\"bi bi-check\"></i>";
                setTimeout(function() {
                    copyButton.innerHTML = "<i class=\"bi bi-clipboard\"></i>";
                }, 2000);
            });
        });
    });
});
