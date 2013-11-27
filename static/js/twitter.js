$(document).ready(function(){
  // Pictures lighten when hovered over
  $('.choice')
  .on('mouseenter', function(){
    $(this).fadeTo('fast', 0.6);
  })
  .on('mouseleave', function(){
    $(this).fadeTo('fast', 1);
  })

  /* Not working for some reason
  // Fade in quote and pictures
  $('blockquote').fadeTo('fast', 1, function(){        
    $('.user').each(function(){
      $(this).animate({
        height: '200px',
        width: '200px'
      },500);
    });
  });
  */

  // Handle category change

  $('.category').click(function(){
    var $clicked = $(this);
    $.ajax({
      url: '/guess_tweet',
      type: 'POST',
      data: {category:$clicked.attr('name')},
      dataType: 'text',
      success: function(){
        $('#activeCategory').removeAttr('id');
        $clicked.attr('id', 'activeCategory');
        document.location.reload(true);
      }
    });
  });

  //Menu slideout
  $('img.arrow').click(function(){
    if($(this).parent().attr('id') === 'open'){
      $(this).parent().attr('id', 'closed');
    }else{
      $(this).parent().attr('id', 'open')
    }
    $(this).text($(this).attr('id'));
  });

  // Handle choice making
  var alreadyChose = false;
  $('.choice').click(function(){
    if(alreadyChose === false){
      var guess = $(this).attr('id');
      var phrase = $('blockquote').text();
      var answer;
      var $result = $('#outerResult');
      var $innerResult = $('#innerResult');
      $.ajax({
        url: '/guess_tweet',
        data: {name:guess, tweet:phrase},
        dataType: 'text',
        success: function(ans){
          if(ans === guess){
            $result.css({
              'background-color': '#009933',
              'border-top': '2px solid #006600',
            });
            $innerResult.append('<p>Correct! the answer was @'+ans+'.</p>');
          }else{
            $result.css({
              'background-color': '#CC0000',
              'border-top': '2px solid #800000',
            });
            $innerResult.append('<p>Wrong! the answer was @'+ans+'.</p>');
          }
          $result.slideDown(1000);
          alreadyChose = true;
        },
        failure: function(){
          $result.css({
            'background-color':'#FFBF00',
            'border-top':'#664400',
          });
          $innerResult.append('<p>Whoops! Something went wrong with the server.</p>')
        }
      });
    }else{alert('You already made your choice!')}
  });
});
