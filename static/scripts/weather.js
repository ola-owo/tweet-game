$(document).ready(function(){
    var getWeather = function(query){
        $.ajax({
            url: '/get_weather',
            data: {'location':query},
            dataType: 'json',
            success: function(data){
                var suggs = data.suggestions;
                var conditions = data.conditions;

                $('#oembed').html(conditions.html);
                $('#city').append(conditions.city);
                $('#temp').prepend(conditions.temp)
                    $('#high').append(conditions.temp_high);
                    $('#low').append(conditions.temp_low);
                for (var city in suggs){
                    if (suggs.hasOwnProperty(city)){
                        $('#suggestions > ul').append("<a href='#'><li class='suggestion' name='"+city+"'>"+suggs[city]+"</li></a>");
                    }
                }
            }
        });
    };
    getWeather('15239');
    $('.closed').click(function(){
        $(this).next().slideDown(200);
        $(this).addClass('open');
        $(this).removeClass('closed');
    });
    $('.open').click(function(){
        $(this).next().slideDown(200);
        $(this).addClass('closed');
        $(this).removeClass('open');
    });
    $('.suggestion').click(function(){
        getWeather($(this).attr('name'));
    });
});
