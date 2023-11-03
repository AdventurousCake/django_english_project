function copy_result() {
  let copyText = document.getElementById("id_fixed_sentence");
  navigator.clipboard.writeText(copyText.value);
}

function copy_url() {
  let url = window.location.href;
  navigator.clipboard.writeText(url);
}