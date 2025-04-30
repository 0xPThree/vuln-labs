// Helper to get cookie by name
function getCookieValue(name) {
    const value = document.cookie
        .split("; ")
        .find(row => row.startsWith(name + "="));
    return value ? value.split("=")[1] : null;
}

const firstName = document.getElementById("first_name");
const lastName = document.getElementById("last_name");
const email = document.getElementById("email");
const phoneNum = document.getElementById("phone_number");
const accessToken = document.getElementById("access_token");

let userHash = getCookieValue("user_hash");

// Debugging log to see if user_hash is being retrieved from cookies
// console.log("User hash from cookies:", userHash);

if (userHash) {
    fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_hash: userHash })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json(); // Parse response body as JSON
    })
    .then(jsonObj => {
        console.log("Fetched user profile data:", jsonObj);
        firstName.value = jsonObj.first_name || "";
        lastName.value = jsonObj.last_name || "";
        email.value = jsonObj.email || "";
        phoneNum.value = jsonObj.phone_number || "";
        accessToken.value = jsonObj.access_token || "";
    })
    .catch(err => {
        console.error("Error fetching user profile:", err);
    });
} else {
    console.warn("No user_hash found in cookies.");
}
