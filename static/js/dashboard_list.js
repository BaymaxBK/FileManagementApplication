function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

$(document).on("click", ".delete-dashboard", function () {
    if (!confirm("Delete this dashboard?")) return;

    const dashboardId = $(this).data("id");
    

    $.ajax({
        url: `/statusdashboard/${dashboardId}/delete/`,
        type: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        success: function () {
            location.reload();
        },
        error: function () {
            alert("Failed to update!");
        }

    });
});

