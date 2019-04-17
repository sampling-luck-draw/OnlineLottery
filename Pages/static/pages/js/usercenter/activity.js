

$(document).ready(function() {
  $("#awards-table").DataTable({
      dom: "Bfrtip",
      buttons: [{
        extend: "copy",
        className: "btn-sm"
      }, {
        extend: "csv",
        className: "btn-sm"
      }, {
        extend: "pdfHtml5",
        className: "btn-sm"
      }, {
        extend: "print",
        className: "btn-sm"
      },],
      responsive: true,
      order: [
        [0, 'asc']
      ]
    });

  $("#dogs-table").DataTable({
      dom: "Bfrtip",
      buttons: [{
        extend: "copy",
        className: "btn-sm"
      }, {
        extend: "csv",
        className: "btn-sm"
      }, {
        extend: "pdfHtml5",
        className: "btn-sm"
      }, {
        extend: "print",
        className: "btn-sm"
      },],
      responsive: true,
      order: [
        [0, 'asc']
      ]
    });
});