//check all click event
$('#chk_all').click(function () 
{
  if ($('#chk_all').is(':checked') == true) 
  {
    $(".chk").prop('checked', true);
    $("#action_btn").show()
    $("#pre_place_order").show()
  }
  else
  {
    $(".chk").prop('checked', false);
    $("#action_btn").hide()
    $("#pre_place_order").hide()
  }
});

//single check click event
$('.chk').click(function() 
{
  if($('.chk:checked').length == $('.chk').length)
  {
    $('#chk_all').prop('checked', true);
    $("#action_btn").show()
    $("#pre_place_order").show()
  }
  else if($('.chk:checked').length == 0)
  {
    $("#action_btn").hide()
    $("#pre_place_order").hide()
  } 
  else 
  {
    $('#chk_all').prop('checked', false);
    $("#action_btn").show()
    $("#pre_place_order").show()
  }
});
function ActionForm(val)
{
  var r=confirm("Are you sure you want to delete selected items?");
  if (r==true)
  {
    $("#action_on").val(val)
    $("#form_list").submit()
  }
}

function ActionPlaceOrder(val)
{
  var r=confirm("Are you sure you want to placed selected orders?");
  if (r==true)
  {
    $("#action_on").val(val)
    $("#form_list").submit()
  }
}

function ItemFormSeach(status)
{
  $("#search_action").val(status)
  $("#filter_item_form").submit()
}

$('#import-btn').click(function() 
{
    var r=confirm("Are you sure you want to import?");
    if (r==true)
    {
      $('.loading').show()
      $("#import-btn").attr("disabled", true);
      $('#import-form').submit()
    }

});

$('#id_category').on('change', function() {

    if(this.value > 0)
    {
      $.ajax({
      url: "/subcategories/"+this.value,
      success:
      function(res)
      {
          $('#id_subcategory').html(res)
      },
      })
    }
    else
    {
      $('#id_subcategory').html('<option value="">-- Select Sub Category --</option>')
    }
});

//calculate mon order
function calculateMonOrder(value,id,event) 
{
  var mon_order_id        = id
  var mon_order_split     = mon_order_id.split('_');
  var mon_id              = mon_order_split[4];
  var mon_moq             = $('#mon_moq_'+mon_id).val();
  var mon_order_quantity  = $('#mon_order_quantity_'+mon_id).val();
  var mon_on_hand_quanty  = $('#mon_on_hand_quanty_'+mon_id).val();
  var mon_order_def       = 0;
  //add only if the value is number
  if(!isNaN(value) && value.length!=0 && value >= 0) 
  {
    if(value.length <= 4)
    {
        mon_order_def = parseInt(mon_order_quantity) - parseInt(mon_on_hand_quanty)
        if(mon_order_def <= 0)
        {
          $('#mon_moq_error_'+mon_id).text('Required quantity is already in stock');
          $('#mon_on_hand_quanty_'+mon_id).removeClass('is-invalid')
          $('#mon_order_valid_'+mon_id).val('yes');
          mon_order_def = 0
        }
        else
        {
            if(mon_order_def < mon_moq)
            {
              $('#mon_moq_error_'+mon_id).text('MOQ is '+mon_moq);
              mon_order_def = mon_moq
            }
            else
            {
              $('#mon_moq_error_'+mon_id).text('');
              $('#mon_on_hand_quanty_'+mon_id).removeClass('is-invalid') 
            }
            $('#mon_order_valid_'+mon_id).val('yes');
        }
    }
    else
    {
      $('#mon_order_valid_'+mon_id).val('no');
      $('#mon_on_hand_quanty_'+mon_id).val('')
      $('#mon_moq_error_'+mon_id).text('The value is too large');
      $('#mon_on_hand_quanty_'+mon_id).addClass('is-invalid')
    }

  }
  else
  {
    $('#mon_order_valid_'+mon_id).val('no');
    if(value.length==0)
    {
      $('#mon_on_hand_quanty_'+mon_id).removeClass('is-invalid')
    }
    else
    {
      $('#mon_on_hand_quanty_'+mon_id).addClass('is-invalid')
    }
  }
  $('#mon_order_txt_'+mon_id).text(mon_order_def);
  $('#mon_order_'+mon_id).val(mon_order_def);
}

