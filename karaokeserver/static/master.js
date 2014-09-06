function handlerQuery(event) {
  var target = $(event.target).closest('form');
  var vendor = target.children('[name=vendor]').val();
  var queryType = target.children('[name=type]').val();
  var val = target.children('[name=query]').val();
  var data = target.serialize();

  $.ajax({
    method: target.attr('method'),
    url: target.attr('action'),
    data: data,
  }).success(function(data) {
    var songs = data.songs;
    var target = $('#result');
    var table = $('<table></table>');
    var header = $(['<tr>',
      '<th>Vendor</th>',
      '<th>Number</th>',
      '<th>Title</th>',
      '<th>Singer</th>',
      '</tr>'].join(''));

    target.html(null);
    table.append(header);
    for (var i=0; i<songs.length; i++) {
      var row = $(['<tr>',
        '<td>' + songs[i].vendor +'</td>',
        '<td>' + songs[i].number +'</td>',
        '<td>' + songs[i].title +'</td>',
        '<td>' + songs[i].singer +'</td>',
        '</tr>'].join(''));
      table.append(row);
    }
    target.append(table);

  });
  event.preventDefault();
}
$(function() {
  $('form').submit(handlerQuery);
});
