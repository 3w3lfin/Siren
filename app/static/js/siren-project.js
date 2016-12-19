$(function  () {
  var adjustment;

  var group = $("ol.plan").sortable({
    refreshPositions: true,
    opacity: 0.6,
    scroll: true,
    containment: 'parent',


    group: 'plan',

    // animation on drop
    onDrop: function  ($item, container, _super) {
      var $clonedItem = $('<li/>').css({height: 0});
      $item.before($clonedItem);
      $clonedItem.animate({'height': $item.height()});

      $item.animate($clonedItem.position(), function  () {
        $clonedItem.detach();
        _super($item, container);
      });
      
        var data = group.sortable("serialize").get();
        var jsonString = JSON.stringify(data, null, ' ');
        $.get('/app/show_project/{{ project.id }}', {command: "drop", serialize: jsonString});
    },

    // set $item relative to cursor position
    onDragStart: function ($item, container, _super) {
      var offset = $item.offset(),
          pointer = container.rootGroup.pointer;

      adjustment = {
        left: pointer.left - offset.left,
        top: pointer.top - offset.top
      };

      _super($item, container);
    },
    onDrag: function ($item, position) {
      $item.css({
        left: position.left - adjustment.left,
        top: position.top - adjustment.top
      });
    },
    
    receive: function (event, ui) {
        console.log("Drag fired!");
    }
  });
});

$(document).ready(function () {    
    $(".myBtn").click(function(){
        var project = $(this).attr("data-project");
        $.get('/app/show_project/' + project, {status: this.id}, function(data){
            location.href = data
        });
    });
    
    $(".removeButton").click(function(){
        var id = $(this).attr("data-catid");
        var project = $(this).attr("data-project");
        $.get('/app/show_project/' + project, {command: "remove", com_id: id}, function(){
               $('#div_'+id).hide();
        });
    });
    
    $(".editButton").click(function(){
        var me = $(this);
        $(me.val()+"one").toggle();
        $(me.val()+"two").toggle();
    });
    
    $(".show_button").click(function(){
        var com_id = $(this).attr("data-catid");
        var project = $(this).attr("data-project");
        var y = $(this).attr("id");
        var z = y.substring(y.length - 4);
        
        $.get('/app/show_project/' + project, {command: z, com_id: com_id}, function(update_com){
            var l = document.getElementById(y)
            if (z == "show") {
                l.setAttribute("id", com_id + "_hide");
                l.innerHTML = "Hide";
            } else {

                l.setAttribute("id",  com_id + "_show");
                l.innerHTML = "Show";
            }
        });
    });
    
    $(".removeService").click(function(){
        var id = $(this).attr("data-catid");
        var project = $(this).attr("data-project");
        $.get('/app/show_project/' + project, {command: "remove_service", service_id: id}, function(){
               $('#service_'+id).hide();
        });
    });
    
    $(".removeModule").click(function(){
        var id = $(this).attr("data-catid");
        var project = $(this).attr("data-project");
        $.get('/app/show_project/' + project, {command: "remove_module", module_id: id}, function(){
               $('#show_module_'+id).hide();
        });
    });

    $(".remove").click(function(){
        var project = $(this).attr("data-project");
        var id = $(this).attr("data-catid");
        $.get('/app/show_project/' + project, {command: "remove_share", user_pro_id: id}, function(){
            $('#remove_'+id).hide();
        });
    });
});

