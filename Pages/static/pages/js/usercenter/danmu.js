//
// Pipelining function for DataTables. To be used to the `ajax` option of DataTables
//
$.fn.dataTable.pipeline = function (opts) {
  // Configuration options
  var conf = $.extend({
    pages: 5,     // number of pages to cache
    url: '',      // script url
    data: null,   // function or object with parameters to send to the server
                  // matching how `ajax.data` works in DataTables
    method: 'GET' // Ajax HTTP method
  }, opts);

  // Private variables for storing the cache
  var cacheLower = -1;
  var cacheUpper = null;
  var cacheLastRequest = null;
  var cacheLastJson = null;

  return function (request, drawCallback, settings) {
    var ajax = false;
    var requestStart = request.start;
    var drawStart = request.start;
    var requestLength = request.length;
    var requestEnd = requestStart + requestLength;

    if (settings.clearCache) {
      // API requested that the cache be cleared
      ajax = true;
      settings.clearCache = false;
    } else if (cacheLower < 0 || requestStart < cacheLower || requestEnd > cacheUpper) {
      // outside cached data - need to make a request
      ajax = true;
    } else if (JSON.stringify(request.order) !== JSON.stringify(cacheLastRequest.order) ||
      JSON.stringify(request.columns) !== JSON.stringify(cacheLastRequest.columns) ||
      JSON.stringify(request.search) !== JSON.stringify(cacheLastRequest.search)
    ) {
      // properties changed (ordering, columns, searching)
      ajax = true;
    }

    // Store the request for checking next time around
    cacheLastRequest = $.extend(true, {}, request);

    if (ajax) {
      // Need data from the server
      if (requestStart < cacheLower) {
        requestStart = requestStart - (requestLength * (conf.pages - 1));

        if (requestStart < 0) {
          requestStart = 0;
        }
      }

      cacheLower = requestStart;
      cacheUpper = requestStart + (requestLength * conf.pages);

      request.start = requestStart;
      request.length = requestLength * conf.pages;

      // Provide the same `data` options as DataTables.
      if (typeof conf.data === 'function') {
        // As a function it is executed with the data object as an arg
        // for manipulation. If an object is returned, it is used as the
        // data object to submit
        var d = conf.data(request);
        if (d) {
          $.extend(request, d);
        }
      } else if ($.isPlainObject(conf.data)) {
        // As an object, the data given extends the default
        $.extend(request, conf.data);
      }

      settings.jqXHR = $.ajax({
        "type": conf.method,
        "url": conf.url,
        "data": request,
        "dataType": "json",
        "cache": false,
        "success": function (json) {
          cacheLastJson = $.extend(true, {}, json);

          if (cacheLower !== drawStart) {
            json.data.splice(0, drawStart - cacheLower);
          }
          if (requestLength >= -1) {
            json.data.splice(requestLength, json.data.length);
          }

          drawCallback(json);
        }
      });
    } else {
      json = $.extend(true, {}, cacheLastJson);
      json.draw = request.draw; // Update the echo for each response
      json.data.splice(0, requestStart - cacheLower);
      json.data.splice(requestLength, json.data.length);

      drawCallback(json);
    }
  }
};

// Register an API method that will empty the pipelined data, forcing an Ajax
// fetch on the next draw (i.e. `table.clearPipeline().draw()`)
$.fn.dataTable.Api.register('clearPipeline()', function () {
  return this.iterator('table', function (settings) {
    settings.clearCache = true;
  });
});

let X = [];
let Y = [];

function process_danmu_data() {
  let last_date = "";
  for (let k in danmu_time_range) {
    let split_date = k.split(' ');
    let x_value;
    if (split_date[0] === last_date) {
      x_value = split_date[1] + '0';
    } else {
      x_value = split_date[1] + '0\n' + split_date[0];
      last_date = split_date[0];
    }
    X.push(x_value);
    Y.push(danmu_time_range[k]);
  }
}


//
// DataTables initialisation
//
$(document).ready(function () {
  process_danmu_data();
  let chart = echarts.init(document.getElementById('danmu_hot_graph'));
  chart.setOption({
    xAxis: {
      type: 'category',
      data: X,

    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: Y,
      type: 'line',
      smooth: true
    }],
    tooltip: {
      trigger: 'item',
      formatter: "{b} <br/> {c}条弹幕"
    },
  });


  $('#danmu-table').DataTable({
    "processing": true,
    "serverSide": true,
    "ajax": $.fn.dataTable.pipeline({
      url: '/get-danmu?a=4',
      pages: 5 // number of pages to cache
    }),
    columns: [
      {data: 'nickName'},
      {data: 'text'},
      {data: 'time'},
    ],
    columnDefs: [
      {
        orderable: false,
        searchable: false,
        targets: [0, 1, 2]
      },
      {"width": "20%", "targets": 1}
    ],
    "autoWidth": false,
    fixedColumns: true
  });
});