"use strict";

function copy_form_result() {
    // let copyText = document.getElementById("id_fixed_sentence"); // from form
    let copyText = document.getElementById("results").dataset.fixed;
    navigator.clipboard.writeText(copyText); // .value
}

function copy_form_url() {
    let url = window.location.href;
    navigator.clipboard.writeText(url);
}

function write_clipboard(text) {
    navigator.clipboard.writeText(text);
}

function h() {
    let x = document.getElementById("hidden");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}