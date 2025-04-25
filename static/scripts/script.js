
document.addEventListener("DOMContentLoaded", function() {
    // Get the search input and table
    const searchInput = document.getElementById("searchInput");
    const table = document.getElementById("resultsTable");
    const rows = table.querySelectorAll("tbody tr");
    
    // Function to filter the table based on search input
    searchInput.addEventListener("input", function() {
    const searchValue = searchInput.value.toLowerCase();
    
    rows.forEach(row => {
    const patientName = row.querySelector("td").textContent.toLowerCase();
    
    // If the patient's name matches the search query, show the row
    if (patientName.includes(searchValue)) {
    row.style.display = "";
    } else {
    row.style.display = "none"; // Hide the row if there's no match
    }
    });
    });
    });