$(".mon_class").each(function() {
  $(this).keyup(function(e){
    calculateMonOrder(this.value,$(this).attr("id"));
  });
});

//calculate fri order
function calculateFriOrder(value,id) 
{
  var fri_order_id        = id
  var fri_order_split     = fri_order_id.split('_');
  var fri_id              = fri_order_split[4];
  var fri_moq             = $('#fri_moq_'+fri_id).val();
  var fri_order_quantity  = $('#fri_order_quantity_'+fri_id).val();
  var fri_on_hand_quanty  = $('#fri_on_hand_quanty_'+fri_id).val();
  var fri_order_def       = 0;
  //add only if the value is number
  if(!isNaN(value) && value.length!=0 && value >= 0) 
  {
    if(value.length <= 4)
    {
      fri_order_def = parseInt(fri_order_quantity) - parseInt(fri_on_hand_quanty)
      if(fri_order_def <= 0)
      {
        $('#fri_moq_error_'+fri_id).text('Required quantity is already in stock');
        $('#fri_on_hand_quanty_'+fri_id).removeClass('is-invalid')
        $('#fri_order_valid_'+fri_id).val('yes');
        fri_order_def = 0
      }
      else
      {
        if(fri_order_def < fri_moq)
        {
          $('#fri_moq_error_'+fri_id).text('MOQ is '+fri_moq);
          fri_order_def = fri_moq
        }
        else
        {
          $('#fri_moq_error_'+fri_id).text('');
          $('#fri_on_hand_quanty_'+fri_id).removeClass('is-invalid') 
        }
        $('#fri_order_valid_'+fri_id).val('yes');
      }
    }
    else
    {
      $('#fri_order_valid_'+fri_id).val('no');
      $('#fri_on_hand_quanty_'+fri_id).val('')
      $('#fri_moq_error_'+fri_id).text('The value is too large');
      $('#fri_on_hand_quanty_'+fri_id).addClass('is-invalid')
    }
  }
  else
  {
    $('#fri_order_valid_'+fri_id).val('no');
    if(value.length==0)
    {
      $('#fri_on_hand_quanty_'+fri_id).removeClass('is-invalid')
    }
    else
    {
      $('#fri_on_hand_quanty_'+fri_id).addClass('is-invalid')
    }
  }
  $('#fri_order_txt_'+fri_id).text(fri_order_def);
  $('#fri_order_'+fri_id).val(fri_order_def);
}

$(".fri_class").each(function() {
  $(this).keyup(function(e){
    calculateFriOrder(this.value,$(this).attr("id"));
  });
});


$('#pre_place_order').click(function() 
{
  var validation = true;
  var activate_day = $('#activate_day').val()
  $('.chk').each( function() 
  {
    var order_id = $(this).attr("id").split('_');
    if(activate_day == 'mon')
    {
      if($('#mon_on_hand_quanty_'+order_id[1]).val() == '')
      {
        $('#mon_moq_error_'+order_id[1]).text('Please enter value.');
        validation = false
      }
      else if($('#mon_order_valid_'+order_id[1]).val() == 'no')
      {
        $('#mon_moq_error_'+order_id[1]).text('Invalid value.');
        validation = false
      }
    }
    else
    {
      if($('#fri_on_hand_quanty_'+order_id[1]).val() == '')
      {
        $('#fri_moq_error_'+order_id[1]).text('Please enter value.');
        validation = false
      }
      else if($('#fri_order_valid_'+order_id[1]).val() == 'no')
      {
        $('#fri_moq_error_'+order_id[1]).text('Invalid value.');
        validation = false
      }
    }
  });

  if(validation)
  {
    $('#pre_place_order_form').submit()
  }

});

function placeOrder()
{
  var r=confirm("Are you sure you want to place this order?");
  if (r==true)
  {
    $('#place-order-form').submit()
  }
}
//event date
$('#id_updatedOn').datepicker({format: 'yyyy-mm-dd',autoclose:true});
$('#id_from_date').datepicker({format: 'yyyy-mm-dd',autoclose:true});
$('#id_to_date').datepicker({format: 'yyyy-mm-dd',autoclose:true});