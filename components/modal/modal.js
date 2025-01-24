htmx.on("htmx:afterSwap", (e) => {
  console.log("afterSwap");
  // Response targeting #dialog => show the modal
  var modal = new bootstrap.Modal(document.getElementById("modal"));

  if (e.detail.target.id == "dialog") {
    console.log("showing the modal");
    modal.show();
  }
});

htmx.on("htmx:beforeSwap", (e) => {
  console.log("beforeSwap");
  // Empty response targeting #dialog => hide the modal
  if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
    var modal = new bootstrap.Modal(document.getElementById("modal"));
    modal.hide();
    console.log("hiding the modal");
    $('body').removeClass('modal-open');
    $('.modal-backdrop').remove();
    e.detail.shouldSwap = false;
    document.body.style.overflow = "auto"; 
  }
});

htmx.on("hidden.bs.modal", () => {
    console.log("hidden.bs.modal");
    $('#dialog').innerHTML = "";
    $('body').removeClass('modal-open');
    $('.modal-backdrop').remove();
    document.body.style.overflow = "auto"; 
});

htmx.on("boardUpdated", () => {
    console.log("boardUpdated");
    /*
    //var modal = new bootstrap.Modal(document.getElementById("modal"));
    $('#modal').hide();
    $('body').removeClass('modal-open');
    $('.modal-backdrop').remove();
    e.detail.shouldSwap = false;
    document.body.style.overflow = "auto"; 
    */

    const regex = /\stories\/[0-9a-f]{32}$/i;
    console.log(window.location.href);
    const href = window.location.href.replace(regex, '');
    console.log(href);
    window.location.replace(href);
    console.log(window.location.href);
});
