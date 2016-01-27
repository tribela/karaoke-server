function handlerQuery(event) {
  var target = $(event.target).closest('form');
  var vendor = target.children('[name=vendor]').val();
  var queryType = target.children('[name=type]').val();
  var val = target.children('[name=query]').val();
  var serialized = target.serialize();

  $.ajax({
    method: target.attr('method'),
    url: target.attr('action'),
    data: serialized,
  }).success(function(data) {
    var songs = data.songs;
    history.pushState(songs, document.title, '?' + serialized);
    printTable(songs);
    try {
      ga('set', 'location', window.location.href);
      ga('send', 'pageview');
    } catch(e) {
      console.debug('Failed to send info to google analytics');
    }
  });
  event.preventDefault();
}

function printTable(songs) {
    var target = $('#result table');

    target.find('tr:not(.header)').remove();
    for (var i=0; i<songs.length; i++) {
      var row = $(['<tr>',
        '<td class="mdl-data-table__cell--non-numeric">' + songs[i].vendor +'</td>',
        '<td>' + songs[i].number +'</td>',
        '<td class="mdl-data-table__cell--non-numeric">' + songs[i].title +'</td>',
        '<td class="mdl-data-table__cell--non-numeric">' + songs[i].singer +'</td>',
        '</tr>'].join(''));
      target.append(row);
    }
}

function clearTable() {
  var target = $('#result table');

  target.find('tr:not(.header)').remove();
}

function handlerTableFold() {
   $(this).siblings('tr:not(.table-divider)').toggle();
}

function handlerPopState(event) {
  var songs = event.originalEvent.state;
  if (songs !== null) {
    printTable(songs);
  } else {
    clearTable();
  }
}

function initPjax() {
  var serialized = location.search.substring(1);
  var target = $('form');

  if (serialized === "") {
    return;
  }

  $.ajax({
    method: target.attr('method'),
    url: target.attr('action'),
    data: serialized,
  }).success(function(data) {
    var songs = data.songs;
    history.replaceState(songs, document.title);
    printTable(songs);
  });
}

$(function() {
  $('form').submit(handlerQuery);
  $(window).on('popstate', handlerPopState);
  $(document.body).on('click', 'tr.table-divider', handlerTableFold);
  initPjax();
});
