document.addEventListener('DOMContentLoaded', () => {
    const togglePass = document.getElementById('toggleVis');
    if (togglePass) {
        togglePass.addEventListener('click', () => {
            togglePasswordVisibility();
        });
    }
    const backToLoginBtn = document.getElementById('backToLoginBtn');
    const regularLoginContainer = document.getElementById('regularLoginContainer');
    const googleSignInContainer = document.getElementById('googleSignInContainer');

    if (backToLoginBtn && regularLoginContainer && googleSignInContainer) {
        backToLoginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            googleSignInContainer.classList.add('hidden');
            regularLoginContainer.classList.remove('hidden');
        });
    }
})



function togglePasswordVisibility() {
    var x = document.getElementById("password");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }