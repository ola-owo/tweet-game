function getWeather(query=defaultLocation, city=null){
  console.log('query: '+query+'; city: '+city);
  if(city != null){
    var cityData = {'cityCode':city};
  }else{
    var cityData = {'location':query};
  }
  $.ajax({
    url: '/get_weather',
    data: cityData,
    dataType: 'json',
    beforeSend:function(){
      $('#ajax').html('<div><img src="/static/icons/ajax-loader.gif" alt="Loading..."/></div>');
    },
    success: function(data){
      var suggs = data.suggestions;
      var conditions = data.conditions;

      $('#ajax').empty();
      $('#main *').hide('slow');
      $('body').replaceWith($origDOM.clone(true));
      if (conditions === null){
        $('#city').text('No cities found.')
      }else{
        $('#city').text(conditions.city);
        $('#current_temp').html(conditions.temp);
        var highlow = '<span class="low">'+conditions.temp_low+'</span>-<span class="high">'+conditions.temp_high+'</span>';
        $('.highlow').html(highlow);
        var w_cond = conditions['condition'];
        $('.conditions').text(w_cond);
        if (suggs != null){
          for (var city in suggs){
            if (suggs.hasOwnProperty(city)){
              var c = suggs[city]
              if(c[2] === '--'){
                var cityName = c[1]+', '+c[4];
                var locationType = 'cityCode';
              }else{
                var cityName = c[1]+', '+c[2]+', '+c[4];
                var locationType = 'location';
              }
              $('#suggestions > ul').append("<li class='suggestion "+locationType+"' name='"+c[0]+"'><a href='#'>"+cityName+"</a></li>");
            }
          }
        }
        var oembed = conditions['html'];
        $('#oembed').html(oembed);

        $('#main *').show('slow');
        $('#suggestions ul').hide();
      }
    }
  });
}
var comma = /,.*,/i;

$('a.slider').click(function(){
  var $prev = $(this).parent().closest('div');
  if($prev.attr('class') === 'closed'){
    $(this).next().slideDown(1000);
    $prev.addClass('open');
    $prev.removeClass('closed');
  }else if( $('#suggestions').attr('class') === 'open' ){
    $(this).next().slideUp(1000);
    $prev.addClass('closed');
    $prev.removeClass('open');
  }
});

$('#suggestions > ul').on('click', 'li', function(event){
  console.log('Suggestion click');
  var cityCode = $(this).attr('name');
  getWeather(query=null, city=cityCode);
});

$('#newLocation').submit(function(){
  var textbox = $('input').attr('name','location');
  if( comma.test(textbox.val()) ){
    alert('You have too many commas. Check the input guidelines and try again.');
  }else{
    console.log('Location change: '+textbox.val());
    if (textbox.val().length != 0){
      getWeather(textbox.val());
    }
    textbox.val("");
  }
  return false;
});
var $origDOM = $('body').clone(true);

$(document).ready(function(){
  getWeather();

});
