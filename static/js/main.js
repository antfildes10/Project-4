// KartControl Main JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss success and info messages
  const alerts = document.querySelectorAll(".alert-success, .alert-info");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Confirm delete actions
  const deleteButtons = document.querySelectorAll("[data-confirm-delete]");
  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      if (
        !confirm(
          "Are you sure you want to delete this? This action cannot be undone.",
        )
      ) {
        e.preventDefault();
      }
    });
  });

  // Confirm booking cancellation
  const cancelButtons = document.querySelectorAll("[data-confirm-cancel]");
  cancelButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      if (!confirm("Are you sure you want to cancel this booking?")) {
        e.preventDefault();
      }
    });
  });
});
