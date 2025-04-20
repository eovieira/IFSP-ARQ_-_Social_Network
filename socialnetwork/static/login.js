const registerButton = document.getElementById("register");
const loginButton = document.getElementById("login");
const container = document.getElementById("container");

registerButton.addEventListener("click", () => {
    console.log(`Clicou no botão de Cadastro`)
    container.classList.add("right-panel-active");
});

loginButton.addEventListener("click", () => {
    console.log(`Clicou no botão de login`);
    container.classList.remove("right-panel-active");
});