$(document).ready(function(){
    var $post = $('.innerReddit');
    $post.mouseenter(function(){
        $(this).fadeTo('fast', 1);
    });
    $post.mouseleave(function(){
        $(this).fadeTo('fast', 0.6);
    });
    
    sorts = ['hot', 'new', 'top', 'controversial'];
    $('.categories a').click(function(){
      var new_sort = $(this).text().toLowerCase();
      if($.inArray(new_sort, sorts) == -1){
        alert('Please pick a real sorting category.');
      }else{
        $.ajax({
          type:'POST',
          url:'/reddit',
          data:{category:new_sort}
        })
      location.reload(true);
      }
    });
});
