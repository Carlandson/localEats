document.addEventListener('DOMContentLoaded', () => {
    const togglePass = document.getElementById('toggleVisPass');
    togglePass.addEventListener('click', () => {
        togglePasswordVisibility();
    });
    const toggleConf = document.getElementById('toggleVisConf');
    toggleConf.addEventListener('click', () => {
        toggleConfVisibility();
    });
})



function togglePasswordVisibility() {
    var x = document.getElementById("id_password1");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }

  function toggleConfVisibility() {
    var x = document.getElementById("id_password2");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }