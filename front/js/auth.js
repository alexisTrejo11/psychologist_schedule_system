document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById("loginForm")
    const loginError = document.getElementById("loginError")
    
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

    try {
        console.log("Intentando iniciar sesión con:", { email, password });
        
        const response = await fetch("http://localhost:8000/login/", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });
        
        console.log("Respuesta de la API:", response);
        
        // DATA
        if (response.ok) {
            const data = await response.json();
            console.log("Inicio de sesión exitoso:", data);
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
        
            window.location.href = "./home.html";
        } else {
            const errorData = await response.json();
            console.error("Error en la API:", errorData);
            loginError.textContent = errorData.message || "Correo electrónico o contraseña incorrectos.";
            loginError.style.display = "block";
        }
        } catch (error) {
        console.error("Error inesperado:", error);
        loginError.textContent = "Ocurrió un error al intentar iniciar sesión. Por favor, inténtalo más tarde.";
        loginError.style.display = "block";
        }
    });
});