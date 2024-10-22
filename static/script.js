function BlockButton() {
    const month  = document.getElementById("current-month");
    const year = document.getElementById("current-year");
    const button = document.getElementById("previous-month")
    if (month.value == "7" && year.value == "2024") {
        button.disabled = "disabled";
    }
}
document.getElementById("previous-month").addEventListener("DOMContentLoaded", BlockButton())

