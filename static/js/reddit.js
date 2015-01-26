$(document).ready(function(){
  /*
  var $post = $('.innerReddit');
  $post.mouseenter(function(){
      $(this).fadeTo('fast', 1);
  });
  $post.mouseleave(function(){
      $(this).fadeTo('fast', 0.7);
  });
  $('.category').mouseenter(function(){
    $(this).fadeTo('fast', 1);
  });
  $('.category').mouseleave(function(){
    $(this).fadeTo('fast', 0.7);
  });
  */

    sorts = ['hot', 'new', 'top', 'controversial'];
    $('.categories a').click(function(){
      var new_sort = $(this).text().trim().toLowerCase();
      if($.inArray(new_sort, sorts) == -1){
        alert('Please pick a real sorting category.');
      }else{
        console.log('Requesting Sort Change: '+new_sort);
        $.ajax({
          type:'POST',
          url:'/reddit',
          data:{category:new_sort},
          success:function(){location.reload(true)},
          failure:function(){alert('Please pick a real sorting category')}
        })
      }
    });
});
