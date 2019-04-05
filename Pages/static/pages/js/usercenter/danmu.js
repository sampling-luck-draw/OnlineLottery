$(document).ready(function() {
  $('#danmu-table').DataTable( {
    ajax: {
      url: "/get-danmu/4",
      dataSrc: ''
    },
    columns: [
        { data: 'nickName' },
        { data: 'text' },
        { data: 'time' },
    ]
} );
});