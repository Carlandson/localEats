document.addEventListener('DOMContentLoaded', () => {
    const togglePass = document.getElementById('toggleVis');
    togglePass.addEventListener('click', () => {
        togglePasswordVisibility();
    });
    const switchToGoogleBtn = document.getElementById('switchToGoogleBtn');
    const backToLoginBtn = document.getElementById('backToLoginBtn');
    const regularLoginContainer = document.getElementById('regularLoginContainer');
    const googleSignInContainer = document.getElementById('googleSignInContainer');

    if (switchToGoogleBtn) {
        switchToGoogleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            regularLoginContainer.classList.add('hidden');
            googleSignInContainer.classList.remove('hidden');
        });
    }

    if (backToLoginBtn) {
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