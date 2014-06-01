function getWeather(query, lat, lon){
  //Load weather forecast data
  if(query === undefined) query = defaultLocation;
  lat = lat || null;
  lon = lon || null;

  console.log('query: '+query+'; latitude: '+lat+'; longitude: '+lon);
  if((lat != null) && (lon != null)) // Both latitude and longitude are supplied
    var cityData = {'latitude':lat, 'longitude':lon};
  else // Ambiguous search query
    var cityData = {'location':query};

  $.ajax({
    async: false,
    url: '/get_weather',
    data: cityData,
    dataType: 'json',
    beforeSend:function(){
      $('#ajax').html('<div><img src="/static/img/ajax-loader.gif" alt="Loading..."/></div>');
    },
    error: function(data){
      $('#city').text('No cities found.');
    },
    success: function(data){
      var conditions = data.conditions,
          suggs = data.suggestions,
          oembed = data.oembed;

      $('#ajax').empty();
      $('#main *').hide('slow');
      $('body').replaceWith($origDOM.clone(true));
      if (conditions === null){
        $('#city').text('No cities found.');
      }else{
        if(suggs.length > 0){
          if(suggs[0].adminArea5)
            $('#city').text(suggs[0].adminArea5 + ', ' + suggs[0].adminArea3 + ', ' + suggs[0].adminArea1);
          else
            $('#city').text(conditions.name + ', ' + conditions.sys.country);
        }else{
          $('#city').text(conditions.name + ', ' + conditions.sys.country);
        } // maybe there's a better way to do the above?
        $('#current_temp').html(Math.round(conditions.main.temp)+'&deg;');
        var highlow = '<span class="low">'+Math.round(conditions.main.temp_min)+'</span><span>/</span><span class="high">'+Math.round(conditions.main.temp_max)+'</span>';
        $('.highlow').html(highlow);
        var w_cond = conditions.weather.main;
        $('.conditions').text(w_cond);
        if(suggs.length > 0){
          for (var city in suggs.splice(0,1)){
            if (suggs.hasOwnProperty(city)){
              var c = suggs[city];
                  sugg_lat = c.latLng.lat,
                  sugg_lng = c.latLng.lng;

              var cityName = c.adminArea5;
              if(c.adminArea3)
                cityName += ', ' + c.adminArea3;
              if(c.adminArea1)
                cityName += ', ' + c.adminArea1;
              
              $('#suggestions > ul').append("<li class='suggestion' data-lat='"+(sugg_lat)+"' data-lng='"+(sugg_lng)+"'><a href='#'>"+cityName+"</a></li>");
            }
          }
        }
        $('#oembed').html(oembed);

        $('#main *').show('slow');
        $('#suggestions ul').hide();
      }
    }
  });
}
var comma = /,.*,/i;

//User clicks on slider menu
$('.slider').click(function(){
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

//User clicks on suggestion
$('#suggestions > ul').on('click', 'li', function(event){
  console.log('Suggestion click');
  var latitude = $(this).attr('data-lat'),
      longitude = $(this).attr('data-lng');
  getWeather(null, latitude, longitude);
});

//New location is typed in
$('#newLocation').submit(function(){
  var textbox = $('input').attr('name','location');
  console.log('Location change: '+textbox.val());
  if (textbox.val().length != 0)
    getWeather(textbox.val());
  textbox.val('');
  return false;
});
var $origDOM = $('body').clone(true);

$(document).ready(function(){
  getWeather();
});
