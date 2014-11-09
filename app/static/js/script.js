availability = function() {
  var availability = [];
  $('.available_time').each(
    function() {
      var month = $(this).find('.month').val();
      var day = $(this).find('.day').val();
      var year = $(this).find('.year').val();
      var start_hour = parseInt($(this).find('.start_hour').val());
      var start_ampm = $(this).find('.start_ampm').val();
      var end_hour = parseInt($(this).find('.end_hour').val());
      var end_ampm = $(this).find('.end_ampm').val();
      available_time = {};
      if (start_ampm == 'pm') {
        start_hour += 12;
      }
      if (end_ampm == 'pm') {
        end_hour += 12;
      }
      if (parseInt(day) < 10) {
        day = "0" + day;
      }
      available_time['date'] = month + '-' + day + '-' + year;
      available_time['start_time'] = start_hour + ':00:00';
      available_time['end_time'] = end_hour + ':00:00';
      availability.push(available_time);
      console.log(month);
    }
  );
  return JSON.stringify(availability);
}
add_available_time = function() {
  $('.available_time:last-child').clone().appendTo('.availability');
  console.log("hey");
}
submit_preferences = function(e) {
  // e.preventDefault();
  var availability_string = availability();
  $('#availability').val(availability_string);
  console.log('bleh');
  $('#event_preference').submit();
  console.log('hi');
}

$(
  function() {
    $('#add_available_time').on('click', add_available_time);
    $('#event_preference input[type=button]').on('click', submit_preferences);
  }
);