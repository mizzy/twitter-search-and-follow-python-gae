var divs = document.getElementsByName('users');

function selectAll() {
    for ( var i = 0; i < divs.length; i++ ) {
        $('#' + divs[i].id + ' > input').attr({ checked: 1 });
    }
}

function deselectAll() {
    for ( var i = 0; i < divs.length; i++ ) {
        $('#' + divs[i].id + ' > input').attr({ checked: 0 });
    }
}

var following = 0;
var count = 0;
function bulkFollow() {
    var divs = document.getElementsByName('users');
    $('#status_top').css({ 'font-weight': 'normal', 'color': '#000000' });
    $('#status_bottom').css({ 'font-weight': 'normal', 'color': '#000000' });
    var status = '<img src="/img/loading.gif" />フォロー中';
    $('#status_bottom').html(status);
    $('#status_top').html(status);
    for ( var i = 0; i < divs.length; i++ ) {
        var checkbox = $('#' + divs[i].id + ' > input');
        if ( checkbox.attr('checked') ) {
            following++;
            screen_name = checkbox.attr('value');
            $.getJSON(
                      '/follow',
                      {
                          'screen_name': screen_name,
                              'id':          divs[i].id,
                              },
                      processResult
                      );
        }
    }
}

function processResult(res) {
    following--;
    var result;
    var color;

    if ( res.code == 200 ) {
        result = 'フォローしました';
        color  = 'ffcc00';
    }
    else if( res.code == 403 ) {
        result = 'フォローしてました';
        color  = 'ddeeff';
    }
    else {
        result = 'エラー:' + res.code;
        color  = 'ff6699';
    }

    $('#span_' + res.id).html(result);
    $('#span_' + res.id).css({
            'padding': '0.5em',
            'margin': '0.2em',
    });
    colorFade('span_' + res.id, 'background', 'ffffff', color, 25, 30);

    if ( !following ) {
        var status = 'フォロー完了';
        $('#status_top').css({ 'font-weight': 'bold', 'color': '#ff6600' });
        $('#status_bottom').css({ 'font-weight': 'bold', 'color': '#ff6600' });

        $('#status_top').html(status);
        $('#status_bottom').html(status);

        colorFade('status_top', 'background', 'ffff66', 'c0deed', 25, 30);
        colorFade('status_bottom', 'background', 'ffff66', 'c0deed', 25, 30);
    }
}

var img = new Image();
img.src = '/img/loading.gif';

function check_input(input_id) {
    var input = $('#input_' + input_id);
    if ( input.attr('checked') ) {
        input.attr({ checked: 0});
    }
    else {
        input.attr({ checked: 1});
    }
}
