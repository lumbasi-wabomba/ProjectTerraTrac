import React, { useState } from "react";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();

        try {
            // add the link
            const response = await fetch("link", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({username, password}),
            });
            
            const data = await response.json();

            if (response.ok) {
                localStorage.setItem("auth_token", data.token);
                window.location.href = "/profile";
            } else {
                setError(data.error || "Login failed");
            }
        }catch (err) {
            setError("Something went wrong");
        }
    }

    return (
        <div className="login-container">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <input type="text" placeholder="Username or Email" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                <input type="password" placeholder="password" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                <button type="submit">Login</button>
            </form>
            {error && <p style={{color: "red"}}>{error}</p>}
        </div>
    )
}

export default Login