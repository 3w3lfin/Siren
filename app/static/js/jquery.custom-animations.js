$('#menu_open').on('click', function(){
  var $this = $(this);
  if ($this.hasClass('open')) {
    $this.animate({
      left : '360px'
    }, 500).removeClass('open');
  } else {
    $this.animate({
      left : 0
    }, 500).addClass('open');
  }
});
