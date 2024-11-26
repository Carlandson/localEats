document.addEventListener('DOMContentLoaded', () => {
    const togglePass = document.getElementById('toggleVis');
    togglePass.addEventListener('click', () => {
        togglePasswordVisibility();
    });
})



function togglePasswordVisibility() {
    var x = document.getElementById("password");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }