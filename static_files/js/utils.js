function copy_form_result() {
  let copyText = document.getElementById("id_fixed_sentence");
  navigator.clipboard.writeText(copyText.value);
}

function copy_form_url() {
  let url = window.location.href;
  navigator.clipboard.writeText(url);
}

function write_clipboard(text) {
  navigator.clipboard.writeText(text);
}